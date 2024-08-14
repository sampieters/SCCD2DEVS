"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration) and Sam Pieters (DEVS)

Model author: Sam Pieters
Model name:   Dissasociate multiple instances
Model description:
Test 23: Dissasociate multiple instances
"""

from sccd.runtime.DEVS_statecharts_core import *

# package "Dissasociate multiple instances"

class MainAppInstance(RuntimeClassBase):
    def __init__(self, atomdevs, id, start_port_id):
        RuntimeClassBase.__init__(self, atomdevs, id)
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        MainAppInstance.user_defined_constructor(self)
        port_name = addInputPort("ui", start_port_id, True)
        atomdevs.state.port_mappings[port_name] = id
        port_name = addInputPort("<narrow_cast>", start_port_id)
        atomdevs.state.port_mappings[port_name] = id
    
    def user_defined_constructor(self):
        self.association_name = None
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /state1
        self.states["/state1"] = State(1, "/state1", self)
        self.states["/state1"].setEnter(self._state1_enter)
        
        # state /state2
        self.states["/state2"] = State(2, "/state2", self)
        self.states["/state2"].setEnter(self._state2_enter)
        
        # state /state3
        self.states["/state3"] = State(3, "/state3", self)
        
        # state /state4
        self.states["/state4"] = State(4, "/state4", self)
        self.states["/state4"].setEnter(self._state4_enter)
        
        # state /state5
        self.states["/state5"] = State(5, "/state5", self)
        self.states["/state5"].setEnter(self._state5_enter)
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].addChild(self.states["/state2"])
        self.states[""].addChild(self.states["/state3"])
        self.states[""].addChild(self.states["/state4"])
        self.states[""].addChild(self.states["/state5"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
        
        # transition /state1
        _state1_0 = Transition(self, self.states["/state1"], [self.states["/state2"]])
        _state1_0.setAction(self._state1_0_exec)
        _state1_0.setTrigger(Event("instance_created", None))
        self.states["/state1"].addTransition(_state1_0)
        
        # transition /state2
        _state2_0 = Transition(self, self.states["/state2"], [self.states["/state3"]])
        _state2_0.setAction(self._state2_0_exec)
        _state2_0.setTrigger(Event("instance_created", None))
        self.states["/state2"].addTransition(_state2_0)
        
        # transition /state3
        _state3_0 = Transition(self, self.states["/state3"], [self.states["/state4"]])
        _state3_0.setAction(self._state3_0_exec)
        _state3_0.setTrigger(Event("instance_started", None))
        self.states["/state3"].addTransition(_state3_0)
        
        # transition /state4
        _state4_0 = Transition(self, self.states["/state4"], [self.states["/state5"]])
        _state4_0.setAction(self._state4_0_exec)
        _state4_0.setTrigger(Event("instance_disassociated", None))
        self.states["/state4"].addTransition(_state4_0)
    
    def _state1_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "linkA", "A"]))
    
    def _state2_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "linkA", "A"]))
    
    def _state4_enter(self):
        self.big_step.outputEventOM(Event("disassociate_instance", None, [self, "linkA"]))
    
    def _state5_enter(self):
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, self.association_name, Event("sanity_check", None, [])]))
    
    def _state1_0_exec(self, parameters):
        association_name = parameters[0]
        self.association_name = association_name
        self.big_step.outputEvent(Event("instance_created_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
    
    def _state2_0_exec(self, parameters):
        association_name = parameters[0]
        self.association_name = association_name
        self.big_step.outputEvent(Event("instance_created_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
    
    def _state3_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_started_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, association_name, Event("link_check", None, [association_name])]))
    
    def _state4_0_exec(self, parameters):
        deleted_links = parameters[0]
        self.big_step.outputEvent(Event("instance_disassociated_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), deleted_links]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/state1"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class MainApp(ClassBase):
    def __init__(self, name):
        ClassBase.__init__(self, name)
        self.input = self.addInPort("input")
        self.glob_outputs["ui"] = self.addOutPort("ui")
        new_instance = self.constructObject(0, 0, [])
        self.state.instances[new_instance.instance_id] = new_instance
        new_instance.start()
        self.state.next_time = 0
    
    def constructObject(self, id, start_port_id, parameters):
        new_instance = MainAppInstance(self, id, start_port_id)
        return new_instance

class AInstance(RuntimeClassBase):
    def __init__(self, atomdevs, id, start_port_id):
        RuntimeClassBase.__init__(self, atomdevs, id)
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        AInstance.user_defined_constructor(self)
        port_name = addInputPort("ui", start_port_id, True)
        atomdevs.state.port_mappings[port_name] = id
        port_name = addInputPort("<narrow_cast>", start_port_id)
        atomdevs.state.port_mappings[port_name] = id
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /state1
        self.states["/state1"] = State(1, "/state1", self)
        self.states["/state1"].setEnter(self._state1_enter)
        
        # state /state2
        self.states["/state2"] = State(2, "/state2", self)
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].addChild(self.states["/state2"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
        
        # transition /state1
        _state1_0 = Transition(self, self.states["/state1"], [self.states["/state2"]])
        _state1_0.setTrigger(None)
        self.states["/state1"].addTransition(_state1_0)
        
        # transition /state2
        _state2_0 = Transition(self, self.states["/state2"], [self.states["/state2"]])
        _state2_0.setAction(self._state2_0_exec)
        _state2_0.setTrigger(Event("link_check", None))
        self.states["/state2"].addTransition(_state2_0)
        _state2_1 = Transition(self, self.states["/state2"], [self.states["/state2"]])
        _state2_1.setAction(self._state2_1_exec)
        _state2_1.setTrigger(Event("sanity_check", None))
        self.states["/state2"].addTransition(_state2_1)
    
    def _state1_enter(self):
        self.big_step.outputEvent(Event("statechart_started_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0))]))
    
    def _state2_0_exec(self, parameters):
        link_name = parameters[0]
        self.big_step.outputEvent(Event("instance_linked_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), link_name]))
    
    def _state2_1_exec(self, parameters):
        self.big_step.outputEvent(Event("not_possible", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0))]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/state1"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class A(ClassBase):
    def __init__(self, name):
        ClassBase.__init__(self, name)
        self.input = self.addInPort("input")
        self.glob_outputs["ui"] = self.addOutPort("ui")
    
    def constructObject(self, id, start_port_id, parameters):
        new_instance = AInstance(self, id, start_port_id)
        return new_instance

def instantiate(self, class_name, construct_params):
    instance = {}
    instance["name"] = class_name
    if class_name == "MainApp":
        self.narrow_cast_id = self.narrow_cast_id + 0
        instance["associations"] = {}
        instance["associations"]["linkA"] = Association("A", 0, -1)
    elif class_name == "A":
        self.narrow_cast_id = self.narrow_cast_id + 0
        instance["associations"] = {}
    else:
        raise Exception("Cannot instantiate class " + class_name)
    return instance
ObjectManagerState.instantiate = instantiate

class ObjectManager(ObjectManagerBase):
    def __init__(self, name):
        ObjectManagerBase.__init__(self, name)
        self.state = ObjectManagerState()
        self.input = self.addInPort("input")
        self.output["MainApp"] = self.addOutPort()
        self.output["A"] = self.addOutPort()
        self.state.createInstance("MainApp", [])

class Controller(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)
        self.in_ui = self.addInPort("ui")
        self.out_ui = self.addOutPort("ui")
        self.objectmanager = self.addSubModel(ObjectManager("ObjectManager"))
        self.atomics = []
        self.atomics.append(self.addSubModel(MainApp("MainApp")))
        self.atomics.append(self.addSubModel(A("A")))
        self.connectPorts(self.atomics[0].obj_manager_out, self.objectmanager.input)
        self.connectPorts(self.objectmanager.output["MainApp"], self.atomics[0].obj_manager_in)
        self.connectPorts(self.atomics[1].obj_manager_out, self.objectmanager.input)
        self.connectPorts(self.objectmanager.output["A"], self.atomics[1].obj_manager_in)
        self.connectPorts(self.atomics[0].glob_outputs["ui"], self.out_ui)
        self.connectPorts(self.in_ui, self.atomics[0].input)
        self.connectPorts(self.atomics[1].glob_outputs["ui"], self.out_ui)
        self.connectPorts(self.in_ui, self.atomics[1].input)