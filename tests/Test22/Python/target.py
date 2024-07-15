"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Sam Pieters
Model name:   Dissasociate an instance
Model description:
Test 12: Dissasociate an instance
"""

from sccd.runtime.statecharts_core import *

# package "Dissasociate an instance"

class MainApp(RuntimeClassBase):
    def __init__(self, controller):
        RuntimeClassBase.__init__(self, controller)
        
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        MainApp.user_defined_constructor(self)
    
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
        
        # state /state3
        self.states["/state3"] = State(3, "/state3", self)
        self.states["/state3"].setEnter(self._state3_enter)
        
        # state /state4
        self.states["/state4"] = State(4, "/state4", self)
        self.states["/state4"].setEnter(self._state4_enter)
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].addChild(self.states["/state2"])
        self.states[""].addChild(self.states["/state3"])
        self.states[""].addChild(self.states["/state4"])
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
        _state2_0.setTrigger(Event("instance_started", None))
        self.states["/state2"].addTransition(_state2_0)
        
        # transition /state3
        _state3_0 = Transition(self, self.states["/state3"], [self.states["/state4"]])
        _state3_0.setAction(self._state3_0_exec)
        _state3_0.setTrigger(Event("instance_disassociated", None))
        self.states["/state3"].addTransition(_state3_0)
    
    def _state1_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "linkA", "A"]))
    
    def _state3_enter(self):
        self.big_step.outputEventOM(Event("disassociate_instance", None, [self, "linkA"]))
    
    def _state4_enter(self):
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, self.association_name, Event("sanity_check", None, [])]))
    
    def _state1_0_exec(self, parameters):
        association_name = parameters[0]
        self.association_name = association_name
        self.big_step.outputEvent(Event("instance_created_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
    
    def _state2_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_started_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, association_name, Event("link_check", None, [association_name])]))
    
    def _state3_0_exec(self, parameters):
        deleted_links = parameters[0]
        self.big_step.outputEvent(Event("instance_disassociated_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), deleted_links]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/state1"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class A(RuntimeClassBase):
    def __init__(self, controller):
        RuntimeClassBase.__init__(self, controller)
        
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        A.user_defined_constructor(self)
    
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

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "MainApp":
            instance = MainApp(self.controller)
            instance.associations = {}
            instance.associations["linkA"] = Association("A", 0, -1)
        elif class_name == "A":
            instance = A(self.controller)
            instance.associations = {}
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None, behind_schedule_callback = None):
        if keep_running == None: keep_running = True
        if behind_schedule_callback == None: behind_schedule_callback = None
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running, behind_schedule_callback)
        self.addInputPort("ui")
        self.addOutputPort("ui")
        self.object_manager.createInstance("MainApp", [])