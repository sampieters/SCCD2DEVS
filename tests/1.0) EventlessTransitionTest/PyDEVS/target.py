"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration) and Sam Pieters (DEVS)

Model author: Sam Pieters
Model name:   EventlessTransitionTest
Model description:
Test 1: Check if a statechart directly transitions without an event being raised.
"""

from sccd.runtime.DEVS_statecharts_core import *

# package "EventlessTransitionTest"

class MainAppInstance(RuntimeClassBase):
    def __init__(self, atomdevs, id, start_port_id):
        RuntimeClassBase.__init__(self, atomdevs, id)
        self.associations = {}
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        MainAppInstance.user_defined_constructor(self)
        port_name = addInputPort("<narrow_cast>", start_port_id)
        atomdevs.addInPort(port_name)
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
        
        # state /state2
        self.states["/state2"] = State(2, "/state2", self)
        
        # state /state3
        self.states["/state3"] = State(3, "/state3", self)
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].addChild(self.states["/state2"])
        self.states[""].addChild(self.states["/state3"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
        
        # transition /state1
        _state1_0 = Transition(self, self.states["/state1"], [self.states["/state3"]])
        _state1_0.setTrigger(None)
        self.states["/state1"].addTransition(_state1_0)
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/state1"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class MainApp(ClassBase):
    def __init__(self, name):
        ClassBase.__init__(self, name)
        self.input = self.addInPort("input")
        new_instance = self.constructObject(0, 0, [])
        self.state.instances[new_instance.instance_id] = new_instance
        self.state.next_instance = self.state.next_instance + 1
    
    def constructObject(self, id, start_port_id, parameters):
        new_instance = MainAppInstance(self, id, start_port_id)
        return new_instance

class Dummy(ObjectManagerState):
    def __init__(self):
        ObjectManagerState.__init__(self)
    
    def instantiate(self, class_name, construct_params):
        instance = {}
        instance["name"] = class_name
        if class_name == "MainApp":
            self.narrow_cast_id = self.narrow_cast_id + 0
            instance["associations"] = {}
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class ObjectManager(ObjectManagerBase):
    def __init__(self, name):
        ObjectManagerBase.__init__(self, name)
        self.state = Dummy()
        self.input = self.addInPort("input")
        self.output["MainApp"] = self.addOutPort()
        self.state.createInstance("MainApp", [])
        self.state.to_send.append((("MainApp", 0), ("MainApp", 0), Event("start_instance", None, ["MainApp[0]"])))

class Controller(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)
        self.objectmanager = self.addSubModel(ObjectManager("ObjectManager"))
        self.atomics = []
        self.atomics.append(self.addSubModel(MainApp("MainApp")))
        self.connectPorts(self.atomics[0].obj_manager_out, self.objectmanager.input)
        self.connectPorts(self.objectmanager.output["MainApp"], self.atomics[0].obj_manager_in)