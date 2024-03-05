"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration) and Sam Pieters (DEVS)

Model author: Raphael Mannadiar
Model name:   Traffic_Light_Python_Version

"""

from sccd.runtime.DEVS_statecharts_core import *
from pypdevs.DEVS import *
from pypdevs.infinity import *
from pypdevs.simulator import *
from sccd.runtime.libs.ui import ui

# package "Traffic_Light_Python_Version"

class MainAppInstance(RuntimeClassBase):
    def __init__(self, atomdevs):
        RuntimeClassBase.__init__(self, atomdevs)
        self.associations = {}
        self.associations["trafficlight"] = Association("TrafficLight", 0, -1)
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        MainAppInstance.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        self.canvas   = ui.append_canvas(ui.window,100,310,{'background':'#eee'});
        police_button = ui.append_button(ui.window, 'Police interrupt');
        quit_button   = ui.append_button(ui.window, 'Quit');
        ui.bind_event(police_button.element, ui.EVENTS.MOUSE_CLICK, self.controller, 'police_interrupt_clicked');
        ui.bind_event(quit_button.element, ui.EVENTS.MOUSE_CLICK, self.controller, 'quit_clicked');
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /initializing
        self.states["/initializing"] = State(1, "/initializing", self)
        
        # state /creating
        self.states["/creating"] = State(2, "/creating", self)
        
        # state /initialized
        self.states["/initialized"] = State(3, "/initialized", self)
        
        # add children
        self.states[""].addChild(self.states["/initializing"])
        self.states[""].addChild(self.states["/creating"])
        self.states[""].addChild(self.states["/initialized"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/initializing"]
        
        # transition /initializing
        _initializing_0 = Transition(self, self.states["/initializing"], [self.states["/creating"]])
        _initializing_0.setAction(self._initializing_0_exec)
        _initializing_0.setTrigger(None)
        self.states["/initializing"].addTransition(_initializing_0)
        
        # transition /creating
        _creating_0 = Transition(self, self.states["/creating"], [self.states["/initialized"]])
        _creating_0.setAction(self._creating_0_exec)
        _creating_0.setTrigger(Event("instance_created", None))
        self.states["/creating"].addTransition(_creating_0)
    
    def _initializing_0_exec(self, parameters):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "trafficlight", "TrafficLight", self.canvas]))
    
    def _creating_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEventOM(Event("start_instance", None, [self, association_name]))
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, association_name, Event("set_association_name", None, [association_name])]))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/initializing"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class MainApp(AtomicDEVS, ObjectManagerBase):
    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        ObjectManagerBase.__init__(self)
        self.elapsed = 0
        self.obj_manager_in = self.addInPort("obj_manager_in")
        self.obj_manager_out = self.addOutPort("obj_manager_out")
        self.input = self.addInPort("input")
        self.outputs = {}
        self.outputs["trafficlight"] = self.addOutPort("trafficlight")
        self.obj_manager_in = self.addInPort("obj_manager_in")
        self.input = self.addInPort("input")
        self.instances.add(MainAppInstance(self))

        self.name = "MainApp"
    
    def extTransition(self, inputs):
        self.simulated_time = (self.simulated_time + self.elapsed)
        all_inputs = []
        if self.obj_manager_in in inputs:
            all_inputs.extend(inputs[self.obj_manager_in])
        if self.input in inputs:
            all_inputs.extend(inputs[self.input])
        for input in all_inputs:
            if isinstance(input, str):
                tem = eval(input)
                self.addInput(tem)
            if input[3].name == "create_instance":
                self.instances.add(MainAppInstance(self))
                ev = Event("instance_created", None, parameters=[f"{input[0]}[{len(self.instances)-1}]"])
                self.to_send.append(("MainApp", TODO, input[2], ev))
            elif input[3].name == "start_instance":
                instance = list(self.instances)[input[2]]
                instance.start()
                ev = Event("instance_started", None, parameters=[])
                self.to_send.append((input[0], input[1], input[2], ev))
            elif input[3].name == "delete_instance":
                ev = Event("instance_deleted", None, parameters=[TODO])
                self.to_send.append((TODO, TODO, TODO, ev))
            elif input[3].name == "associate_instance":
                ev = Event("instance_associated", None, parameters=[TODO])
                self.to_send.append((TODO, TODO, TODO, ev))
            elif input[3].name == "disassociate_instance":
                ev = Event("instance_disassociated", None, parameters=[TODO])
                self.to_send.append((TODO, TODO, TODO, ev))
            elif input[3].name == "instance_created":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
                instance.associations['fields'].instances[0] = input[3].parameters[0]
            elif input[3].name == "instance_started":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
            elif input[3].name == "instance_deleted":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
            elif input[3].name == "instance_associated":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
            elif input[3].name == "instance_disassociated":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
            elif input[3].name == "set_association_name":
                ev = input[3]
                self.addInput(ev, force_internal=True)
        return self.instances
    
    def intTransition(self):
        self.to_send = []
        self.handleInput()
        self.stepAll()
        return self.instances
    
    def outputFnc(self):
        to_dict = {}
        for sending in self.to_send:
            if sending[0] == None:
                if self.obj_manager_out in to_dict:
                    to_dict[self.obj_manager_out].append(sending)
                else:
                    to_dict[self.obj_manager_out] = [sending]
            else:
                the_port = None
                for port in self.OPorts:
                    if port.name == sending[0]:
                        the_port = port
                if the_port in to_dict:
                    to_dict[the_port].append(sending)
                else:
                    to_dict[the_port] = [sending]
        return to_dict
    
    def timeAdvance(self):
        if not (len(self.to_send) == 0):
            return 0
        return self.getEarliestEventTime()

class TrafficLightInstance(RuntimeClassBase):
    def __init__(self, atomdevs, canvas):
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
        TrafficLightInstance.user_defined_constructor(self, canvas)
    
    def user_defined_constructor(self, canvas):
        size        = 100;
        offset      = size+5;
        self.RED    = 0;
        self.YELLOW = 1;
        self.GREEN  = 2;
        self.colors = ['#f00','#ff0','#0f0']
        self.lights = [
            canvas.add_rectangle(size/2, size/2, size, size, {'fill':'#000'}),
            canvas.add_rectangle(size/2, size/2+offset,     size, size, {'fill':'#000'}),
            canvas.add_rectangle(size/2, size/2+2*offset, size, size, {'fill':'#000'})];
    
    def user_defined_destructor(self):
        pass
    
    
    # user defined method
    def clear(self):
        self.lights[self.RED].set_color('#000');
        self.lights[self.YELLOW].set_color('#000');
        self.lights[self.GREEN].set_color('#000');
    
    
    # user defined method
    def setGreen(self):
        self.clear();
        self.lights[self.GREEN].set_color(self.colors[self.GREEN]);
    
    
    # user defined method
    def setYellow(self):
        self.clear();
        self.lights[self.YELLOW].set_color(self.colors[self.YELLOW]);
    
    
    # user defined method
    def setRed(self):
        self.clear();
        self.lights[self.RED].set_color(self.colors[self.RED]);
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /on
        self.states["/on"] = State(1, "/on", self)
        
        # state /on/normal
        self.states["/on/normal"] = State(2, "/on/normal", self)
        
        # state /on/normal/red
        self.states["/on/normal/red"] = State(3, "/on/normal/red", self)
        self.states["/on/normal/red"].setEnter(self._on_normal_red_enter)
        self.states["/on/normal/red"].setExit(self._on_normal_red_exit)
        
        # state /on/normal/green
        self.states["/on/normal/green"] = State(4, "/on/normal/green", self)
        self.states["/on/normal/green"].setEnter(self._on_normal_green_enter)
        self.states["/on/normal/green"].setExit(self._on_normal_green_exit)
        
        # state /on/normal/yellow
        self.states["/on/normal/yellow"] = State(5, "/on/normal/yellow", self)
        self.states["/on/normal/yellow"].setEnter(self._on_normal_yellow_enter)
        self.states["/on/normal/yellow"].setExit(self._on_normal_yellow_exit)
        
        # state /on/normal/history
        self.states["/on/normal/history"] = ShallowHistoryState(6, "/on/normal/history", self)
        
        # state /on/interrupted
        self.states["/on/interrupted"] = State(7, "/on/interrupted", self)
        
        # state /on/interrupted/yellow
        self.states["/on/interrupted/yellow"] = State(8, "/on/interrupted/yellow", self)
        self.states["/on/interrupted/yellow"].setEnter(self._on_interrupted_yellow_enter)
        self.states["/on/interrupted/yellow"].setExit(self._on_interrupted_yellow_exit)
        
        # state /on/interrupted/black
        self.states["/on/interrupted/black"] = State(9, "/on/interrupted/black", self)
        self.states["/on/interrupted/black"].setEnter(self._on_interrupted_black_enter)
        self.states["/on/interrupted/black"].setExit(self._on_interrupted_black_exit)
        
        # state /off
        self.states["/off"] = State(10, "/off", self)
        self.states["/off"].setEnter(self._off_enter)
        
        # add children
        self.states[""].addChild(self.states["/on"])
        self.states[""].addChild(self.states["/off"])
        self.states["/on"].addChild(self.states["/on/normal"])
        self.states["/on"].addChild(self.states["/on/interrupted"])
        self.states["/on/normal"].addChild(self.states["/on/normal/red"])
        self.states["/on/normal"].addChild(self.states["/on/normal/green"])
        self.states["/on/normal"].addChild(self.states["/on/normal/yellow"])
        self.states["/on/normal"].addChild(self.states["/on/normal/history"])
        self.states["/on/interrupted"].addChild(self.states["/on/interrupted/yellow"])
        self.states["/on/interrupted"].addChild(self.states["/on/interrupted/black"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/on"]
        self.states["/on"].default_state = self.states["/on/normal"]
        self.states["/on/normal"].default_state = self.states["/on/normal/red"]
        self.states["/on/interrupted"].default_state = self.states["/on/interrupted/yellow"]
        
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
        
        # transition /on
        _on_0 = Transition(self, self.states["/on"], [self.states["/off"]])
        _on_0.setTrigger(Event("quit_clicked", self.getInPortName("ui")))
        self.states["/on"].addTransition(_on_0)
        
        # transition /on/normal
        _on_normal_0 = Transition(self, self.states["/on/normal"], [self.states["/on/interrupted"]])
        _on_normal_0.setTrigger(Event("police_interrupt_clicked", self.getInPortName("ui")))
        self.states["/on/normal"].addTransition(_on_normal_0)
        
        # transition /on/interrupted
        _on_interrupted_0 = Transition(self, self.states["/on/interrupted"], [self.states["/on/normal/history"]])
        _on_interrupted_0.setTrigger(Event("police_interrupt_clicked", self.getInPortName("ui")))
        self.states["/on/interrupted"].addTransition(_on_interrupted_0)
    
    def _on_normal_red_enter(self):
        self.setRed();
        self.addTimer(0, 3)
    
    def _on_normal_red_exit(self):
        self.removeTimer(0)
    
    def _on_normal_green_enter(self):
        self.setGreen();
        self.addTimer(1, 2)
    
    def _on_normal_green_exit(self):
        self.removeTimer(1)
    
    def _on_normal_yellow_enter(self):
        self.setYellow();
        self.addTimer(2, 1)
    
    def _on_normal_yellow_exit(self):
        self.removeTimer(2)
    
    def _on_interrupted_yellow_enter(self):
        self.setYellow();
        self.addTimer(3, .5)
    
    def _on_interrupted_yellow_exit(self):
        self.removeTimer(3)
    
    def _on_interrupted_black_enter(self):
        self.clear();
        self.addTimer(4, .5)
    
    def _on_interrupted_black_exit(self):
        self.removeTimer(4)
    
    def _off_enter(self):
        self.clear();
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/on"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class TrafficLight(AtomicDEVS, ObjectManagerBase):
    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        ObjectManagerBase.__init__(self)
        self.elapsed = 0
        self.obj_manager_in = self.addInPort("obj_manager_in")
        self.obj_manager_out = self.addOutPort("obj_manager_out")
        self.input = self.addInPort("input")
        self.outputs = {}
        self.obj_manager_in = self.addInPort("obj_manager_in")
        self.input = self.addInPort("input")
    
    def extTransition(self, inputs):
        self.simulated_time = (self.simulated_time + self.elapsed)
        all_inputs = []
        if self.obj_manager_in in inputs:
            all_inputs.extend(inputs[self.obj_manager_in])
        if self.input in inputs:
            all_inputs.extend(inputs[self.input])
        for input in all_inputs:
            if isinstance(input, str):
                tem = eval(input)
                self.addInput(tem)
            if input[3].name == "create_instance":
                self.instances.add(TrafficLightInstance(self))
                ev = Event("instance_created", None, parameters=[f"{input[0]}[{len(self.instances)-1}]"])
                self.to_send.append(("TrafficLight", TODO, input[2], ev))
            elif input[3].name == "start_instance":
                instance = list(self.instances)[input[2]]
                instance.start()
                ev = Event("instance_started", None, parameters=[TODO])
                self.to_send.append((input[0], input[1], input[2], ev))
            elif input[3].name == "delete_instance":
                ev = Event("instance_deleted", None, parameters=[TODO])
                self.to_send.append((TODO, TODO, TODO, ev))
            elif input[3].name == "associate_instance":
                ev = Event("instance_associated", None, parameters=[TODO])
                self.to_send.append((TODO, TODO, TODO, ev))
            elif input[3].name == "disassociate_instance":
                ev = Event("instance_disassociated", None, parameters=[TODO])
                self.to_send.append((TODO, TODO, TODO, ev))
            elif input[3].name == "instance_created":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
                instance.associations['fields'].instances[0] = input[3].parameters[0]
            elif input[3].name == "instance_started":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
            elif input[3].name == "instance_deleted":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
            elif input[3].name == "instance_associated":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
            elif input[3].name == "instance_disassociated":
                instance = list(self.instances)[input[2]]
                instance.addEvent(input[3])
            elif input[3].name == "set_association_name":
                ev = input[3]
                self.addInput(ev, force_internal=True)
        return self.instances
    
    def intTransition(self):
        self.to_send = []
        self.handleInput()
        self.stepAll()
        return self.instances
    
    def outputFnc(self):
        to_dict = {}
        for sending in self.to_send:
            if sending[0] == None:
                if self.obj_manager_out in to_dict:
                    to_dict[self.obj_manager_out].append(sending)
                else:
                    to_dict[self.obj_manager_out] = [sending]
            else:
                the_port = None
                for port in self.OPorts:
                    if port.name == sending[0]:
                        the_port = port
                if the_port in to_dict:
                    to_dict[the_port].append(sending)
                else:
                    to_dict[the_port] = [sending]
        return to_dict
    
    def timeAdvance(self):
        if not (len(self.to_send) == 0):
            return 0
        return self.getEarliestEventTime()

class ObjectManagerState:
    def __init__(self):
        self.to_send = [(None, "MainApp", 0, Event("start_instance", None, None))]

class ObjectManager(AtomicDEVS):
    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.State = ObjectManagerState()
        self.input = self.addInPort("input")
        self.output = {}
        self.output["MainApp"] = self.addOutPort()
        self.output["TrafficLight"] = self.addOutPort()
    
    def extTransition(self, inputs):
        all_inputs = inputs[self.input]
        for input in all_inputs:
            self.State.to_send.append(input)
        return self.State
    
    def intTransition(self):
        self.State.to_send = []
        return self.State
    
    def outputFnc(self):
        out_dict = {}
        for (source, target, id, message) in self.State.to_send:
            out_dict[self.output[target]] = [(source, target, id, message)]
        return out_dict
    
    def timeAdvance(self):
        if self.State.to_send:
            return 0
        return INFINITY

class Controller(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)
        self.ui = self.addInPort("ui")
        self.objectmanager = self.addSubModel(ObjectManager("ObjectManager"))
        self.atomic0 = self.addSubModel(MainApp("MainApp"))
        self.atomic1 = self.addSubModel(TrafficLight("TrafficLight"))
        self.connectPorts(self.atomic0.obj_manager_out, self.objectmanager.input)
        self.connectPorts(self.objectmanager.output["MainApp"], self.atomic0.obj_manager_in)
        self.connectPorts(self.atomic0.outputs["trafficlight"], self.atomic1.input)
        self.connectPorts(self.atomic1.obj_manager_out, self.objectmanager.input)
        self.connectPorts(self.objectmanager.output["TrafficLight"], self.atomic1.obj_manager_in)