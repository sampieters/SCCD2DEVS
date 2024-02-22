"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Simon Van Mierlo
Model name:   Bouncing Balls - Tkinter Version 
Model description:
Tkinter frame with bouncing balls in it.
"""

from sccd.runtime.statecharts_core import *
import random
import tkinter as tk
from widget import Widget

# package "Bouncing Balls - Tkinter Version "

class MainApp(RuntimeClassBase):
    def __init__(self, controller, root):
        RuntimeClassBase.__init__(self, controller)
        
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        MainApp.user_defined_constructor(self, root)
    
    def user_defined_constructor(self, root):
        self.nr_of_windows = 0
        self.root = root
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /main
        self.states["/main"] = ParallelState(1, "/main", self)
        
        # state /main/main_behaviour
        self.states["/main/main_behaviour"] = State(2, "/main/main_behaviour", self)
        
        # state /main/main_behaviour/initializing
        self.states["/main/main_behaviour/initializing"] = State(3, "/main/main_behaviour/initializing", self)
        self.states["/main/main_behaviour/initializing"].setEnter(self._main_main_behaviour_initializing_enter)
        
        # state /main/main_behaviour/running
        self.states["/main/main_behaviour/running"] = State(4, "/main/main_behaviour/running", self)
        
        # state /main/creating_behaviour
        self.states["/main/creating_behaviour"] = State(5, "/main/creating_behaviour", self)
        
        # state /main/creating_behaviour/waiting
        self.states["/main/creating_behaviour/waiting"] = State(6, "/main/creating_behaviour/waiting", self)
        
        # state /main/creating_behaviour/creating
        self.states["/main/creating_behaviour/creating"] = State(7, "/main/creating_behaviour/creating", self)
        
        # state /main/deleting_behaviour
        self.states["/main/deleting_behaviour"] = State(8, "/main/deleting_behaviour", self)
        
        # state /main/deleting_behaviour/waiting
        self.states["/main/deleting_behaviour/waiting"] = State(9, "/main/deleting_behaviour/waiting", self)
        
        # state /main/deleting_behaviour/deleting
        self.states["/main/deleting_behaviour/deleting"] = State(10, "/main/deleting_behaviour/deleting", self)
        
        # state /stopped
        self.states["/stopped"] = State(11, "/stopped", self)
        self.states["/stopped"].setEnter(self._stopped_enter)
        
        # add children
        self.states[""].addChild(self.states["/main"])
        self.states[""].addChild(self.states["/stopped"])
        self.states["/main"].addChild(self.states["/main/main_behaviour"])
        self.states["/main"].addChild(self.states["/main/creating_behaviour"])
        self.states["/main"].addChild(self.states["/main/deleting_behaviour"])
        self.states["/main/main_behaviour"].addChild(self.states["/main/main_behaviour/initializing"])
        self.states["/main/main_behaviour"].addChild(self.states["/main/main_behaviour/running"])
        self.states["/main/creating_behaviour"].addChild(self.states["/main/creating_behaviour/waiting"])
        self.states["/main/creating_behaviour"].addChild(self.states["/main/creating_behaviour/creating"])
        self.states["/main/deleting_behaviour"].addChild(self.states["/main/deleting_behaviour/waiting"])
        self.states["/main/deleting_behaviour"].addChild(self.states["/main/deleting_behaviour/deleting"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/main"]
        self.states["/main/main_behaviour"].default_state = self.states["/main/main_behaviour/initializing"]
        self.states["/main/creating_behaviour"].default_state = self.states["/main/creating_behaviour/waiting"]
        self.states["/main/deleting_behaviour"].default_state = self.states["/main/deleting_behaviour/waiting"]
        
        # transition /main/main_behaviour/initializing
        _main_main_behaviour_initializing_0 = Transition(self, self.states["/main/main_behaviour/initializing"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_initializing_0.setTrigger(None)
        self.states["/main/main_behaviour/initializing"].addTransition(_main_main_behaviour_initializing_0)
        
        # transition /main/main_behaviour/running
        _main_main_behaviour_running_0 = Transition(self, self.states["/main/main_behaviour/running"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_running_0.setAction(self._main_main_behaviour_running_0_exec)
        _main_main_behaviour_running_0.setTrigger(Event("window_created", None))
        self.states["/main/main_behaviour/running"].addTransition(_main_main_behaviour_running_0)
        _main_main_behaviour_running_1 = Transition(self, self.states["/main/main_behaviour/running"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_running_1.setAction(self._main_main_behaviour_running_1_exec)
        _main_main_behaviour_running_1.setTrigger(Event("window_deleted", None))
        _main_main_behaviour_running_1.setGuard(self._main_main_behaviour_running_1_guard)
        self.states["/main/main_behaviour/running"].addTransition(_main_main_behaviour_running_1)
        _main_main_behaviour_running_2 = Transition(self, self.states["/main/main_behaviour/running"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_running_2.setAction(self._main_main_behaviour_running_2_exec)
        _main_main_behaviour_running_2.setTrigger(Event("window_deleted", None))
        _main_main_behaviour_running_2.setGuard(self._main_main_behaviour_running_2_guard)
        self.states["/main/main_behaviour/running"].addTransition(_main_main_behaviour_running_2)
        
        # transition /main/creating_behaviour/waiting
        _main_creating_behaviour_waiting_0 = Transition(self, self.states["/main/creating_behaviour/waiting"], [self.states["/main/creating_behaviour/creating"]])
        _main_creating_behaviour_waiting_0.setAction(self._main_creating_behaviour_waiting_0_exec)
        _main_creating_behaviour_waiting_0.setTrigger(Event("create_window", None))
        self.states["/main/creating_behaviour/waiting"].addTransition(_main_creating_behaviour_waiting_0)
        
        # transition /main/creating_behaviour/creating
        _main_creating_behaviour_creating_0 = Transition(self, self.states["/main/creating_behaviour/creating"], [self.states["/main/creating_behaviour/waiting"]])
        _main_creating_behaviour_creating_0.setAction(self._main_creating_behaviour_creating_0_exec)
        _main_creating_behaviour_creating_0.setTrigger(Event("instance_created", None))
        self.states["/main/creating_behaviour/creating"].addTransition(_main_creating_behaviour_creating_0)
        
        # transition /main/deleting_behaviour/waiting
        _main_deleting_behaviour_waiting_0 = Transition(self, self.states["/main/deleting_behaviour/waiting"], [self.states["/main/deleting_behaviour/deleting"]])
        _main_deleting_behaviour_waiting_0.setAction(self._main_deleting_behaviour_waiting_0_exec)
        _main_deleting_behaviour_waiting_0.setTrigger(Event("delete_window", None))
        self.states["/main/deleting_behaviour/waiting"].addTransition(_main_deleting_behaviour_waiting_0)
        
        # transition /main/deleting_behaviour/deleting
        _main_deleting_behaviour_deleting_0 = Transition(self, self.states["/main/deleting_behaviour/deleting"], [self.states["/main/deleting_behaviour/waiting"]])
        _main_deleting_behaviour_deleting_0.setAction(self._main_deleting_behaviour_deleting_0_exec)
        _main_deleting_behaviour_deleting_0.setTrigger(Event("instance_deleted", None))
        self.states["/main/deleting_behaviour/deleting"].addTransition(_main_deleting_behaviour_deleting_0)
        
        # transition /main
        _main_0 = Transition(self, self.states["/main"], [self.states["/stopped"]])
        _main_0.setTrigger(Event("stop", None))
        self.states["/main"].addTransition(_main_0)
    
    def _main_main_behaviour_initializing_enter(self):
        self.raiseInternalEvent(Event("create_window", None, []))
    
    def _stopped_enter(self):
        self.root.quit()
    
    def _main_main_behaviour_running_0_exec(self, parameters):
        self.nr_of_windows += 1
    
    def _main_main_behaviour_running_1_exec(self, parameters):
        self.nr_of_windows -= 1
    
    def _main_main_behaviour_running_1_guard(self, parameters):
        return self.nr_of_windows > 1
    
    def _main_main_behaviour_running_2_exec(self, parameters):
        self.raiseInternalEvent(Event("stop", None, []))
    
    def _main_main_behaviour_running_2_guard(self, parameters):
        return self.nr_of_windows == 1
    
    def _main_creating_behaviour_waiting_0_exec(self, parameters):
        self.big_step.outputEventOM(Event("create_instance", None, [self, 'windows']))
    
    def _main_creating_behaviour_creating_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, association_name, Event("set_association_name", None, [association_name])]))
        self.raiseInternalEvent(Event("window_created", None, []))
    
    def _main_deleting_behaviour_waiting_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEventOM(Event("delete_instance", None, [self, association_name]))
    
    def _main_deleting_behaviour_deleting_0_exec(self, parameters):
        self.raiseInternalEvent(Event("window_deleted", None, []))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/main"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class Window(RuntimeClassBase, tk.Toplevel, Widget):
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
        Window.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        tk.Toplevel.__init__(self)
        Widget.__init__(self, True)
        self.title('BouncingBalls')
        
        CANVAS_SIZE_TUPLE = (0, 0, self.winfo_screenwidth() * 2, self.winfo_screenheight() * 2)
        self.c = tk.Canvas(self, relief=tk.RIDGE, scrollregion=CANVAS_SIZE_TUPLE)
        
        self.set_bindable_and_tagorid(self.c)
    
    def user_defined_destructor(self):
        self.destroy()
        # call super class destructors
        if hasattr(tk.Toplevel, "__del__"):
            tk.Toplevel.__del__(self)
        if hasattr(Widget, "__del__"):
            Widget.__del__(self)
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /main
        self.states["/main"] = ParallelState(1, "/main", self)
        
        # state /main/main_behaviour
        self.states["/main/main_behaviour"] = State(2, "/main/main_behaviour", self)
        
        # state /main/main_behaviour/initializing
        self.states["/main/main_behaviour/initializing"] = State(3, "/main/main_behaviour/initializing", self)
        
        # state /main/main_behaviour/creating_button
        self.states["/main/main_behaviour/creating_button"] = State(4, "/main/main_behaviour/creating_button", self)
        
        # state /main/main_behaviour/packing_button
        self.states["/main/main_behaviour/packing_button"] = State(5, "/main/main_behaviour/packing_button", self)
        
        # state /main/main_behaviour/running
        self.states["/main/main_behaviour/running"] = State(6, "/main/main_behaviour/running", self)
        
        # state /main/main_behaviour/creating_ball
        self.states["/main/main_behaviour/creating_ball"] = State(7, "/main/main_behaviour/creating_ball", self)
        
        # state /stopped
        self.states["/stopped"] = State(8, "/stopped", self)
        self.states["/stopped"].setEnter(self._stopped_enter)
        
        # add children
        self.states[""].addChild(self.states["/main"])
        self.states[""].addChild(self.states["/stopped"])
        self.states["/main"].addChild(self.states["/main/main_behaviour"])
        self.states["/main/main_behaviour"].addChild(self.states["/main/main_behaviour/initializing"])
        self.states["/main/main_behaviour"].addChild(self.states["/main/main_behaviour/creating_button"])
        self.states["/main/main_behaviour"].addChild(self.states["/main/main_behaviour/packing_button"])
        self.states["/main/main_behaviour"].addChild(self.states["/main/main_behaviour/running"])
        self.states["/main/main_behaviour"].addChild(self.states["/main/main_behaviour/creating_ball"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/main"]
        self.states["/main/main_behaviour"].default_state = self.states["/main/main_behaviour/initializing"]
        
        # transition /main/main_behaviour/initializing
        _main_main_behaviour_initializing_0 = Transition(self, self.states["/main/main_behaviour/initializing"], [self.states["/main/main_behaviour/creating_button"]])
        _main_main_behaviour_initializing_0.setAction(self._main_main_behaviour_initializing_0_exec)
        _main_main_behaviour_initializing_0.setTrigger(Event("set_association_name", None))
        self.states["/main/main_behaviour/initializing"].addTransition(_main_main_behaviour_initializing_0)
        
        # transition /main/main_behaviour/creating_button
        _main_main_behaviour_creating_button_0 = Transition(self, self.states["/main/main_behaviour/creating_button"], [self.states["/main/main_behaviour/packing_button"]])
        _main_main_behaviour_creating_button_0.setAction(self._main_main_behaviour_creating_button_0_exec)
        _main_main_behaviour_creating_button_0.setTrigger(Event("instance_created", None))
        self.states["/main/main_behaviour/creating_button"].addTransition(_main_main_behaviour_creating_button_0)
        
        # transition /main/main_behaviour/packing_button
        _main_main_behaviour_packing_button_0 = Transition(self, self.states["/main/main_behaviour/packing_button"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_packing_button_0.setAction(self._main_main_behaviour_packing_button_0_exec)
        _main_main_behaviour_packing_button_0.setTrigger(Event("button_created", None))
        self.states["/main/main_behaviour/packing_button"].addTransition(_main_main_behaviour_packing_button_0)
        
        # transition /main/main_behaviour/running
        _main_main_behaviour_running_0 = Transition(self, self.states["/main/main_behaviour/running"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_running_0.setAction(self._main_main_behaviour_running_0_exec)
        _main_main_behaviour_running_0.setTrigger(Event("window-close", self.getInPortName("input")))
        _main_main_behaviour_running_0.setGuard(self._main_main_behaviour_running_0_guard)
        self.states["/main/main_behaviour/running"].addTransition(_main_main_behaviour_running_0)
        _main_main_behaviour_running_1 = Transition(self, self.states["/main/main_behaviour/running"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_running_1.setAction(self._main_main_behaviour_running_1_exec)
        _main_main_behaviour_running_1.setTrigger(Event("button_pressed", None))
        _main_main_behaviour_running_1.setGuard(self._main_main_behaviour_running_1_guard)
        self.states["/main/main_behaviour/running"].addTransition(_main_main_behaviour_running_1)
        _main_main_behaviour_running_2 = Transition(self, self.states["/main/main_behaviour/running"], [self.states["/main/main_behaviour/creating_ball"]])
        _main_main_behaviour_running_2.setAction(self._main_main_behaviour_running_2_exec)
        _main_main_behaviour_running_2.setTrigger(Event("right-click", self.getInPortName("input")))
        _main_main_behaviour_running_2.setGuard(self._main_main_behaviour_running_2_guard)
        self.states["/main/main_behaviour/running"].addTransition(_main_main_behaviour_running_2)
        _main_main_behaviour_running_3 = Transition(self, self.states["/main/main_behaviour/running"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_running_3.setAction(self._main_main_behaviour_running_3_exec)
        _main_main_behaviour_running_3.setTrigger(Event("delete_ball", None))
        self.states["/main/main_behaviour/running"].addTransition(_main_main_behaviour_running_3)
        
        # transition /main/main_behaviour/creating_ball
        _main_main_behaviour_creating_ball_0 = Transition(self, self.states["/main/main_behaviour/creating_ball"], [self.states["/main/main_behaviour/running"]])
        _main_main_behaviour_creating_ball_0.setAction(self._main_main_behaviour_creating_ball_0_exec)
        _main_main_behaviour_creating_ball_0.setTrigger(Event("instance_created", None))
        self.states["/main/main_behaviour/creating_ball"].addTransition(_main_main_behaviour_creating_ball_0)
        
        # transition /main
        _main_0 = Transition(self, self.states["/main"], [self.states["/stopped"]])
        _main_0.setAction(self._main_0_exec)
        _main_0.setTrigger(Event("stop", None))
        self.states["/main"].addTransition(_main_0)
    
    def _stopped_enter(self):
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, 'parent', Event("delete_window", None, [self.association_name])]))
    
    def _main_0_exec(self, parameters):
        self.big_step.outputEventOM(Event("delete_instance", None, [self, 'buttons']))
        self.big_step.outputEventOM(Event("delete_instance", None, [self, 'balls']))
    
    def _main_main_behaviour_initializing_0_exec(self, parameters):
        association_name = parameters[0]
        self.association_name = association_name
        self.big_step.outputEventOM(Event("create_instance", None, [self, 'buttons', 'Button', self, 'create_window', 'Create Window']))
    
    def _main_main_behaviour_creating_button_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
    
    def _main_main_behaviour_packing_button_0_exec(self, parameters):
        button = parameters[0]
        button.pack(expand=False, fill=tk.X, side=tk.TOP)
        self.c.focus_force()
        self.c.pack(expand=True, fill=tk.BOTH)
    
    def _main_main_behaviour_running_0_exec(self, parameters):
        tagorid = parameters[0]
        self.raiseInternalEvent(Event("stop", None, []))
    
    def _main_main_behaviour_running_0_guard(self, parameters):
        tagorid = parameters[0]
        return tagorid == id(self)
    
    def _main_main_behaviour_running_1_exec(self, parameters):
        event_name = parameters[0]
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, 'parent', Event("create_window", None, [])]))
    
    def _main_main_behaviour_running_1_guard(self, parameters):
        event_name = parameters[0]
        return event_name == 'create_window'
    
    def _main_main_behaviour_running_2_exec(self, parameters):
        tagorid = parameters[0]
        self.big_step.outputEventOM(Event("create_instance", None, [self, "balls", "Ball", self.c, self.last_x, self.last_y]))
    
    def _main_main_behaviour_running_2_guard(self, parameters):
        tagorid = parameters[0]
        return tagorid == id(self)
    
    def _main_main_behaviour_running_3_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEventOM(Event("delete_instance", None, [self, association_name]))
    
    def _main_main_behaviour_creating_ball_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, association_name, Event("set_association_name", None, [association_name])]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/main"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class Button(RuntimeClassBase, tk.Button, Widget):
    def __init__(self, controller, parent, event_name, button_text):
        RuntimeClassBase.__init__(self, controller)
        
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        Button.user_defined_constructor(self, parent, event_name, button_text)
    
    def user_defined_constructor(self, parent, event_name, button_text):
        tk.Button.__init__(self, parent, **{'text': button_text})
        Widget.__init__(self)
        self.event_name = event_name
    
    def user_defined_destructor(self):
        self.destroy()
        # call super class destructors
        if hasattr(tk.Button, "__del__"):
            tk.Button.__del__(self)
        if hasattr(Widget, "__del__"):
            Widget.__del__(self)
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /initializing
        self.states["/initializing"] = State(1, "/initializing", self)
        self.states["/initializing"].setEnter(self._initializing_enter)
        
        # state /running
        self.states["/running"] = State(2, "/running", self)
        
        # add children
        self.states[""].addChild(self.states["/initializing"])
        self.states[""].addChild(self.states["/running"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/initializing"]
        
        # transition /initializing
        _initializing_0 = Transition(self, self.states["/initializing"], [self.states["/running"]])
        _initializing_0.setTrigger(None)
        self.states["/initializing"].addTransition(_initializing_0)
        
        # transition /running
        _running_0 = Transition(self, self.states["/running"], [self.states["/running"]])
        _running_0.setAction(self._running_0_exec)
        _running_0.setTrigger(Event("left-click", self.getInPortName("input")))
        _running_0.setGuard(self._running_0_guard)
        self.states["/running"].addTransition(_running_0)
    
    def _initializing_enter(self):
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, 'parent', Event("button_created", None, [self])]))
    
    def _running_0_exec(self, parameters):
        tagorid = parameters[0]
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, 'parent', Event("button_pressed", None, [self.event_name])]))
    
    def _running_0_guard(self, parameters):
        tagorid = parameters[0]
        return tagorid == id(self)
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/initializing"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class Ball(RuntimeClassBase, Widget):
    def __init__(self, controller, canvas, x, y):
        RuntimeClassBase.__init__(self, controller)
        
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # user defined attributes
        self.canvas = None
        
        # call user defined constructor
        Ball.user_defined_constructor(self, canvas, x, y)
    
    def user_defined_constructor(self, canvas, x, y):
        Widget.__init__(self, True)
        self.canvas = canvas
        self.r = 20.0;
        self.vel = {'x': random.uniform(-5.0, 5.0), 'y': random.uniform(-5.0, 5.0)};
        self.smooth = 0.4 # value between 0 and 1
        self.id = self.canvas.create_oval(x, y, x + (self.r * 2), y + (self.r * 2), fill="black")
        self.set_bindable_and_tagorid(self.canvas, self.id)
    
    def user_defined_destructor(self):
        self.canvas.delete(self.id)
        # call super class destructors
        if hasattr(Widget, "__del__"):
            Widget.__del__(self)
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /initializing
        self.states["/initializing"] = State(1, "/initializing", self)
        
        # state /bouncing
        self.states["/bouncing"] = State(2, "/bouncing", self)
        self.states["/bouncing"].setEnter(self._bouncing_enter)
        self.states["/bouncing"].setExit(self._bouncing_exit)
        
        # state /dragging
        self.states["/dragging"] = State(3, "/dragging", self)
        
        # state /selected
        self.states["/selected"] = State(4, "/selected", self)
        
        # state /deleted
        self.states["/deleted"] = State(5, "/deleted", self)
        
        # add children
        self.states[""].addChild(self.states["/initializing"])
        self.states[""].addChild(self.states["/bouncing"])
        self.states[""].addChild(self.states["/dragging"])
        self.states[""].addChild(self.states["/selected"])
        self.states[""].addChild(self.states["/deleted"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/initializing"]
        
        # transition /initializing
        _initializing_0 = Transition(self, self.states["/initializing"], [self.states["/bouncing"]])
        _initializing_0.setAction(self._initializing_0_exec)
        _initializing_0.setTrigger(Event("set_association_name", None))
        self.states["/initializing"].addTransition(_initializing_0)
        
        # transition /bouncing
        _bouncing_0 = Transition(self, self.states["/bouncing"], [self.states["/bouncing"]])
        _bouncing_0.setAction(self._bouncing_0_exec)
        _bouncing_0.setTrigger(Event("_0after"))
        self.states["/bouncing"].addTransition(_bouncing_0)
        _bouncing_1 = Transition(self, self.states["/bouncing"], [self.states["/selected"]])
        _bouncing_1.setAction(self._bouncing_1_exec)
        _bouncing_1.setTrigger(Event("left-click", self.getInPortName("input")))
        _bouncing_1.setGuard(self._bouncing_1_guard)
        self.states["/bouncing"].addTransition(_bouncing_1)
        
        # transition /dragging
        _dragging_0 = Transition(self, self.states["/dragging"], [self.states["/dragging"]])
        _dragging_0.setAction(self._dragging_0_exec)
        _dragging_0.setTrigger(Event("motion", self.getInPortName("input")))
        self.states["/dragging"].addTransition(_dragging_0)
        _dragging_1 = Transition(self, self.states["/dragging"], [self.states["/bouncing"]])
        _dragging_1.setAction(self._dragging_1_exec)
        _dragging_1.setTrigger(Event("left-release", self.getInPortName("input")))
        self.states["/dragging"].addTransition(_dragging_1)
        
        # transition /selected
        _selected_0 = Transition(self, self.states["/selected"], [self.states["/dragging"]])
        _selected_0.setTrigger(Event("left-click", self.getInPortName("input")))
        _selected_0.setGuard(self._selected_0_guard)
        self.states["/selected"].addTransition(_selected_0)
        _selected_1 = Transition(self, self.states["/selected"], [self.states["/deleted"]])
        _selected_1.setAction(self._selected_1_exec)
        _selected_1.setTrigger(Event("delete", self.getInPortName("input")))
        self.states["/selected"].addTransition(_selected_1)
    
    def _bouncing_enter(self):
        self.addTimer(0, (20 - self.getSimulatedTime() % 20) / 1000.0)
    
    def _bouncing_exit(self):
        self.removeTimer(0)
    
    def _initializing_0_exec(self, parameters):
        association_name = parameters[0]
        self.association_name = association_name
    
    def _bouncing_0_exec(self, parameters):
        pos = self.canvas.coords(self.id)
        x = self.canvas.canvasx(pos[0])
        y = self.canvas.canvasy(pos[1])
        if x <= 0 or x + (self.r * 2) >= self.canvas.canvasx(self.canvas.winfo_width()):
            self.vel['x'] = -self.vel['x']
        if y <= 0 or y + (self.r * 2) >= self.canvas.canvasy(self.canvas.winfo_height()):
            self.vel['y'] = -self.vel['y']
        self.canvas.move(self.id, self.vel['x'], self.vel['y']);
    
    def _bouncing_1_exec(self, parameters):
        tagorid = parameters[0]
        self.canvas.itemconfig(self.id, fill="yellow")
    
    def _bouncing_1_guard(self, parameters):
        tagorid = parameters[0]
        return tagorid == id(self)
    
    def _dragging_0_exec(self, parameters):
        tagorid = parameters[0]
        coords = self.canvas.coords(self.id)
        dx = self.canvas.canvasx(self.last_x) - self.canvas.canvasx(coords[0])
        dy = self.canvas.canvasx(self.last_y) - self.canvas.canvasy(coords[1])
        
        self.canvas.move(self.id, dx, dy);
        
        # keep ball within boundaries
        coords = self.canvas.coords(self.id)
        x = self.canvas.canvasx(coords[0])
        y = self.canvas.canvasy(coords[1])
        if x - self.r <= 0:
            x = 1;
        elif x + self.r >= self.canvas.winfo_width():
            x = self.canvas.winfo_width() - (2 * self.r) - 1
        if y - self.r <= 0:
            y = 1
        elif y + self.r >= self.canvas.winfo_height():
            y = self.canvas.winfo_height() - (2 * self.r) - 1;
        self.canvas.coords(self.id, x, y, x + (self.r * 2), y + (self.r * 2));
        self.vel = {
            'x': (1 - self.smooth) * dx + self.smooth * self.vel['x'],
            'y': (1 - self.smooth) * dy + self.smooth * self.vel['y']
        }
    
    def _dragging_1_exec(self, parameters):
        tagorid = parameters[0]
        self.canvas.itemconfig(self.id, fill="red")
    
    def _selected_0_guard(self, parameters):
        tagorid = parameters[0]
        return tagorid == id(self)
    
    def _selected_1_exec(self, parameters):
        tagorid = parameters[0]
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, 'parent', Event("delete_ball", None, [self.association_name])]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/initializing"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "MainApp":
            instance = MainApp(self.controller, construct_params[0])
            instance.associations = {}
            instance.associations["windows"] = Association("Window", 0, -1)
        elif class_name == "Window":
            instance = Window(self.controller)
            instance.associations = {}
            instance.associations["parent"] = Association("MainApp", 1, 1)
            instance.associations["buttons"] = Association("Button", 0, -1)
            instance.associations["balls"] = Association("Ball", 0, -1)
        elif class_name == "Button":
            instance = Button(self.controller, construct_params[0], construct_params[1], construct_params[2])
            instance.associations = {}
            instance.associations["parent"] = Association("Field", 1, 1)
        elif class_name == "Ball":
            instance = Ball(self.controller, construct_params[0], construct_params[1], construct_params[2])
            instance.associations = {}
            instance.associations["parent"] = Association("Window", 1, 1)
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class Controller(EventLoopControllerBase):
    def __init__(self, root, event_loop_callbacks, finished_callback = None, behind_schedule_callback = None):
        if finished_callback == None: finished_callback = None
        if behind_schedule_callback == None: behind_schedule_callback = None
        EventLoopControllerBase.__init__(self, ObjectManager(self), event_loop_callbacks, finished_callback, behind_schedule_callback)
        self.addInputPort("input")
        self.object_manager.createInstance("MainApp", [root])