"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration) and Sam Pieters (DEVS)

Model author: Sam Pieters
Model name:   Output Test
Model description:
Test 2: Check if the model outputs one event on the right time.
"""

from sccd.runtime.DEVS_statecharts_core import *

# package "Output Test"

class MainAppInstance(RuntimeClassBase):
    def __init__(self, atomdevs):
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
        MainAppInstance.user_defined_constructor(self)
        port_name = Ports.addInputPort("<narrow_cast>", self)
        atomdevs.addInPort(port_name)
    
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
        self.states["/state1"].setExit(self._state1_exit)
        
        # state /end
        self.states["/end"] = State(2, "/end", self)
        self.states["/end"].setEnter(self._end_enter)
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].addChild(self.states["/end"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
        
        # transition /state1
        _state1_0 = Transition(self, self.states["/state1"], [self.states["/end"]])
        _state1_0.setTrigger(Event("_0after"))
        self.states["/state1"].addTransition(_state1_0)
    
    def _state1_enter(self):
        self.addTimer(0, 1)
    
    def _state1_exit(self):
        self.removeTimer(0)
    
    def _end_enter(self):
        self.big_step.outputEvent(Event("test_event", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0))]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/state1"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class MainApp(ObjectManagerBase):
    def __init__(self, name):
        ObjectManagerBase.__init__(self, name)
        self.input = self.addInPort("input")
        self.output = self.addOutPort("ui")
        self.instances[self.next_instance] = MainAppInstance(self)
        self.next_instance = self.next_instance + 1
    
    def constructObject(self, parameters):
        new_instance = MainAppInstance(self)
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

class Controller(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)
        self.in_ui = self.addInPort("ui")
        Ports.addInputPort("ui")
        self.out_ui = self.addOutPort("ui")
        Ports.addOutputPort("ui")
        self.objectmanager = self.addSubModel(ObjectManager("ObjectManager"))
        self.atomic0 = self.addSubModel(MainApp("MainApp"))
        self.connectPorts(self.atomic0.obj_manager_out, self.objectmanager.input)
        self.connectPorts(self.objectmanager.output["MainApp"], self.atomic0.obj_manager_in)
        self.connectPorts(self.atomic0.output, self.out_ui)