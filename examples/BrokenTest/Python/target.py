"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Yentl Van Tendeloo+Simon Van Mierlo
Model name:   broken
Model description:
Broken!
        Sam: The file was called external input + TODO: don't get what this file needs to do
"""

from sccd.runtime.statecharts_core import *

# package "broken"

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
        
        # state /x
        self.states["/x"] = State(1, "/x", self)
        self.states["/x"].setEnter(self._x_enter)
        
        # state /ready
        self.states["/ready"] = State(2, "/ready", self)
        self.states["/ready"].setEnter(self._ready_enter)
        self.states["/ready"].setExit(self._ready_exit)
        
        # state /done
        self.states["/done"] = State(3, "/done", self)
        
        # add children
        self.states[""].addChild(self.states["/x"])
        self.states[""].addChild(self.states["/ready"])
        self.states[""].addChild(self.states["/done"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/x"]
        
        # transition /x
        _x_0 = Transition(self, self.states["/x"], [self.states["/ready"]])
        _x_0.setAction(self._x_0_exec)
        _x_0.setTrigger(Event("instance_created", None))
        self.states["/x"].addTransition(_x_0)
        
        # transition /ready
        _ready_0 = Transition(self, self.states["/ready"], [self.states["/ready"]])
        _ready_0.setAction(self._ready_0_exec)
        _ready_0.setTrigger(Event("_0after"))
        self.states["/ready"].addTransition(_ready_0)
        _ready_1 = Transition(self, self.states["/ready"], [self.states["/done"]])
        _ready_1.setAction(self._ready_1_exec)
        _ready_1.setTrigger(Event("close", None))
        self.states["/ready"].addTransition(_ready_1)
    
    def _x_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, 'child', 'B']))
    
    def _ready_enter(self):
        self.addTimer(0, 0.001)
    
    def _ready_exit(self):
        self.removeTimer(0)
    
    def _x_0_exec(self, parameters):
        instancename = parameters[0]
        self.instancename = instancename
        self.big_step.outputEventOM(Event("start_instance", None, [self, self.instancename]))
    
    def _ready_0_exec(self, parameters):
        for _ in range(100000):
            pass
    
    def _ready_1_exec(self, parameters):
        self.big_step.outputEventOM(Event("delete_instance", None, [self, self.instancename]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/x"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class B(RuntimeClassBase):
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
        B.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /z
        self.states["/z"] = State(1, "/z", self)
        
        # add children
        self.states[""].addChild(self.states["/z"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/z"]
        
        # transition /z
        _z_0 = Transition(self, self.states["/z"], [self.states["/z"]])
        _z_0.setAction(self._z_0_exec)
        _z_0.setTrigger(Event("stop", self.getInPortName("input")))
        self.states["/z"].addTransition(_z_0)
    
    def _z_0_exec(self, parameters):
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, 'parent[0]', Event("close", None, [])]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/z"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "A":
            instance = A(self.controller)
            instance.associations = {}
            instance.associations["child"] = Association("B", 0, 1)
        elif class_name == "B":
            instance = B(self.controller)
            instance.associations = {}
            instance.associations["parent"] = Association("A", 1, 1)
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None, behind_schedule_callback = None):
        if keep_running == None: keep_running = True
        if behind_schedule_callback == None: behind_schedule_callback = None
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running, behind_schedule_callback)
        self.addInputPort("input")
        self.object_manager.createInstance("A", [])