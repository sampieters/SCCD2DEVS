import sys
import re
from sccd.runtime.event_queue import EventQueue
from pypdevs.infinity import INFINITY
from pypdevs.DEVS import *

from heapq import heappush, heappop, heapify
import threading

ELSE_GUARD = "ELSE_GUARD"

def get_private_port(text):
    match = re.search(r'private_\d+_(\w+)', text)

    if match:
        result = match.group(1)
        return result

class RuntimeException(Exception):
    """
    Base class for runtime exceptions.
    """
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)


class AssociationException(RuntimeException):
    """
    Exception class thrown when an error occurs in a CRUD operation on associations.
    """
    pass


class Association(object):
    """
    Class representing an SCCD association.
    """

    def __init__(self, to_class, min_card, max_card):
        """
        Constructor

       :param to_class: the name of the target class
       :param min_card: the minimal cardinality
       :param max_card: the maximal cardinality
        """
        self.to_class = to_class
        self.min_card = min_card
        self.max_card = max_card
        self.instances = {}  # maps index (as string) to instance
        self.instances_to_ids = {}
        self.size = 0
        self.next_id = 0

    def allowedToAdd(self):
        return self.max_card == -1 or self.size < self.max_card

    def allowedToRemove(self):
        return self.min_card == -1 or self.size > self.min_card

    def addInstance(self, instance):
        if self.allowedToAdd():
            new_id = self.next_id
            self.next_id += 1
            self.instances[new_id] = instance
            self.instances_to_ids[instance] = new_id
            self.size += 1
            return new_id
        else:
            raise AssociationException("Not allowed to add the instance to the association.")

    def removeInstance(self, instance):
        if self.allowedToRemove():
            index = self.instances_to_ids[instance]
            del self.instances[index]
            del self.instances_to_ids[instance]
            #self.size -= 1
            return index
        else:
            raise AssociationException("Not allowed to remove the instance from the association.")

    def getInstance(self, index):
        try:
            return self.instances[index]
        except IndexError:
            raise AssociationException("Invalid index for fetching instance(s) from association.")


class StatechartSemantics:
    # Big Step Maximality
    TakeOne = 0
    TakeMany = 1
    # Concurrency - not implemented yet
    Single = 0
    Many = 1
    # Preemption - not implemented yet
    NonPreemptive = 0
    Preemptive = 1
    # Internal Event Lifeline
    Queue = 0
    NextSmallStep = 1
    NextComboStep = 2
    # Input Event Lifeline
    Whole = 0
    FirstSmallStep = 1
    FirstComboStep = 2
    # Priority
    SourceParent = 0
    SourceChild = 1

    # TODO: add Memory Protocol options

    def __init__(self):
        # default semantics:
        self.big_step_maximality = self.TakeMany
        self.internal_event_lifeline = self.Queue
        self.input_event_lifeline = self.FirstComboStep
        self.priority = self.SourceParent
        self.concurrency = self.Single


class State:
    def __init__(self, state_id, name, obj):
        self.state_id = state_id
        self.name = name
        self.obj = obj

        self.ancestors = []
        self.descendants = []
        self.descendant_bitmap = 0
        self.children = []
        self.parent = None
        self.enter = None
        self.exit = None
        self.default_state = None
        self.transitions = []
        self.history = []
        self.has_eventless_transitions = False

    def getEffectiveTargetStates(self):
        targets = [self]
        if self.default_state:
            targets.extend(self.default_state.getEffectiveTargetStates())
        return targets

    def fixTree(self):
        for c in self.children:
            if isinstance(c, HistoryState):
                self.history.append(c)
            c.parent = self
            c.ancestors.append(self)
            c.ancestors.extend(self.ancestors)
            c.fixTree()
        self.descendants.extend(self.children)
        for c in self.children:
            self.descendants.extend(c.descendants)
        for d in self.descendants:
            self.descendant_bitmap |= 2 ** d.state_id

    def addChild(self, child):
        self.children.append(child)

    def addTransition(self, transition):
        self.transitions.append(transition)

    def setEnter(self, enter):
        self.enter = enter

    def setExit(self, exit):
        self.exit = exit

    def __repr__(self):
        return "State(%s)" % (self.state_id)


class HistoryState(State):
    def __init__(self, state_id, name, obj):
        State.__init__(self, state_id, name, obj)


class ShallowHistoryState(HistoryState):
    def __init__(self, state_id, name, obj):
        HistoryState.__init__(self, state_id, name, obj)

    def getEffectiveTargetStates(self):
        if self.state_id in self.obj.history_values:
            targets = []
            for hv in self.obj.history_values[self.state_id]:
                targets.extend(hv.getEffectiveTargetStates())
            return targets
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates()


class DeepHistoryState(HistoryState):
    def __init__(self, state_id, name, obj):
        HistoryState.__init__(self, state_id, name, obj)

    def getEffectiveTargetStates(self):
        if self.state_id in self.obj.history_values:
            return self.obj.history_values[self.state_id]
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates()


class ParallelState(State):
    def __init__(self, state_id, name, obj):
        State.__init__(self, state_id, name, obj)

    def getEffectiveTargetStates(self):
        targets = [self]
        for c in self.children:
            if not isinstance(c, HistoryState):
                targets.extend(c.getEffectiveTargetStates())
        return targets


class Transition:
    def __init__(self, obj, source, targets):
        self.guard = None
        self.action = None
        self.trigger = None
        self.source = source
        self.targets = targets
        self.obj = obj
        self.enabled_event = None  # the event that enabled this transition
        self.optimize()

    def isEnabled(self, events, enabled_transitions):
        if self.trigger is None:
            self.enabled_event = None
            return (self.guard is None) or (self.guard == ELSE_GUARD and not enabled_transitions) or self.guard([])
        else:
            for event in events:
                if (self.trigger.name == event.name and (
                        not self.trigger.port or self.trigger.port == event.port)) and (
                        (self.guard is None) or (self.guard == ELSE_GUARD and not enabled_transitions) or self.guard(
                        event.parameters)):
                    self.enabled_event = event
                    return True

    # @profile
    def fire(self):
        # exit states...
        exit_set = self.__exitSet()
        for s in exit_set:
            # remember which state(s) we were in if a history state is present
            for h in s.history:
                f = lambda s0: s0.ancestors and s0.parent == s
                if isinstance(h, DeepHistoryState):
                    f = lambda s0: not s0.descendants and s0 in s.descendants
                self.obj.history_values[h.state_id] = list(filter(f, self.obj.configuration))
        for s in exit_set:
            self.obj.eventless_states -= s.has_eventless_transitions
            # execute exit action(s)
            if s.exit:
                s.exit()
            self.obj.configuration_bitmap &= ~2 ** s.state_id

        # combo state changed area
        self.obj.combo_step.changed_bitmap |= 2 ** self.lca.state_id
        self.obj.combo_step.changed_bitmap |= self.lca.descendant_bitmap

        # execute transition action(s)
        if self.action:
            self.action(self.enabled_event.parameters if self.enabled_event else [])

        # enter states...
        targets = self.__getEffectiveTargetStates()
        enter_set = self.__enterSet(targets)
        for s in enter_set:
            self.obj.eventless_states += s.has_eventless_transitions
            self.obj.configuration_bitmap |= 2 ** s.state_id
            # execute enter action(s)
            if s.enter:
                s.enter()

        if self.obj.eventless_states:
            self.obj.controller.eventless.add(self.obj)
        else:
            self.obj.controller.eventless.discard(self.obj)

        try:
            self.obj.configuration = self.obj.config_mem[self.obj.configuration_bitmap]
        except:
            self.obj.configuration = self.obj.config_mem[self.obj.configuration_bitmap] = sorted(
                [s for s in list(self.obj.states.values()) if 2 ** s.state_id & self.obj.configuration_bitmap],
                key=lambda s: s.state_id)
        self.enabled_event = None

    def __getEffectiveTargetStates(self):
        targets = []
        for target in self.targets:
            for e_t in target.getEffectiveTargetStates():
                if not e_t in targets:
                    targets.append(e_t)
        return targets

    def __exitSet(self):
        return [s for s in reversed(self.lca.descendants) if (s in self.obj.configuration)]

    def __enterSet(self, targets):
        target = targets[0]
        for a in reversed(target.ancestors):
            if a in self.source.ancestors:
                continue
            else:
                yield a
        for target in targets:
            yield target

    def setGuard(self, guard):
        self.guard = guard

    def setAction(self, action):
        self.action = action

    def setTrigger(self, trigger):
        self.trigger = trigger
        if self.trigger is None:
            self.source.has_eventless_transitions = True

    def optimize(self):
        # the least-common ancestor can be computed statically
        if self.source in self.targets[0].ancestors:
            self.lca = self.source
        else:
            self.lca = self.source.parent
            target = self.targets[0]
            if self.source.parent != target.parent:  # external
                for a in self.source.ancestors:
                    if a in target.ancestors:
                        self.lca = a
                        break

    def __repr__(self):
        return "Transition(%s, %s)" % (self.source, self.targets[0])


class Event(object):
    def __init__(self, event_name, port="", parameters=[], instance=None):
        self.name = event_name
        self.parameters = parameters
        self.port = port
        self.instance = instance

    # for comparisons in heaps
    def __lt__(self, other):
        s = str(self.name) + str(self.parameters) + str(self.port)
        return len(s)

    def getName(self):
        return self.name

    def getPort(self):
        return self.port

    def getParameters(self):
        return self.parameters

    def __repr__(self):
        representation = "(event name: " + str(self.name) + "; port: " + str(self.port)
        if self.parameters:
            representation += "; parameters: " + str(self.parameters)
        representation += ")"
        return representation


class RuntimeClassBase(object):

    def __init__(self, controller):
        self.events = EventQueue()

        self.active = False

        # Instead of controller, do the class for which the instanced 
        self.controller = controller

        self.__set_stable(True)
        self.inports = {}
        self.outports = {}
        self.timers = {}
        self.states = {}
        self.eventless_states = 0
        self.configuration_bitmap = 0
        self.transition_mem = {}
        self.config_mem = {}


        #self.narrow_cast_port = self.controller.addInputPort("<narrow_cast>", self)

        self.semantics = StatechartSemantics()

    # to break ties in the heap,
    # compare by number of events in the list
    def __lt__(self, other):
        return len(self.events.event_list) < len(other.events.event_list)

    def getChildren(self, link_name):
        pass

    def getSingleChild(self, link_name):
        return self.getChildren(link_name)[0]  # assume this will return a single child...

    def getOutPortName(self, port_name):
        return self.outports[port_name] if port_name in self.outports else port_name

    def getInPortName(self, port_name):
        return self.inports[port_name] if port_name in self.inports else port_name

    def start(self):
        self.configuration = []

        self.active = True

        self.current_state = {}
        self.history_values = {}
        self.timers = {}
        self.timers_to_add = {}

        self.big_step = BigStepState()
        self.combo_step = ComboStepState()
        self.small_step = SmallStepState()

        self.__set_stable(False)

        self.initializeStatechart()
        self.processBigStepOutput()

    def stop(self):
        self.active = False
        self.__set_stable(True)

    def updateConfiguration(self, states):
        self.configuration.extend(states)
        self.configuration_bitmap = sum([2 ** s.state_id for s in states])

    def getSimulatedTime(self):
        # TODO: added to be exactly the same as sccd
        return self.controller.simulated_time * 1000

    def addTimer(self, index, timeout):
        #self.timers_to_add[index] = (self.controller.simulated_time + int(timeout * 1000), Event("_%iafter" % index))
        self.timers_to_add[index] = (self.controller.simulated_time + timeout, Event("_%iafter" % index))

    def removeTimer(self, index):
        if index in self.timers_to_add:
            del self.timers_to_add[index]
        if index in self.timers:
            self.events.remove(self.timers[index])
            del self.timers[index]
        self.earliest_event_time = self.events.getEarliestTime()

    def addEvent(self, event_list, time_offset=0):
        event_time = self.controller.simulated_time + time_offset
        if not (event_time, self) in self.controller.instance_times:
            heappush(self.controller.instance_times, (event_time, self))
        if event_time < self.earliest_event_time:
            self.earliest_event_time = event_time
        if not isinstance(event_list, list):
            event_list = [event_list]
        for e in event_list:
            self.events.add(event_time, e)

    def processBigStepOutput(self):
        for e in self.big_step.output_events_port:
            self.controller.outputEvent(e)
        for e in self.big_step.output_events_om:
            #TODO: is this the same as obbject manager, so cd scope?
            self.controller.addEvent(e)

    def __set_stable(self, is_stable):
        self.is_stable = is_stable
        # self.earliest_event_time keeps track of the earliest time this instance will execute a transition
        if not is_stable:
            self.earliest_event_time = self.controller.simulated_time
        
        elif not self.active:
            self.earliest_event_time = INFINITY
        else:
            self.earliest_event_time = self.events.getEarliestTime()
        if self.earliest_event_time != INFINITY:
            if not (self.earliest_event_time, self) in self.controller.instance_times:
                heappush(self.controller.instance_times, (self.earliest_event_time, self))

    def step(self):
        is_stable = False
        while not is_stable:
            due = []
            if self.events.getEarliestTime() <= self.controller.simulated_time:
                due = [self.events.pop()]
            is_stable = not self.bigStep(due)
            self.processBigStepOutput()
        for index, entry in list(self.timers_to_add.items()):
            self.timers[index] = self.events.add(*entry)
        self.timers_to_add = {}
        self.__set_stable(True)

    def inState(self, state_strings):
        state_ids = [self.states[state_string].state_id for state_string in state_strings]
        for state_id in state_ids:
            for s in self.configuration:
                if s.state_id == state_id:
                    break
            else:
                return False
        return True

    def bigStep(self, input_events):
        self.big_step.next(input_events)
        self.small_step.reset()
        self.combo_step.reset()
        while self.comboStep():
            self.big_step.has_stepped = True
            if self.semantics.big_step_maximality == StatechartSemantics.TakeOne:
                break  # Take One -> only one combo step allowed
        return self.big_step.has_stepped

    def comboStep(self):
        self.combo_step.next()
        while self.smallStep():
            self.combo_step.has_stepped = True
        return self.combo_step.has_stepped

    # generate transition candidates for current small step
    # @profile
    def generateCandidates(self):
        changed_bitmap = self.combo_step.changed_bitmap
        key = (self.configuration_bitmap, changed_bitmap)
        try:
            transitions = self.transition_mem[key]
        except:
            self.transition_mem[key] = transitions = [t for s in self.configuration if
                                                      not (2 ** s.state_id & changed_bitmap) for t in s.transitions]

        enabledEvents = self.getEnabledEvents()
        enabledTransitions = []
        for t in transitions:
            if t.isEnabled(enabledEvents, enabledTransitions):
                enabledTransitions.append(t)
        return enabledTransitions

    # @profile
    def smallStep(self):
        def __younger_than(x, y):
            if x.source in y.source.ancestors:
                return 1
            elif y.source in x.source.ancestors:
                return -1
            else:
                return 0

        if self.small_step.has_stepped:
            self.small_step.next()
        candidates = self.generateCandidates()
        if candidates:
            to_skip = set()
            conflicting = []
            for c1 in candidates:
                if c1 not in to_skip:
                    conflict = [c1]
                    for c2 in candidates[candidates.index(c1):]:
                        if c2.source in c1.source.ancestors or c1.source in c2.source.ancestors:
                            conflict.append(c2)
                            to_skip.add(c2)

                    if sys.version_info[0] < 3:
                        conflicting.append(sorted(conflict, cmp=__younger_than))
                    else:
                        import functools
                        conflicting.append(sorted(conflict, key=functools.cmp_to_key(__younger_than)))

            if self.semantics.concurrency == StatechartSemantics.Single:
                candidate = conflicting[0]
                if self.semantics.priority == StatechartSemantics.SourceParent:
                    candidate[-1].fire()
                else:
                    candidate[0].fire()
            elif self.semantics.concurrency == StatechartSemantics.Many:
                pass  # TODO: implement
            self.small_step.has_stepped = True
        return self.small_step.has_stepped

    # @profile
    def getEnabledEvents(self):
        result = self.small_step.current_events + self.combo_step.current_events
        if self.semantics.input_event_lifeline == StatechartSemantics.Whole or (
                not self.big_step.has_stepped and
                (self.semantics.input_event_lifeline == StatechartSemantics.FirstComboStep or (
                        not self.combo_step.has_stepped and
                        self.semantics.input_event_lifeline == StatechartSemantics.FirstSmallStep))):
            result += self.big_step.input_events
        return result

    def raiseInternalEvent(self, event):
        if self.semantics.internal_event_lifeline == StatechartSemantics.NextSmallStep:
            self.small_step.addNextEvent(event)
        elif self.semantics.internal_event_lifeline == StatechartSemantics.NextComboStep:
            self.combo_step.addNextEvent(event)
        elif self.semantics.internal_event_lifeline == StatechartSemantics.Queue:
            self.addEvent(event)

    def initializeStatechart(self):
        self.updateConfiguration(self.default_targets)
        for state in self.default_targets:
            self.eventless_states += state.has_eventless_transitions
            if state.enter:
                state.enter()
        if self.eventless_states:
            print("")
            pass
            #self.controller.object_manager.eventless.add(self)

class BigStepState(object):
    def __init__(self):
        self.input_events = [] # input events received from environment before beginning of big step (e.g. from object manager, from input port)
        self.output_events_port = [] # output events to be sent to output port after big step ends.
        self.output_events_om = [] # output events to be sent to object manager after big step ends.
        self.has_stepped = True

    def next(self, input_events):
        self.input_events = input_events
        self.output_events_port = []
        self.output_events_om = []
        self.has_stepped = False

    def outputEvent(self, event):
        self.output_events_port.append(event)

    def outputEventOM(self, event):
        self.output_events_om.append(event)


class ComboStepState(object):
    def __init__(self):
        self.current_events = [] # set of enabled events during combo step
        self.next_events = [] # internal events that were raised during combo step
        self.changed_bitmap = 0 # set of all or-states that were the arena of a triggered transition during big step.
        self.has_stepped = True

    def reset(self):
        self.current_events = []
        self.next_events = []

    def next(self):
        self.current_events = self.next_events
        self.next_events = []
        self.changed_bitmap = 0
        self.has_stepped = False

    def addNextEvent(self, event):
        self.next_events.append(event)


class SmallStepState(object):
    def __init__(self):
        self.current_events = [] # set of enabled events during small step
        self.next_events = [] # events to become 'current' in the next small step
        self.candidates = [] # document-ordered(!) list of transitions that can potentially be executed concurrently, or preempt each other, depending on concurrency semantics. If no concurrency is used and there are multiple candidates, the first one is chosen. Source states of candidates are *always* orthogonal to each other.
        self.has_stepped = True

    def reset(self):
        self.current_events = []
        self.next_events = []

    def next(self):
        self.current_events = self.next_events # raised events from previous small step
        self.next_events = []
        self.candidates = []
        self.has_stepped = False

    def addNextEvent(self, event):
        self.next_events.append(event)

    def addCandidate(self, t, p):
        self.candidates.append((t, p))

    def hasCandidates(self):
        return len(self.candidates) > 0

class ObjectManagerBase(AtomicDEVS):    
    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.elapsed = 0
        self.obj_manager_in = self.addInPort("obj_manager_in")
        self.obj_manager_out = self.addOutPort("obj_manager_out")
        self.outputs = {}
        self.next_time = INFINITY
        
        self.port_mappings = {}
        
        self.input_queue = EventQueue()
        self.simulated_time = 0
        self.to_send = []

        self.events = EventQueue()
        self.instances = {}
        self.next_instance = 0
        self.instance_times = []
        self.eventless = set()
        self.regex_pattern = re.compile("^([a-zA-Z_]\w*)(?:\[(\d+)\])?$")
        self.handlers = {"narrow_cast": self.handleNarrowCastEvent,
                         "broad_cast": self.handleBroadCastEvent,
                         "create_instance": self.handleCreateEvent,
                         "associate_instance": self.handleAssociateEvent,
                         "disassociate_instance": self.handleDisassociateEvent,
                         "start_instance": self.handleStartInstanceEvent,
                         "delete_instance": self.handleDeleteInstanceEvent,
                         "create_and_start_instance": self.handleCreateAndStartEvent}
        
        self.output_listeners = []

        self.inports = {}

        self.lock = threading.Condition()
    
    def getEarliestEventTime(self):
        with self.lock:
            while self.instance_times and self.instance_times[0][0] < self.instance_times[0][1].earliest_event_time:
                heappop(self.instance_times)
            return min(INFINITY if not self.instance_times else self.instance_times[0][0], self.events.getEarliestTime())
        
    def addEvent(self, event, time_offset = 0):
        self.events.add(self.simulated_time + time_offset, event)
        
    # broadcast an event to all instances
    def broadcast(self, source, new_event, time_offset = 0):
        for i in self.instances:
            if i != source:
                i.addEvent(new_event, time_offset)
        
    def stepAll(self):
        self.step()
        simulated_time = self.simulated_time
        self.to_step = set()
        if len(self.instance_times) > (4 * len(self.instances)):
            new_instance_times = []
            for it in self.instances:
                if it.earliest_event_time != INFINITY:
                    new_instance_times.append((it.earliest_event_time, it))
            self.instance_times = new_instance_times
            heapify(self.instance_times)
        while self.instance_times and self.instance_times[0][0] <= simulated_time:
            self.to_step.add(heappop(self.instance_times)[1])
        for i in self.to_step | self.eventless:
            if i.active and (i.earliest_event_time <= simulated_time or i.eventless_states):
                i.step()

    def step(self):
        while self.events.getEarliestTime() <= self.simulated_time:
            if self.events:
                self.handleEvent(self.events.pop())
               
    def start(self):
        for i in self.instances:
            i.start()

    def handleInput(self):
        while not self.input_queue.isEmpty():
            event_time = self.input_queue.getEarliestTime()
            e = self.input_queue.pop()
            
            #TODO: tot nu toe zal dit werken maar niet 
            #input_port = self.input_ports[e.getPort()]
            input_port = e.getPort()

            #target_instance = input_port.instance
            #TODO: get the first field, should be dynamically
            #temp = None

            # TODO: instance is now given in parameters
            temp = e.instance
            if temp is None:
                temp = self.processAssociationReference(e.parameters[0])[0]
                temp = temp[1]
            #target_instance = list(self.instances)[temp]
            target_instance = self.instances[temp]
            if target_instance == None:
                self.broadcast(e, event_time - self.simulated_time)
            else:
                target_instance.addEvent(e, event_time - self.simulated_time)

    def addInput(self, input_event_list, time_offset = 0, force_internal=False):
        # force_internal is for narrow_cast events, otherwise these would arrive as external events (on the current wall-clock time)
        if not isinstance(input_event_list, list):
            input_event_list = [input_event_list]

        for e in input_event_list:
            if e.getName() == "":
                raise InputException("Input event can't have an empty name.")
            
            #if e.getPort() not in self.IPorts:
            #    raise InputException("Input port mismatch, no such port: " + e.getPort() + ".")
                
            if force_internal:
                self.input_queue.add((0 if self.simulated_time is None else self.simulated_time) + time_offset, e)
            else:
                # TODO; changed this from self.accurate_time.get_wct() to self.simulated_time
                #self.input_queue.add((0 if self.simulated_time is None else 0) + time_offset, e)
                self.input_queue.add((0 if self.simulated_time is None else 0) + time_offset, e)


    def handleEvent(self, e):
        self.handlers[e.getName()](e.getParameters())

    def outputEvent(self, event):
        self.to_send.append((self.name, None, event))
        #for listener in self.output_listeners:
        #    self.to_send.append((self.name, None, event))
        #   listener.add(event)

    def processAssociationReference(self, input_string):
        if len(input_string) == 0:
            raise AssociationReferenceException("Empty association reference.")
        path_string =  input_string.split("/")
        result = []
        for piece in path_string:
            match = self.regex_pattern.match(piece)
            if match:
                name = match.group(1)
                index = match.group(2)
                if index is None:
                    index = -1
                result.append((name,int(index)))
            else:
                raise AssociationReferenceException("Invalid entry in association reference. Input string: " + input_string)
        return result
    
    def handleStartInstanceEvent(self, parameters):
        if len(parameters) != 2:
            raise ParameterException ("The start instance event needs 2 parameters.")  
        else:
            source = parameters[0]
            source_index = None
            try:
                source_traversal_list = self.processAssociationReference(source.association_name)
                source_index = source_traversal_list[0][1]
            except:
                source_index = 0 
                
            traversal_list = self.processAssociationReference(parameters[1])

            for i in self.getInstances(source, traversal_list):
                ev = Event("start_instance", None, [i['path']], source_index)
                self.to_send.append((self.name, i['to_class'], ev))

        
    def handleBroadCastEvent(self, parameters):
        if len(parameters) != 2:
            raise ParameterException ("The broadcast event needs 2 parameters (source of event and event name).")
        self.broadcast(parameters[0], parameters[1])

    def handleCreateEvent(self, parameters):
        if len(parameters) < 2:
            raise ParameterException ("The create event needs at least 2 parameters.")

        source = parameters[0]
        source_index = None
        try:
            source_index = self.processAssociationReference(source.association_name)
            source_index = source_index[0][1]
        except:
            # TODO: I think the else is only for mainapp becuase it would not have an assocation name
            source_index = 0

        association_name = parameters[1]

        traversal_list = self.processAssociationReference(association_name)
        instances = self.getInstances(source, traversal_list)
        
        association = source.associations[association_name]
        if association.allowedToAdd():
            ''' allow subclasses to be instantiated '''
            class_name = association.to_class if len(parameters) == 2 else parameters[2]
            self.to_send.append((self.name, class_name, Event('create_instance', None, parameters[1:], source_index)))

        #else:
        #    source.addEvent(Event("instance_creation_error", None, [association_name]))
        #    return []

    def handleCreateAndStartEvent(self, parameters):
        params = self.handleCreateEvent(parameters)
        if params:
            self.handleStartInstanceEvent(params)

    def handleDeleteInstanceEvent(self, parameters):
        if len(parameters) < 2:
            raise ParameterException ("The delete event needs at least 2 parameters.")
        else:
            source = parameters[0]
            association_name = parameters[1]
            
            traversal_list = self.processAssociationReference(association_name)
            
            instances = self.getInstances(source, traversal_list)
            association = source.associations[traversal_list[0][0]]
            index = None
            try:
                index = self.processAssociationReference(source.association_name)
                index = index[0][1]
                params = list(association.instances.values())
            except:
                # TODO: This is only for the default, don't know if it will work always --> beter check source with instances 
                index = self.processAssociationReference(association_name)
                params = [index[0][1]]
                index = 0
            self.to_send.append((self.name, association.to_class, Event("delete_instance", None, [parameters[1], params], index)))
                
    def handleAssociateEvent(self, parameters):
        if len(parameters) != 3:
            raise ParameterException ("The associate_instance event needs 3 parameters.")
        else:
            source = parameters[0]
            to_copy_list = self.getInstances(source, self.processAssociationReference(parameters[1]))
            if len(to_copy_list) != 1:
                raise AssociationReferenceException ("Invalid source association reference.")
            wrapped_to_copy_instance = to_copy_list[0]["instance"]
            dest_list = self.processAssociationReference(parameters[2])
            if len(dest_list) == 0:
                raise AssociationReferenceException ("Invalid destination association reference.")
            last = dest_list.pop()
            if last[1] != -1:
                raise AssociationReferenceException ("Last association name in association reference should not be accompanied by an index.")
                
            added_links = []
            for i in self.getInstances(source, dest_list):
                association = i["instance"].associations[last[0]]
                if association.allowedToAdd():
                    index = association.addInstance(wrapped_to_copy_instance)
                    added_links.append(i["path"] + ("" if i["path"] == "" else "/") + last[0] + "[" + str(index) + "]")
                
            source.addEvent(Event("instance_associated", parameters = [added_links]))
                
    def handleDisassociateEvent(self, parameters):
        if len(parameters) < 2:
            raise ParameterException ("The disassociate_instance event needs at least 2 parameters.")
        else:
            source = parameters[0]
            association_name = parameters[1]
            if not isinstance(association_name, list):
                association_name = [association_name]
            deleted_links = []
            
            for a_n in association_name:
                traversal_list = self.processAssociationReference(a_n)
                instances = self.getInstances(source, traversal_list)
                
                for i in instances:
                    try:
                        index = i['ref'].associations[i['assoc_name']].removeInstance(i["instance"])
                        deleted_links.append(a_n +  "[" + str(index) + "]")
                    except AssociationException as exception:
                        raise RuntimeException("Error disassociating '" + a_n + "': " + str(exception))
                
            source.addEvent(Event("instance_disassociated", parameters = [deleted_links]))
        
    def handleNarrowCastEvent(self, parameters):
        if len(parameters) != 3:
            raise ParameterException ("The narrow_cast event needs 3 parameters.")
        source = parameters[0]
        
        if not isinstance(parameters[1], list):
            targets = [parameters[1]]
        else:
            targets = parameters[1]

        for target in targets:
            traversal_list = self.processAssociationReference(target)
            cast_event = parameters[2]
            for i in self.getInstances(source, traversal_list):
                ev = Event(cast_event.name, None, cast_event.parameters, i["instance"])
                self.to_send.append((self.name, i['to_class'], ev))
        
    def getInstances(self, source, traversal_list):
        currents = [{
            "to_class": None,
            "instance": source,
            "ref": None,
            "assoc_name": None,
            "assoc_index": None,
            "path": ""
        }]
        for (name, index) in traversal_list:
            nexts = []
            for current in currents:
                association = current["instance"].associations[name]
                if (index >= 0 ):
                    try:
                        nexts.append({
                            "to_class": association.to_class,
                            "instance": index,
                            "ref": current["instance"],
                            "assoc_name": name,
                            "assoc_index": index,
                            "path": current["path"] + ("" if current["path"] == "" else "/") + name + "[" + str(index) + "]"
                        })
                    except KeyError:
                        # Entry was removed, so ignore this request
                        pass
                elif (index == -1):
                    for i in association.instances:
                        parent = association.instances[i]
                        nexts.append({
                            "to_class": association.to_class,
                            "instance": parent,
                            "ref": current["instance"],
                            "assoc_name": name,
                            "assoc_index": index,
                            "path": current["path"] + ("" if current["path"] == "" else "/") + name + "[" + str(index) + "]"
                        })
                    #nexts.extend( association.instances.values() )
                else:
                    raise AssociationReferenceException("Incorrect index in association reference.")
            currents = nexts
        return currents
    
    def instantiate(self, class_name, construct_params):
        pass
    
    def createInstance(self, to_class, construct_params = []):
        instance = self.instantiate(to_class, construct_params)
        self.instances.add(instance)
        return instance

    def addMyOwnOutputListener(self, listener):
        self.output_listeners.append(listener)
    
    def constructObject(self, parameters):
        raise "Something went wrong "

    def extTransition(self, inputs):
        self.simulated_time += self.elapsed
        self.next_time = 0
        all_inputs = []
        for input_list in inputs.values():
            all_inputs.extend(input_list)
        for input in all_inputs:
            if isinstance(input, str):
                tem = eval(input)
                tem.instance = self.port_mappings[tem.port]
                tem.port = get_private_port(tem.port)
                self.addInput(tem)
            elif input[2].name == "create_instance":
                new_instance = self.constructObject(input[2].parameters)
                self.instances[self.next_instance] = new_instance
                p = new_instance.associations.get("parent")
                if p:
                    p.addInstance(input[2].instance)
                ev = Event("instance_created", None, [f"{input[2].parameters[0]}[{self.next_instance}]"], input[2].instance)
                self.to_send.append((input[1], input[0], ev))
                self.next_instance += 1
            elif input[2].name == "start_instance":
                test = self.processAssociationReference(input[2].parameters[0])
                index = test[0][1]
                instance = self.instances[index]
                instance.start()
                ev = Event("instance_started", None, [input[2].parameters[0]], input[2].instance)
                self.to_send.append((input[1], input[0], ev))
            elif input[2].name == "delete_instance":
                for index in input[2].parameters[1]:
                    i = self.instances[index]
                    for assoc_name in i.associations:
                        if not (assoc_name == "parent"):
                            traversal_list = self.processAssociationReference(assoc_name)
                            #instances = self.getInstances(i["instance"], traversal_list)
                            #if len(instances) > 0:
                            #    pass
                    i.user_defined_destructor()
                    i.stop()
                self.instances = {key: value for key, value in self.instances.items() if key not in input[2].parameters[1]}
                ev = Event("instance_deleted", None, input[2].parameters[1], input[2].instance)
                self.to_send.append((input[1], input[0], ev))
            elif input[2].name == "instance_created":
                instance = self.instances[input[2].instance]
                
                test = self.processAssociationReference(input[2].parameters[0])
                association_name = test[0][0]
                association_index = test[0][1]

                association = instance.associations[association_name]
                if association.allowedToAdd():
                    ''' allow subclasses to be instantiated '''
                    class_name = association.to_class # TODO: normally the following is behind this: if len(parameters) == 2 else parameters[2]
                    try:
                        new_index = association.addInstance(association_index)
                    except AssociationException as exception:
                        raise RuntimeException("Error adding instance to association '" + association_name + "': " + str(exception))
                instance.addEvent(input[2])
            elif input[2].name == "instance_started":
                instance = self.instances[input[2].instance]
                instance.addEvent(input[2])
            elif input[2].name == "instance_deleted":
                instance = self.instances[input[2].instance]
                for association in instance.associations.items():
                    if association[1].to_class == input[0]:
                        for index in input[2].parameters:
                            association[1].removeInstance(index)
                instance.addEvent(input[2])
            else:
                ev = input[2]
                self.addInput(ev)
        return self.instances

    def intTransition(self):
        earliest = min(self.getEarliestEventTime(), self.simulated_time + self.input_queue.getEarliestTime())
        if not (earliest == INFINITY):
            self.simulated_time = earliest
        self.to_send = []
        self.handleInput()
        self.stepAll()
        next_earliest = min(self.getEarliestEventTime(), self.input_queue.getEarliestTime())
        if not (len(self.to_send) == 0):
            self.next_time = 0
        elif next_earliest == INFINITY:
            self.next_time = INFINITY
        else:
            self.next_time = next_earliest - earliest
        return self.instances

    def outputFnc(self):
        to_dict = {}
        for sending in self.to_send:
            if sending[2].port == None:
                if self.obj_manager_out in to_dict:
                    to_dict[self.obj_manager_out].append(sending)
                else:
                    to_dict[self.obj_manager_out] = [sending]
            else:
                the_port = None
                for port in self.OPorts:
                    if port.name == sending[2].port:
                        the_port = port
                if the_port in to_dict:
                    to_dict[the_port].append(sending)
                else:
                    to_dict[the_port] = [sending]
        return to_dict
    
    def timeAdvance(self):
        return self.next_time

class TheObjectManager(AtomicDEVS):
    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.output = {}

        self.to_send = []
    
    def extTransition(self, inputs):
        all_inputs = inputs[self.input]
        for input in all_inputs:
            self.State.to_send.append(input)
        return self.State
    
    def intTransition(self):
        self.State.to_send = []
        return self.State
    
    def outputFnc(self):
        out_dict = {}
        for (source, target, message) in self.State.to_send:
            if self.output[target] in out_dict:
                out_dict[self.output[target]].append((source, target, message))
            else:
                out_dict[self.output[target]] = [(source, target, message)]
        return out_dict
    
    def timeAdvance(self):
        if self.State.to_send:
            return 0
        return INFINITY
    
# TODO: port class as wrapper to define the in and out ports the same as in SCCD
class Ports:
    private_port_counter = 0

    inports = {}
    outports = {}

    @classmethod
    def addOutputPort(self, virtual_name, instance=None):
        if instance == None:
            port_name = virtual_name
        else:
            port_name = "private_" + str(self.private_port_counter) + "_" + virtual_name
            self.outports[port_name] = instance
            self.private_port_counter += 1
        return port_name

    @classmethod
    def addInputPort(self, virtual_name, instance=None):
        if instance == None:
            port_name = virtual_name
        else:
            port_name = "private_" + str(self.private_port_counter) + "_" + virtual_name
            self.inports[port_name] = instance
            self.private_port_counter += 1
        return port_name

