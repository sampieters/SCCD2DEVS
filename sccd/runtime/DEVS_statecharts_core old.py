import sys
import re
from sccd.runtime.event_queue import EventQueue
from pypdevs.infinity import INFINITY
from pypdevs.DEVS import *

from sccd.runtime.statecharts_core import StatechartSemantics, State, HistoryState, ShallowHistoryState, DeepHistoryState, ParallelState, Transition, BigStepState, ComboStepState, SmallStepState, RuntimeException, AssociationException, Association

from heapq import heappush, heappop, heapify
import threading

ELSE_GUARD = "ELSE_GUARD"

def get_private_port(text):
    match = re.search(r'private_\d+_(\w+)', text)

    if match:
        result = match.group(1)
        return result
    
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
    def fire(self, statechart):
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
            #########################################
            # TODO, here trace for exit state
            statechart.text += "\n"
            statechart.text += "\t\t\tEXIT STATE in model <%s>\n" % statechart.name
            statechart.text += f"\t\t\tState: {str(s)} (name: {s.name})\n"
            #########################################

            self.obj.eventless_states -= s.has_eventless_transitions
            # execute exit action(s)
            if s.exit:
                s.exit()
            self.obj.configuration_bitmap &= ~2 ** s.state_id

        # combo state changed area
        self.obj.combo_step.changed_bitmap |= 2 ** self.lca.state_id
        self.obj.combo_step.changed_bitmap |= self.lca.descendant_bitmap

        #########################################
         # TODO, here trace for fired transition
        statechart.text += "\n"
        statechart.text += "\t\t\tTRANSITION FIRED in model <%s>\n" % statechart.name
        statechart.text += "\t\t\t%s\n" % str(self)
        #########################################
        # execute transition action(s)
        if self.action:
            self.action(self.enabled_event.parameters if self.enabled_event else [])

        # enter states...
        targets = self.__getEffectiveTargetStates()
        enter_set = self.__enterSet(targets)
        for s in enter_set:
            #########################################
            # TODO, here trace for enter state
            statechart.text += "\n"
            statechart.text += "\t\t\tENTER STATE in model <%s>\n" % statechart.name
            statechart.text += f"\t\t\tState: {str(s)} (name: {s.name})\n"
            #########################################

            self.obj.eventless_states += s.has_eventless_transitions
            self.obj.configuration_bitmap |= 2 ** s.state_id
            # execute enter action(s)
            if s.enter:
                s.enter()

        if self.obj.eventless_states:
            self.obj.controller.state.eventless.add(self.obj)
        else:
            self.obj.controller.state.eventless.discard(self.obj)

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

        self.semantics = StatechartSemantics()

    # to break ties in the heap, compare by number of events in the list
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
        return self.controller.state.simulated_time * 1000

    def addTimer(self, index, timeout):
        self.timers_to_add[index] = (self.controller.state.simulated_time + timeout, Event("_%iafter" % index))

    def removeTimer(self, index):
        if index in self.timers_to_add:
            del self.timers_to_add[index]
        if index in self.timers:
            self.events.remove(self.timers[index])
            del self.timers[index]
        self.earliest_event_time = self.events.getEarliestTime()

    def addEvent(self, event_list, time_offset=0):
        event_time = self.controller.state.simulated_time + time_offset
        if not (event_time, self) in self.controller.state.instance_times:
            heappush(self.controller.state.instance_times, (event_time, self))
        if event_time < self.earliest_event_time:
            self.earliest_event_time = event_time
        if not isinstance(event_list, list):
            event_list = [event_list]
        for e in event_list:
            self.events.add(event_time, e)

    def processBigStepOutput(self):
        for e in self.big_step.output_events_port:
            self.controller.state.outputEvent(e)
        for e in self.big_step.output_events_om:
            self.controller.state.addEvent(e)

    def __set_stable(self, is_stable):
        self.is_stable = is_stable
        # self.earliest_event_time keeps track of the earliest time this instance will execute a transition
        if not is_stable:
            self.earliest_event_time = self.controller.state.simulated_time
        
        elif not self.active:
            self.earliest_event_time = INFINITY
        else:
            self.earliest_event_time = self.events.getEarliestTime()
        if self.earliest_event_time != INFINITY:
            if not (self.earliest_event_time, self) in self.controller.state.instance_times:
                heappush(self.controller.state.instance_times, (self.earliest_event_time, self))

    def step(self):
        is_stable = False
        while not is_stable:
            due = []
            if self.events.getEarliestTime() <= self.controller.state.simulated_time:
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
                    candidate[-1].fire(self.controller.state)
                else:
                    candidate[0].fire(self.controller.state)
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
            pass
            # TODO: Check (untill now no problems)
            #self.controller.object_manager.eventless.add(self)
    
class ClassState():
    def __init__(self, name) -> None:
        self.name = name
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

        self.text = ""

    def __str__(self) -> str:
        return self.text

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
            if self.instances[i] != source:
                self.instances[i].addEvent(new_event, time_offset)
        
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
            event = self.input_queue.pop()
            
            #if event.instance is None:
            #    event.instance = self.processAssociationReference(event.parameters[0])[0][1]
            if event.instance is None:
                target_instance = None
            else:
                target_instance = self.instances[event.instance]
            if target_instance == None:
                self.broadcast(None, event, event_time - self.simulated_time)
            else:
                target_instance.addEvent(event, event_time - self.simulated_time)

    def addInput(self, input_event_list, time_offset = 0):
        if not isinstance(input_event_list, list):
            input_event_list = [input_event_list]

        for e in input_event_list:
            if e.getName() == "":
                raise InputException("Input event can't have an empty name.")
            
            #if e.getPort() not in self.IPorts:
            #    raise InputException("Input port mismatch, no such port: " + e.getPort() + ".")
                
            self.input_queue.add((0 if self.simulated_time is None else 0) + time_offset, e)


    def handleEvent(self, e):
        self.handlers[e.getName()](e.getParameters())

    def outputEvent(self, event):
        self.to_send.append(event)

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

            traversal_list = self.processAssociationReference(parameters[1])
            to_copy_list = self.getInstances(source, traversal_list)




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
                self.to_send.append((self.name, i["to_class"], Event("associate_instance", None, parameters=parameters[1:])))
                #association = i["instance"].associations[last[0]]

                # TODO: sent associate_instance to instance
                association = self.instances[i['instance']].associations[last[0]]

                

                #if association.allowedToAdd():
                #    index = association.addInstance(wrapped_to_copy_instance)
                #    added_links.append(i["path"] + ("" if i["path"] == "" else "/") + last[0] + "[" + str(index) + "]")
                
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
                        # TODO: check if this check works
                        check = association.instances_to_ids[index]
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

class ClassBase(AtomicDEVS):    
    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        
        self.glob_outputs = {}
        self.outputs = {}
        self.state = ClassState(name)
        #self.elapsed = 0
        self.obj_manager_in = self.addInPort("obj_manager_in")
        self.obj_manager_out = self.addOutPort("obj_manager_out")

    def constructObject(self, parameters):
        raise "Something went wrong "

    def extTransition(self, inputs):
        # Update simulated time
        self.state.simulated_time += self.elapsed
        self.state.next_time = 0
        self.state.text = ""

        # Collect all inputs
        all_inputs = [input for input_list in inputs.values() for input in input_list]
        for input in all_inputs:
            if isinstance(input, str):
                tem = eval(input)

                # TODO: This works, the instance does not create a ball in bouncing balls but this is probably normal (port != input_port)

                #tem.instance = self.state.port_mappings[tem.port]
                tem.instance = self.state.port_mappings.setdefault(tem.port, None)

                if tem.instance != None:
                    tem.port = get_private_port(tem.port)
                self.state.addInput(tem)
            elif input[2].name == "create_instance":
                new_instance = self.constructObject(input[2].parameters)
                self.state.instances[self.state.next_instance] = new_instance
                p = new_instance.associations.get("parent")
                if p:
                    p.addInstance(input[2].instance)
                ev = Event("instance_created", None, [f"{input[2].parameters[0]}[{self.state.next_instance}]"], input[2].instance)
                self.state.to_send.append((input[1], input[0], ev))
                self.state.next_instance += 1
            elif input[2].name == "start_instance":
                test = self.state.processAssociationReference(input[2].parameters[0])
                index = test[0][1]
                instance = self.state.instances[index]
                instance.start()
                ev = Event("instance_started", None, [input[2].parameters[0]], input[2].instance)
                self.state.to_send.append((input[1], input[0], ev))
            elif input[2].name == "delete_instance":
                # TODO: deletion of port mappings

                # TODO: deletion, only use the parameter instances if assocaiton returns -1 as eveything must be removed

                # The instance parameter is now al instances that need to be deleted but should actually be the source
                parameters = input[2].parameters
                if len(parameters) < 2:
                    raise ParameterException ("The delete event needs at least 2 parameters.")
                else:

                    #source = self.state.instances[input[2].instance]
                    association_name = input[2].parameters[0]

                    traversal_list = self.state.processAssociationReference(association_name)
                    #instances = self.state.getInstances(source, traversal_list)
                    #association = source.associations[traversal_list[0][0]]


                    #instance_indexes = parameters[1]
                    instance_indexes = []
                    instances = []
                    for i in traversal_list:
                        if i[1] != -1:
                            instance_indexes.append(i[1])
                            instances.append(self.state.instances[i[1]])
                        else:
                            # TODO
                            instance_indexes.extend(parameters[1])
                            for ins in parameters[1]:
                                instances.append(self.state.instances[ins])

                    
                    for i in instances:
                        i.user_defined_destructor()
                        i.stop()
                        
                    self.state.instances = {key: value for key, value in self.state.instances.items() if key not in instance_indexes}

                    ev = Event("instance_deleted", None, [input[2].parameters[0], input[2].parameters[1]], input[2].instance)
                    self.state.to_send.append((input[1], input[0], ev))
                    #source.addEvent(Event("instance_deleted", parameters = [parameters[1]]))
                    
            elif input[2].name == "associate_instance":
                # TODO: index of the target
                #instance = self.state.instances[]

                if len(input[2].parameters) != 2:
                    raise ParameterException("The associate_instance event needs 3 parameters.")
                else:
                    #source = parameters[0]
                    
                    #to_copy_list = self.state.getInstances(source, self.processAssociationReference(input[2].parameters[0]))


                    to_copy_list = self.state.processAssociationReference(input[2].parameters[0])
                    if len(to_copy_list) != 1:
                        raise AssociationReferenceException ("Invalid source association reference.")
                    wrapped_to_copy_instance = to_copy_list[0]["instance"]
                    dest_list = self.processAssociationReference(input[2].parameters[1])
                    if len(dest_list) == 0:
                        raise AssociationReferenceException ("Invalid destination association reference.")
                    last = dest_list.pop()
                    if last[1] != -1:
                        raise AssociationReferenceException ("Last association name in association reference should not be accompanied by an index.")
                        
                    added_links = []
                    for i in self.getInstances(source, dest_list):
                        association = instance.associations[last[0]]
                        if association.allowedToAdd():
                            index = association.addInstance(wrapped_to_copy_instance)
                            added_links.append(i["path"] + ("" if i["path"] == "" else "/") + last[0] + "[" + str(index) + "]")
                        
                    source.addEvent(Event("instance_associated", parameters = [added_links]))
                
            elif input[2].name == "instance_created":
                instance = self.state.instances[input[2].instance]
                
                test = self.state.processAssociationReference(input[2].parameters[0])
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
                instance = self.state.instances[input[2].instance]
                instance.addEvent(input[2])
            elif input[2].name == "instance_deleted":
                source = self.state.instances[input[2].instance]
                association_name = input[2].parameters[0]

                traversal_list = self.state.processAssociationReference(association_name)
                instances = self.state.getInstances(source, traversal_list)
                association = source.associations[traversal_list[0][0]]

                for instance in instances:
                    try:
                        association.removeInstance(instance["instance"])
                    except AssociationException as exception:
                        raise RuntimeException("Error removing instance from association '" + association_name + "': " + str(exception))
                source.addEvent(Event("instance_deleted", parameters = [input[2].parameters[0]]))
            else:
                ev = input[2]
                self.state.addInput(ev)
        return self.state
    
    '''
    def intTransition(self):
        # Update simulated time and clear previous messages 
        self.state.simulated_time += self.state.next_time
        self.state.to_send = []
        # Calculate the next event time, clamp to ensure non-negative result
        self.state.next_time = min(self.state.getEarliestEventTime(), self.state.simulated_time + self.state.input_queue.getEarliestTime())
        self.state.next_time -= self.state.simulated_time
        self.state.next_time = max(self.state.next_time, 0.0)
        # Handle incoming inputs and do a step in all statecharts
        self.state.handleInput()
        self.state.stepAll()
        return self.state
    '''
    
    def intTransition(self):
        self.state.to_send = self.state.to_send[1:]
        self.state.text = ""

        if len(self.state.to_send) == 0:
            # Update simulated time and clear previous messages 
            self.state.simulated_time += self.state.next_time
            
            # Calculate the next event time, clamp to ensure non-negative result
            self.state.next_time = min(self.state.getEarliestEventTime(), self.state.simulated_time + self.state.input_queue.getEarliestTime())
            self.state.next_time -= self.state.simulated_time
            self.state.next_time = max(self.state.next_time, 0.0)
            # Handle incoming inputs and do a step in all statecharts
            self.state.handleInput()
            self.state.stepAll()
        else:
            self.state.next_time = 0
        return self.state

    '''
    def outputFnc(self):
        to_dict = {}
        for sending in self.state.to_send:
            if isinstance(sending, tuple) and sending[2].port == None:
                to_dict.setdefault(self.obj_manager_out, []).append(sending)
            else:
                the_port = next((port for port in self.OPorts if port.name == sending.port), None)
                to_dict.setdefault(the_port, []).append(sending)
        return to_dict
    '''

    def outputFnc(self):
        to_dict = {}
        #for sending in self.state.to_send:
        if not len(self.state.to_send) == 0:
            sending = self.state.to_send[0]

            if isinstance(sending, tuple) and sending[2].port == None:
                #to_dict.setdefault(self.obj_manager_out, []).append(sending)
                to_dict[self.obj_manager_out] = sending
            else:
                the_port = next((port for port in self.OPorts if port.name == sending.port), None)
                #to_dict.setdefault(the_port, []).append(sending)
                to_dict[the_port] = sending
        return to_dict
    
    def timeAdvance(self):
        return self.state.next_time

class ObjectManagerBase(AtomicDEVS):
    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.output = {}
    
    def extTransition(self, inputs):
        all_inputs = inputs[self.input]
        self.state.to_send.append(all_inputs)
        return self.state
    
    def intTransition(self):
        self.state.to_send.clear()
        return self.state
    
    def outputFnc(self):
        out_dict = {}
        for source, target, message in self.state.to_send:
            out_dict.setdefault(self.output.get(target), []).append((source, target, message))
        return out_dict
    
    def timeAdvance(self):
        return 0 if self.state.to_send else INFINITY
    
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
