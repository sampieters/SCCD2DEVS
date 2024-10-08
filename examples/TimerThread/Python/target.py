"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Simon Van Mierlo
Model name:   Timer (Threaded Version)

"""

from sccd.runtime.statecharts_core import *
import time

# package "Timer (Threaded Version)"

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
        self.starting_time = time.time()
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /running
        self.states["/running"] = State(1, "/running", self)
        self.states["/running"].setEnter(self._running_enter)
        self.states["/running"].setExit(self._running_exit)
        
        # state /interrupted
        self.states["/interrupted"] = State(2, "/interrupted", self)
        
        # add children
        self.states[""].addChild(self.states["/running"])
        self.states[""].addChild(self.states["/interrupted"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/running"]
        
        # transition /running
        _running_0 = Transition(self, self.states["/running"], [self.states["/running"]])
        _running_0.setAction(self._running_0_exec)
        _running_0.setTrigger(Event("_0after"))
        self.states["/running"].addTransition(_running_0)
        _running_1 = Transition(self, self.states["/running"], [self.states["/interrupted"]])
        _running_1.setAction(self._running_1_exec)
        _running_1.setTrigger(Event("interrupt", self.getInPortName("input")))
        self.states["/running"].addTransition(_running_1)
        
        # transition /interrupted
        _interrupted_0 = Transition(self, self.states["/interrupted"], [self.states["/interrupted"]])
        _interrupted_0.setAction(self._interrupted_0_exec)
        _interrupted_0.setTrigger(Event("interrupt", self.getInPortName("input")))
        self.states["/interrupted"].addTransition(_interrupted_0)
        _interrupted_1 = Transition(self, self.states["/interrupted"], [self.states["/running"]])
        _interrupted_1.setAction(self._interrupted_1_exec)
        _interrupted_1.setTrigger(Event("continue", self.getInPortName("input")))
        self.states["/interrupted"].addTransition(_interrupted_1)
    
    def _running_enter(self):
        self.addTimer(0, 0.05)
    
    def _running_exit(self):
        self.removeTimer(0)
    
    def _running_0_exec(self, parameters):
        self.big_step.outputEvent(Event("time_update", self.getOutPortName("output"), [self.getSimulatedTime(), time.time() - self.starting_time]))
    
    def _running_1_exec(self, parameters):
        self.big_step.outputEvent(Event("time_update", self.getOutPortName("output"), [self.getSimulatedTime(), time.time() - self.starting_time]))
    
    def _interrupted_0_exec(self, parameters):
        self.big_step.outputEvent(Event("time_update", self.getOutPortName("output"), [self.getSimulatedTime(), time.time() - self.starting_time]))
    
    def _interrupted_1_exec(self, parameters):
        self.big_step.outputEvent(Event("time_update", self.getOutPortName("output"), [self.getSimulatedTime(), time.time() - self.starting_time]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/running"].getEffectiveTargetStates()
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
        self.addInputPort("input")
        self.addOutputPort("output")
        self.object_manager.createInstance("MainApp", [])