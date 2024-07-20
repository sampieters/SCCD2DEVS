"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Sam Pieters
Model name:   Bouncing_Balls_DEVS_Version
Model description:
Tkinter frame with bouncing balls in it.
"""

from sccd.runtime.statecharts_core import *

# package "Bouncing_Balls_DEVS_Version"

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
        self.huh = 21
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /running
        self.states["/running"] = State(1, "/running", self)
        
        # add children
        self.states[""].addChild(self.states["/running"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/running"]
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/running"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class B(A):
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
        A.user_defined_constructor(self)
        self.nr_of_fields = 0
    
    def user_defined_destructor(self):
        # call super class destructors
        A.user_defined_destructor(self)
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /running
        self.states["/running"] = State(1, "/running", self)
        self.states["/running"].setEnter(self._running_enter)
        
        # add children
        self.states[""].addChild(self.states["/running"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/running"]
    
    def _running_enter(self):
        print(self.huh)
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/running"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "A":
            instance = A(self.controller)
            instance.associations = {}
        elif class_name == "B":
            instance = B(self.controller)
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
        self.object_manager.createInstance("B", [])