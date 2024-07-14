"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Sam Pieters
Model name:   Create and Start Instance
Model description:
Test 8: Check if an instance is created and started successfully with constructor parameters (other than the main app)
"""

from sccd.runtime.statecharts_core import *

# package "Create and Start Instance"

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
        _state1_0.setAction(self._state1_0_exec)
        _state1_0.setTrigger(Event("instance_created", None))
        self.states["/state1"].addTransition(_state1_0)
        
        # transition /state2
        _state2_0 = Transition(self, self.states["/state2"], [self.states["/state2"]])
        _state2_0.setAction(self._state2_0_exec)
        _state2_0.setTrigger(Event("instance_started", None))
        self.states["/state2"].addTransition(_state2_0)
    
    def _state1_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "linkA", "A", 1, 3.14, "test", [1, 2, 3], {"1": 1, "2": 2, "3": 3}]))
    
    def _state1_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_created_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
    
    def _state2_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_started_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), association_name]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/state1"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class A(RuntimeClassBase):
    def __init__(self, controller, integer, floating_point, astring, alist, adict):
        RuntimeClassBase.__init__(self, controller)
        
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        A.user_defined_constructor(self, integer, floating_point, astring, alist, adict)
    
    def user_defined_constructor(self, integer, floating_point, astring, alist, adict):
        self.integer = integer
        self.floating_point = floating_point
        self.astring = astring
        self.alist = alist
        self.adict = adict
    
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
        self.big_step.outputEvent(Event("statechart_started_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0))]))
        self.big_step.outputEvent(Event("constructor_initialized_succesfully", self.getOutPortName("ui"), [str('%.2f' % (self.getSimulatedTime() / 1000.0)), self.integer, self.floating_point, self.astring, self.alist, self.adict]))
    
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
            instance = A(self.controller, construct_params[0], construct_params[1], construct_params[2], construct_params[3], construct_params[4])
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