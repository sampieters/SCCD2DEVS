"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration) and Sam Pieters (DEVS)

Model author: Sam Pieters
Model name:   Create and Start Multiple Instances Of The Same Class
Model description:
Test 9: Create and start multiple instances of the same class
"""

from sccd.runtime.DEVS_statecharts_core import *

# package "Create and Start Multiple Instances Of The Same Class"

class MainAppInstance(RuntimeClassBase):
    def __init__(self, atomdevs):
        RuntimeClassBase.__init__(self, atomdevs)
        self.associations = {}
        self.associations["linkA"] = Association("A", 0, -1)
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        MainAppInstance.user_defined_constructor(self)
        port_name = Ports.addInputPort("<narrow_cast>", self)
        atomdevs.addInPort(port_name)
    
    def user_defined_constructor(self):
        self.instances = 10
    
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
        
        # state /state3
        self.states["/state3"] = State(3, "/state3", self)
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].addChild(self.states["/state2"])
        self.states[""].addChild(self.states["/state3"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
        
        # transition /state1
        _state1_0 = Transition(self, self.states["/state1"], [self.states["/state2"]])
        _state1_0.setAction(self._state1_0_exec)
        _state1_0.setTrigger(Event("instance_created", None))
        self.states["/state1"].addTransition(_state1_0)
        
        # transition /state2
        _state2_0 = Transition(self, self.states["/state2"], [self.states["/state2"]])
        _state2_0.setAction(self._state2_0_exec)
        _state2_0.setTrigger(Event("instance_started", None))
        self.states["/state2"].addTransition(_state2_0)
        _state2_1 = Transition(self, self.states["/state2"], [self.states["/state1"]])
        _state2_1.setTrigger(None)
        _state2_1.setGuard(self._state2_1_guard)
        self.states["/state2"].addTransition(_state2_1)
        _state2_2 = Transition(self, self.states["/state2"], [self.states["/state3"]])
        _state2_2.setTrigger(None)
        _state2_2.setGuard(self._state2_2_guard)
        self.states["/state2"].addTransition(_state2_2)
    
    def _state1_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "linkA", "A", self.instances]))
    
    def _state1_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_created_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
        self.instances -= 1
    
    def _state2_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_started_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
    
    def _state2_1_guard(self, parameters):
        return self.instances != 0
    
    def _state2_2_guard(self, parameters):
        return self.instances == 0
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/state1"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class MainApp(ObjectManagerBase):
    def __init__(self, name):
        ObjectManagerBase.__init__(self, name)
        self.input = self.addInPort("input")
        self.output = self.addOutPort("ui")
        self.outputs["linkA"] = self.addOutPort("linkA")
        self.instances[self.next_instance] = MainAppInstance(self)
        self.next_instance = self.next_instance + 1
    
    def constructObject(self, parameters):
        new_instance = MainAppInstance(self)
        return new_instance

class AInstance(RuntimeClassBase):
    def __init__(self, atomdevs, instance_number):
        RuntimeClassBase.__init__(self, atomdevs)
        self.associations = {}
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        AInstance.user_defined_constructor(self, instance_number)
        port_name = Ports.addInputPort("<narrow_cast>", self)
        atomdevs.addInPort(port_name)
    
    def user_defined_constructor(self, instance_number):
        self.number = instance_number
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /state1
        self.states["/state1"] = State(1, "/state1", self)
        self.states["/state1"].setEnter(self._state1_enter)
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
    
    def _state1_enter(self):
        self.big_step.outputEvent(Event("statechart_started_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), self.number]))
        self.big_step.outputEvent(Event("constructor_initialized_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), self.number]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/state1"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class A(ObjectManagerBase):
    def __init__(self, name):
        ObjectManagerBase.__init__(self, name)
        self.input = self.addInPort("input")
        self.output = self.addOutPort("ui")
    
    def constructObject(self, parameters):
        new_instance = AInstance(self, parameters[2])
        return new_instance

class ObjectManagerState:
    def __init__(self):
        self.to_send = [("MainApp", "MainApp", Event("start_instance", None, ["MainApp[0]"], 0))]

class ObjectManager(TheObjectManager):
    def __init__(self, name):
        TheObjectManager.__init__(self, name)
        self.State = ObjectManagerState()
        self.input = self.addInPort("input")
        self.output["MainApp"] = self.addOutPort()
        self.output["A"] = self.addOutPort()

class Controller(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)
        self.in_ui = self.addInPort("ui")
        Ports.addInputPort("ui")
        self.out_ui = self.addOutPort("ui")
        Ports.addOutputPort("ui")
        self.objectmanager = self.addSubModel(ObjectManager("ObjectManager"))
        self.atomic0 = self.addSubModel(MainApp("MainApp"))
        self.atomic1 = self.addSubModel(A("A"))
        self.connectPorts(self.atomic0.obj_manager_out, self.objectmanager.input)
        self.connectPorts(self.objectmanager.output["MainApp"], self.atomic0.obj_manager_in)
        self.connectPorts(self.atomic0.outputs["linkA"], self.atomic1.input)
        self.connectPorts(self.atomic1.obj_manager_out, self.objectmanager.input)
        self.connectPorts(self.objectmanager.output["A"], self.atomic1.obj_manager_in)
        self.connectPorts(self.atomic0.output, self.out_ui)
        self.connectPorts(self.atomic1.output, self.out_ui)