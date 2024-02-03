import sys

from sccd.runtime.event_queue import EventQueue
from pypdevs.infinity import INFINITY

DEBUG = False
ELSE_GUARD = "ELSE_GUARD"

def print_debug(msg):
    if DEBUG:
        print(msg)

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
            self.size -= 1
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
            print_debug('EXIT: %s::%s' % (self.obj.__class__.__name__, s.name))
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
            print_debug('ENTER: %s::%s' % (self.obj.__class__.__name__, s.name))
            self.obj.eventless_states += s.has_eventless_transitions
            self.obj.configuration_bitmap |= 2 ** s.state_id
            # execute enter action(s)
            if s.enter:
                s.enter()

        if self.obj.eventless_states:
            self.obj.controller.object_manager.eventless.add(self.obj)
        else:
            self.obj.controller.object_manager.eventless.discard(self.obj)

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
    def __init__(self, event_name, port="", parameters=[]):
        self.name = event_name
        self.parameters = parameters
        self.port = port

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

        self.narrow_cast_port = self.controller.addInputPort("<narrow_cast>", self)

        self.semantics = StatechartSemantics()

    # to break ties in the heap,
    # compare by number of events in the list
    def __lt__(self, other):
        return len(self.events.event_list) < len(other.events.event_list)

    def getChildren(self, link_name):
        traversal_list = self.controller.object_manager.processAssociationReference(link_name)
        return [i["instance"] for i in self.controller.object_manager.getInstances(self, traversal_list)]

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

    def sccd_yield(self):
        return max(0, (self.controller.accurate_time.get_wct() - self.controller.simulated_time) / 1000.0)

    def getSimulatedTime(self):
        return self.controller.getSimulatedTime()

    def getWallClockTime(self):
        return self.controller.getWallClockTime()

    def updateConfiguration(self, states):
        self.configuration.extend(states)
        self.configuration_bitmap = sum([2 ** s.state_id for s in states])

    def addTimer(self, index, timeout):
        self.timers_to_add[index] = (self.controller.simulated_time + int(timeout * 1000), Event("_%iafter" % index))

    def removeTimer(self, index):
        if index in self.timers_to_add:
            del self.timers_to_add[index]
        if index in self.timers:
            self.events.remove(self.timers[index])
            del self.timers[index]
        self.earliest_event_time = self.events.getEarliestTime()

    def addEvent(self, event_list, time_offset=0):
        event_time = self.controller.simulated_time + time_offset
        #if not (event_time, self) in self.controller.object_manager.instance_times:
            #heappush(self.controller.object_manager.instance_times, (event_time, self))
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
            self.controller.object_manager.addEvent(e)

    def __set_stable(self, is_stable):
        self.is_stable = is_stable
        # self.earliest_event_time keeps track of the earliest time this instance will execute a transition
        if not is_stable:
            self.earliest_event_time = self.controller.simulated_time
        elif not self.active:
            self.earliest_event_time = INFINITY
        else:
            self.earliest_event_time = self.events.getEarliestTime()
        #if self.earliest_event_time != INFINITY:
            #if not (self.earliest_event_time, self) in self.controller.object_manager.instance_times:
                #heappush(self.controller.object_manager.instance_times, (self.earliest_event_time, self))

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
            self.controller.object_manager.eventless.add(self)

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

