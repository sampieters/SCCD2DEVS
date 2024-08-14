"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Model author: Sam Pieters
Model name:   TrafficLight
Model description:
Tkinter frame with Traffic light in a single statechart.
"""

from sccd.runtime.statecharts_core import *
from sccd.runtime.libs import ui_v2 as ui
CANVAS_DIMS = (100, 350)
CANVAS_WIDTH = 100
CANVAS_HEIGHT = 350

# package "TrafficLight"

class MainApp(RuntimeClassBase):
    def __init__(self, controller):
        RuntimeClassBase.__init__(self, controller)
        
        self.inports["field_ui"] = controller.addInputPort("field_ui", self)
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # user defined attributes
        self.window_id = None
        self.canvas_id = None
        self.green_id = None
        self.yellow_id = None
        self.red_id = None
        self.police_button_id = None
        
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
        
        # state /creating_window
        self.states["/creating_window"] = State(1, "/creating_window", self)
        self.states["/creating_window"].setEnter(self._creating_window_enter)
        
        # state /creating_canvas
        self.states["/creating_canvas"] = State(2, "/creating_canvas", self)
        self.states["/creating_canvas"].setEnter(self._creating_canvas_enter)
        
        # state /creating_trafficlight
        self.states["/creating_trafficlight"] = State(3, "/creating_trafficlight", self)
        
        # state /creating_trafficlight/creating_greenlight
        self.states["/creating_trafficlight/creating_greenlight"] = State(4, "/creating_trafficlight/creating_greenlight", self)
        self.states["/creating_trafficlight/creating_greenlight"].setEnter(self._creating_trafficlight_creating_greenlight_enter)
        
        # state /creating_trafficlight/creating_yellowlight
        self.states["/creating_trafficlight/creating_yellowlight"] = State(5, "/creating_trafficlight/creating_yellowlight", self)
        self.states["/creating_trafficlight/creating_yellowlight"].setEnter(self._creating_trafficlight_creating_yellowlight_enter)
        
        # state /creating_trafficlight/creating_redlight
        self.states["/creating_trafficlight/creating_redlight"] = State(6, "/creating_trafficlight/creating_redlight", self)
        self.states["/creating_trafficlight/creating_redlight"].setEnter(self._creating_trafficlight_creating_redlight_enter)
        
        # state /creating_interrupt_button
        self.states["/creating_interrupt_button"] = State(7, "/creating_interrupt_button", self)
        self.states["/creating_interrupt_button"].setEnter(self._creating_interrupt_button_enter)
        
        # state /creating_quit_button
        self.states["/creating_quit_button"] = State(8, "/creating_quit_button", self)
        self.states["/creating_quit_button"].setEnter(self._creating_quit_button_enter)
        
        # state /on
        self.states["/on"] = State(9, "/on", self)
        
        # state /on/normal
        self.states["/on/normal"] = State(10, "/on/normal", self)
        
        # state /on/normal/red
        self.states["/on/normal/red"] = State(11, "/on/normal/red", self)
        self.states["/on/normal/red"].setEnter(self._on_normal_red_enter)
        self.states["/on/normal/red"].setExit(self._on_normal_red_exit)
        
        # state /on/normal/green
        self.states["/on/normal/green"] = State(12, "/on/normal/green", self)
        self.states["/on/normal/green"].setEnter(self._on_normal_green_enter)
        self.states["/on/normal/green"].setExit(self._on_normal_green_exit)
        
        # state /on/normal/yellow
        self.states["/on/normal/yellow"] = State(13, "/on/normal/yellow", self)
        self.states["/on/normal/yellow"].setEnter(self._on_normal_yellow_enter)
        self.states["/on/normal/yellow"].setExit(self._on_normal_yellow_exit)
        
        # state /on/normal/history
        self.states["/on/normal/history"] = ShallowHistoryState(14, "/on/normal/history", self)
        
        # state /on/interrupted
        self.states["/on/interrupted"] = State(15, "/on/interrupted", self)
        
        # state /on/interrupted/yellow
        self.states["/on/interrupted/yellow"] = State(16, "/on/interrupted/yellow", self)
        self.states["/on/interrupted/yellow"].setEnter(self._on_interrupted_yellow_enter)
        self.states["/on/interrupted/yellow"].setExit(self._on_interrupted_yellow_exit)
        
        # state /on/interrupted/black
        self.states["/on/interrupted/black"] = State(17, "/on/interrupted/black", self)
        self.states["/on/interrupted/black"].setEnter(self._on_interrupted_black_enter)
        self.states["/on/interrupted/black"].setExit(self._on_interrupted_black_exit)
        
        # state /off
        self.states["/off"] = State(18, "/off", self)
        self.states["/off"].setEnter(self._off_enter)
        
        # state /deleted
        self.states["/deleted"] = State(19, "/deleted", self)
        
        # add children
        self.states[""].addChild(self.states["/creating_window"])
        self.states[""].addChild(self.states["/creating_canvas"])
        self.states[""].addChild(self.states["/creating_trafficlight"])
        self.states[""].addChild(self.states["/creating_interrupt_button"])
        self.states[""].addChild(self.states["/creating_quit_button"])
        self.states[""].addChild(self.states["/on"])
        self.states[""].addChild(self.states["/off"])
        self.states[""].addChild(self.states["/deleted"])
        self.states["/creating_trafficlight"].addChild(self.states["/creating_trafficlight/creating_greenlight"])
        self.states["/creating_trafficlight"].addChild(self.states["/creating_trafficlight/creating_yellowlight"])
        self.states["/creating_trafficlight"].addChild(self.states["/creating_trafficlight/creating_redlight"])
        self.states["/on"].addChild(self.states["/on/normal"])
        self.states["/on"].addChild(self.states["/on/interrupted"])
        self.states["/on/normal"].addChild(self.states["/on/normal/red"])
        self.states["/on/normal"].addChild(self.states["/on/normal/green"])
        self.states["/on/normal"].addChild(self.states["/on/normal/yellow"])
        self.states["/on/normal"].addChild(self.states["/on/normal/history"])
        self.states["/on/interrupted"].addChild(self.states["/on/interrupted/yellow"])
        self.states["/on/interrupted"].addChild(self.states["/on/interrupted/black"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/creating_window"]
        self.states["/creating_trafficlight"].default_state = self.states["/creating_trafficlight/creating_greenlight"]
        self.states["/on"].default_state = self.states["/on/normal"]
        self.states["/on/normal"].default_state = self.states["/on/normal/red"]
        self.states["/on/interrupted"].default_state = self.states["/on/interrupted/yellow"]
        
        # transition /creating_window
        _creating_window_0 = Transition(self, self.states["/creating_window"], [self.states["/creating_canvas"]])
        _creating_window_0.setAction(self._creating_window_0_exec)
        _creating_window_0.setTrigger(Event("window_created", None))
        self.states["/creating_window"].addTransition(_creating_window_0)
        
        # transition /creating_canvas
        _creating_canvas_0 = Transition(self, self.states["/creating_canvas"], [self.states["/creating_trafficlight"]])
        _creating_canvas_0.setAction(self._creating_canvas_0_exec)
        _creating_canvas_0.setTrigger(Event("canvas_created", None))
        self.states["/creating_canvas"].addTransition(_creating_canvas_0)
        
        # transition /creating_trafficlight/creating_greenlight
        _creating_trafficlight_creating_greenlight_0 = Transition(self, self.states["/creating_trafficlight/creating_greenlight"], [self.states["/creating_trafficlight/creating_yellowlight"]])
        _creating_trafficlight_creating_greenlight_0.setAction(self._creating_trafficlight_creating_greenlight_0_exec)
        _creating_trafficlight_creating_greenlight_0.setTrigger(Event("rectangle_created", None))
        self.states["/creating_trafficlight/creating_greenlight"].addTransition(_creating_trafficlight_creating_greenlight_0)
        
        # transition /creating_trafficlight/creating_yellowlight
        _creating_trafficlight_creating_yellowlight_0 = Transition(self, self.states["/creating_trafficlight/creating_yellowlight"], [self.states["/creating_trafficlight/creating_redlight"]])
        _creating_trafficlight_creating_yellowlight_0.setAction(self._creating_trafficlight_creating_yellowlight_0_exec)
        _creating_trafficlight_creating_yellowlight_0.setTrigger(Event("rectangle_created", None))
        self.states["/creating_trafficlight/creating_yellowlight"].addTransition(_creating_trafficlight_creating_yellowlight_0)
        
        # transition /creating_trafficlight/creating_redlight
        _creating_trafficlight_creating_redlight_0 = Transition(self, self.states["/creating_trafficlight/creating_redlight"], [self.states["/creating_interrupt_button"]])
        _creating_trafficlight_creating_redlight_0.setAction(self._creating_trafficlight_creating_redlight_0_exec)
        _creating_trafficlight_creating_redlight_0.setTrigger(Event("rectangle_created", None))
        self.states["/creating_trafficlight/creating_redlight"].addTransition(_creating_trafficlight_creating_redlight_0)
        
        # transition /creating_interrupt_button
        _creating_interrupt_button_0 = Transition(self, self.states["/creating_interrupt_button"], [self.states["/creating_quit_button"]])
        _creating_interrupt_button_0.setAction(self._creating_interrupt_button_0_exec)
        _creating_interrupt_button_0.setTrigger(Event("button_created", None))
        self.states["/creating_interrupt_button"].addTransition(_creating_interrupt_button_0)
        
        # transition /creating_quit_button
        _creating_quit_button_0 = Transition(self, self.states["/creating_quit_button"], [self.states["/on"]])
        _creating_quit_button_0.setAction(self._creating_quit_button_0_exec)
        _creating_quit_button_0.setTrigger(Event("button_created", None))
        self.states["/creating_quit_button"].addTransition(_creating_quit_button_0)
        
        # transition /on/normal/red
        _on_normal_red_0 = Transition(self, self.states["/on/normal/red"], [self.states["/on/normal/green"]])
        _on_normal_red_0.setTrigger(Event("_0after"))
        self.states["/on/normal/red"].addTransition(_on_normal_red_0)
        
        # transition /on/normal/green
        _on_normal_green_0 = Transition(self, self.states["/on/normal/green"], [self.states["/on/normal/yellow"]])
        _on_normal_green_0.setTrigger(Event("_1after"))
        self.states["/on/normal/green"].addTransition(_on_normal_green_0)
        
        # transition /on/normal/yellow
        _on_normal_yellow_0 = Transition(self, self.states["/on/normal/yellow"], [self.states["/on/normal/red"]])
        _on_normal_yellow_0.setTrigger(Event("_2after"))
        self.states["/on/normal/yellow"].addTransition(_on_normal_yellow_0)
        
        # transition /on/interrupted/yellow
        _on_interrupted_yellow_0 = Transition(self, self.states["/on/interrupted/yellow"], [self.states["/on/interrupted/black"]])
        _on_interrupted_yellow_0.setTrigger(Event("_3after"))
        self.states["/on/interrupted/yellow"].addTransition(_on_interrupted_yellow_0)
        
        # transition /on/interrupted/black
        _on_interrupted_black_0 = Transition(self, self.states["/on/interrupted/black"], [self.states["/on/interrupted/yellow"]])
        _on_interrupted_black_0.setTrigger(Event("_4after"))
        self.states["/on/interrupted/black"].addTransition(_on_interrupted_black_0)
        
        # transition /on/normal
        _on_normal_0 = Transition(self, self.states["/on/normal"], [self.states["/deleted"]])
        _on_normal_0.setAction(self._on_normal_0_exec)
        _on_normal_0.setTrigger(Event("window_close", self.getInPortName("field_ui")))
        self.states["/on/normal"].addTransition(_on_normal_0)
        _on_normal_1 = Transition(self, self.states["/on/normal"], [self.states["/off"]])
        _on_normal_1.setTrigger(Event("quit_clicked", self.getInPortName("field_ui")))
        _on_normal_1.setGuard(self._on_normal_1_guard)
        self.states["/on/normal"].addTransition(_on_normal_1)
        _on_normal_2 = Transition(self, self.states["/on/normal"], [self.states["/on/interrupted"]])
        _on_normal_2.setAction(self._on_normal_2_exec)
        _on_normal_2.setTrigger(Event("interrupt_clicked", self.getInPortName("field_ui")))
        _on_normal_2.setGuard(self._on_normal_2_guard)
        self.states["/on/normal"].addTransition(_on_normal_2)
        
        # transition /on/interrupted
        _on_interrupted_0 = Transition(self, self.states["/on/interrupted"], [self.states["/on/normal/history"]])
        _on_interrupted_0.setTrigger(Event("interrupt_clicked", self.getInPortName("field_ui")))
        _on_interrupted_0.setGuard(self._on_interrupted_0_guard)
        self.states["/on/interrupted"].addTransition(_on_interrupted_0)
    
    def _creating_window_enter(self):
        self.big_step.outputEvent(Event("create_window", self.getOutPortName("ui"), [CANVAS_DIMS[0], CANVAS_DIMS[1], "Fixed Traffic Light", self.inports['field_ui']]))
    
    def _creating_canvas_enter(self):
        self.big_step.outputEvent(Event("create_canvas", self.getOutPortName("ui"), [self.window_id, CANVAS_DIMS[0], CANVAS_DIMS[1] - 100, {'background':'#222222'}, self.inports['field_ui']]))
    
    def _creating_trafficlight_creating_greenlight_enter(self):
        self.big_step.outputEvent(Event("create_rectangle", self.getOutPortName("ui"), [self.canvas_id, 50, 50, 50, 50, {'fill':'#000'}, self.inports['field_ui']]))
    
    def _creating_trafficlight_creating_yellowlight_enter(self):
        self.big_step.outputEvent(Event("create_rectangle", self.getOutPortName("ui"), [self.canvas_id, 50, 110, 50, 50, {'fill':'#000'}, self.inports['field_ui']]))
    
    def _creating_trafficlight_creating_redlight_enter(self):
        self.big_step.outputEvent(Event("create_rectangle", self.getOutPortName("ui"), [self.canvas_id, 50, 170, 50, 50, {'fill':'#000'}, self.inports['field_ui']]))
    
    def _creating_interrupt_button_enter(self):
        self.big_step.outputEvent(Event("create_button", self.getOutPortName("ui"), [self.window_id, 'Police Interrupt', self.inports['field_ui']]))
    
    def _creating_quit_button_enter(self):
        self.big_step.outputEvent(Event("create_button", self.getOutPortName("ui"), [self.window_id, 'Quit', self.inports['field_ui']]))
    
    def _on_normal_red_enter(self):
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.yellow_id, 'black']))
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.red_id, 'red']))
        self.addTimer(0, 3)
    
    def _on_normal_red_exit(self):
        self.removeTimer(0)
    
    def _on_normal_green_enter(self):
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.red_id, 'black']))
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.green_id, 'green']))
        self.addTimer(1, 2)
    
    def _on_normal_green_exit(self):
        self.removeTimer(1)
    
    def _on_normal_yellow_enter(self):
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.green_id, 'black']))
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.yellow_id, 'yellow']))
        self.addTimer(2, 1)
    
    def _on_normal_yellow_exit(self):
        self.removeTimer(2)
    
    def _on_interrupted_yellow_enter(self):
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.yellow_id, 'yellow']))
        self.addTimer(3, .5)
    
    def _on_interrupted_yellow_exit(self):
        self.removeTimer(3)
    
    def _on_interrupted_black_enter(self):
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.yellow_id, 'black']))
        self.addTimer(4, .5)
    
    def _on_interrupted_black_exit(self):
        self.removeTimer(4)
    
    def _off_enter(self):
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.green_id, 'black']))
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.yellow_id, 'black']))
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.red_id, 'black']))
    
    def _on_normal_0_exec(self, parameters):
        self.big_step.outputEvent(Event("destroy_all", self.getOutPortName("ui"), []))
    
    def _on_normal_1_guard(self, parameters):
        x = parameters[0]
        y = parameters[1]
        button = parameters[2]
        return button == ui.MOUSE_BUTTONS.LEFT
    
    def _on_normal_2_exec(self, parameters):
        x = parameters[0]
        y = parameters[1]
        button = parameters[2]
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.green_id, 'black']))
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.yellow_id, 'black']))
        self.big_step.outputEvent(Event("set_element_color", self.getOutPortName("ui"), [self.canvas_id, self.red_id, 'black']))
    
    def _on_normal_2_guard(self, parameters):
        x = parameters[0]
        y = parameters[1]
        button = parameters[2]
        return button == ui.MOUSE_BUTTONS.LEFT
    
    def _on_interrupted_0_guard(self, parameters):
        x = parameters[0]
        y = parameters[1]
        button = parameters[2]
        return button == ui.MOUSE_BUTTONS.LEFT
    
    def _creating_window_0_exec(self, parameters):
        window_id = parameters[0]
        self.window_id = window_id
        self.big_step.outputEvent(Event("bind_event", self.getOutPortName("ui"), [window_id, ui.EVENTS.WINDOW_CLOSE, 'window_close', self.inports['field_ui']]))
    
    def _creating_canvas_0_exec(self, parameters):
        canvas_id = parameters[0]
        self.canvas_id = canvas_id
    
    def _creating_trafficlight_creating_greenlight_0_exec(self, parameters):
        canvas_id = parameters[0]
        green_id = parameters[1]
        self.green_id = green_id
    
    def _creating_trafficlight_creating_yellowlight_0_exec(self, parameters):
        canvas_id = parameters[0]
        yellow_id = parameters[1]
        self.yellow_id = yellow_id
    
    def _creating_trafficlight_creating_redlight_0_exec(self, parameters):
        canvas_id = parameters[0]
        red_id = parameters[1]
        self.red_id = red_id
    
    def _creating_interrupt_button_0_exec(self, parameters):
        button_id = parameters[0]
        self.police_button_id = button_id
        self.big_step.outputEvent(Event("bind_event", self.getOutPortName("ui"), [button_id, ui.EVENTS.MOUSE_CLICK, "interrupt_clicked", self.inports['field_ui']]))
    
    def _creating_quit_button_0_exec(self, parameters):
        button_id = parameters[0]
        self.quit_button_id = button_id
        self.big_step.outputEvent(Event("bind_event", self.getOutPortName("ui"), [button_id, ui.EVENTS.MOUSE_CLICK, "quit_clicked", self.inports['field_ui']]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/creating_window"].getEffectiveTargetStates()
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

class Controller(EventLoopControllerBase):
    def __init__(self, event_loop_callbacks, finished_callback = None, behind_schedule_callback = None):
        if finished_callback == None: finished_callback = None
        if behind_schedule_callback == None: behind_schedule_callback = None
        EventLoopControllerBase.__init__(self, ObjectManager(self), event_loop_callbacks, finished_callback, behind_schedule_callback)
        self.addInputPort("ui")
        self.addOutputPort("ui")
        self.object_manager.createInstance("MainApp", [])