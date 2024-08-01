"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Sam Pieters
Model name:   Create and Delete an Instance (other than the MainApp)
Model description:
Test 12: Check if an instance can be deleted after the creation, the instance is not started yet.
"""

from sccd.runtime.statecharts_core import *

# package "Create and Delete an Instance (other than the MainApp)"

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
        self.states["/state2"].setEnter(self._state2_enter)
        
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
        _state2_0 = Transition(self, self.states["/state2"], [self.states["/state3"]])
        _state2_0.setAction(self._state2_0_exec)
        _state2_0.setTrigger(Event("instance_created", None))
        self.states["/state2"].addTransition(_state2_0)
        
        # transition /state3
        _state3_0 = Transition(self, self.states["/state3"], [self.states["/state3"]])
        _state3_0.setAction(self._state3_0_exec)
        _state3_0.setTrigger(Event("instance_deleted", None))
        self.states["/state3"].addTransition(_state3_0)
    
    def _state1_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "linkA", "A"]))
    
    def _state2_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "linkA", "A"]))
    
    def _state1_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_created_succesfully", self.getOutPortName("ui"), [association_name]))
    
    def _state2_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_created_succesfully", self.getOutPortName("ui"), [association_name]))
        self.big_step.outputEventOM(Event("delete_instance", None, [self, 'linkA']))
    
    def _state3_0_exec(self, parameters):
        deleted_links = parameters[0]
        self.big_step.outputEvent(Event("instance_deleted_succesfully", self.getOutPortName("ui"), [deleted_links]))
    
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
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
    
    def _state1_enter(self):
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