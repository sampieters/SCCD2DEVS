"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Sam Pieters
Model name:   Dissasociate and associate an instance
Model description:
TODO: Does not work as I think it does
        Test 13: Dissasociate an instance and then associate an instance again
"""

from sccd.runtime.statecharts_core import *

# package "Dissasociate and associate an instance"

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
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
    
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