from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY
from ..statecharts_core import *
import time
import random
import tk
from mvk_widget import MvKWidget


class SCCD(CoupledDEVS):
	def __init__(self):
		CoupledDEVS.__init__(self)

		self.inports = []
		for inport in range(1):
			self.inports.append(self.addInPort())

		self.outports = []
		for outport in range(0):
			self.outports.append(self.addOutPort())

		mainapp = self.addSubModel(MainApp())
		field = self.addSubModel(Field())
		button = self.addSubModel(Button())
		ball = self.addSubModel(Ball())

		self.connectPorts(mainapp.outport, field.inport)
		self.connectPorts(field.outport, ball.inport)
		self.connectPorts(field.outport, button.inport)
		self.connectPorts(field.outport, mainapp.inport)
		self.connectPorts(button.outport, field.inport)
		self.connectPorts(ball.outport, field.inport)


class MainAppState:
	def __init__(self):
		tk.Tk.__init__(self)
		self.fixed_update_time = 20
		self.update_self()
		self.withdraw()
		self.nr_of_fields = 0
			
		Root_running_root_main_behaviour_initializing = State()
		Root_running_root_main_behaviour_running = State()
		Root_running_root_main_behaviour = CompositeState(Root_running_root_main_behaviour_initializing)
		Root_running_root_cd_behaviour_waiting = State()
		Root_running_root_cd_behaviour_creating = State()
		Root_running_root_cd_behaviour_check_nr_of_fields = State()
		Root_running_root_cd_behaviour = CompositeState(Root_running_root_cd_behaviour_waiting)
		Root_running_root = ParallelState([Root_running_root_main_behaviour, Root_running_root_cd_behaviour])
		Root_running_stopped = State()
		Root_running = CompositeState(Root_running_root)
		Root = CompositeState(Root_running)

		Transition(None, Root_running_root_main_behaviour_initializing, Root_running_root_main_behaviour_running)
		Transition(None, Root_running_root_main_behaviour_running, Root_running_root_main_behaviour_running)
		Transition(None, Root_running_root_cd_behaviour_waiting, Root_running_root_cd_behaviour_creating)
		Transition(None, Root_running_root_cd_behaviour_waiting, Root_running_root_cd_behaviour_check_nr_of_fields)
		Transition(None, Root_running_root_cd_behaviour_creating, Root_running_root_cd_behaviour_waiting)
		Transition(None, Root_running_root_cd_behaviour_check_nr_of_fields, Root_running_stopped)
		Transition(None, Root_running_root_cd_behaviour_check_nr_of_fields, Root_running_root_cd_behaviour_waiting)
		
	def update_self(self):
		self.controller.update(self.fixed_update_time / 1000.0)
		self.schedule_time = time.time()
		self.scheduled_update_id = self.after(self.fixed_update_time, self.update_self)
			

class MainApp(AtomicDEVS):
	def __init__(self):
		AtomicDEVS.__init__(self)
		self.advance = 0
		self.state = [MainAppState()]

	def timeAdvance(self):
		pass
	def extTransition(self, inputs):
		pass
	def intTransition(self):
		pass
	def outputFnc(self):
		pass


class FieldState:
	def __init__(self):
		
		tk.Toplevel.__init__(self)
		self.title('BouncingBalls')

		CANVAS_SIZE_TUPLE = (0, 0, self.winfo_screenwidth() * 2, self.winfo_screenheight() * 2)
		self.c = tk.Canvas(self, relief=tk.RIDGE, scrollregion=CANVAS_SIZE_TUPLE)

		MvKWidget.__init__(self, self.controller, self.c)
		
			
		Root_root_waiting = State()
		Root_root_initializing = State()
		Root_root_creating = State()
		Root_root_packing = State()
		Root_root_running_main_behaviour_running = State()
		Root_root_running_main_behaviour_creating = State()
		Root_root_running_main_behaviour = CompositeState(Root_root_running_main_behaviour_running)
		Root_root_running_deleting_behaviour_running = State()
		Root_root_running_deleting_behaviour = CompositeState(Root_root_running_deleting_behaviour_running)
		Root_root_running_child_behaviour_listening = State()
		Root_root_running_child_behaviour = CompositeState(Root_root_running_child_behaviour_listening)
		Root_root_running = ParallelState([Root_root_running_main_behaviour, Root_root_running_deleting_behaviour, Root_root_running_child_behaviour])
		Root_root_deleting = State()
		Root_root_deleted = State()
		Root_root = CompositeState(Root_root_waiting)
		Root = CompositeState(Root_root)
		Transition(None, Root_root_waiting, Root_root_initializing)
		Transition(None, Root_root_initializing, Root_root_creating)
		Transition(None, Root_root_creating, Root_root_packing)
		Transition(None, Root_root_packing, Root_root_running)
		Transition(None, Root_root_running_main_behaviour_running, Root_root_running_main_behaviour_creating)
		Transition(None, Root_root_running_main_behaviour_creating, Root_root_running_main_behaviour_running)
		Transition(None, Root_root_running_deleting_behaviour_running, Root_root_running_deleting_behaviour_running)
		Transition(None, Root_root_running_child_behaviour_listening, Root_root_running_child_behaviour_listening)
		Transition(None, Root_root_running, Root_root_deleting)
		Transition(None, Root_root_deleting, Root_root_deleted)
		


class Field(AtomicDEVS):
	def __init__(self):
		AtomicDEVS.__init__(self)
		self.advance = INFINITY
		self.state = []

	def timeAdvance(self):
		pass
	def extTransition(self, inputs):
		pass
	def intTransition(self):
		pass
	def outputFnc(self):
		pass


class ButtonState:
	def __init__(self, parent, event_name, button_text):
		tk.Button.__init__(self, parent, text=button_text)
		MvKWidget.__init__(self, self.controller)
		self.event_name = event_name
			
		Root_initializing = State()
		Root_running = State()
		Root = CompositeState(Root_initializing)
		Transition(None, Root_initializing, Root_running)
		Transition(None, Root_running, Root_running)
		


class Button(AtomicDEVS):
	def __init__(self):
		AtomicDEVS.__init__(self)
		self.advance = INFINITY
		self.state = []

	def timeAdvance(self):
		pass
	def extTransition(self, inputs):
		pass
	def intTransition(self):
		pass
	def outputFnc(self):
		pass


class BallState:
	def __init__(self, canvas, x, y):
		self.canvas = canvas
		self.r = 15.0
		self.smooth = 0.4 # value between 0 and 1
		self.vel = {'x': random.random() * 2.0 - 1.0, 'y': random.random() * 2.0 - 1.0}
		self.id = self.canvas.create_oval(x, y, x + (self.r * 2), y + (self.r * 2), fill="black")
		MvKWidget.__init__(self, self.controller, self.canvas, self.id)
			
		Root_main_behaviour_initializing = State()
		Root_main_behaviour_bouncing = State()
		Root_main_behaviour_dragging = State()
		Root_main_behaviour_selected = State()
		Root_main_behaviour = CompositeState(Root_main_behaviour_initializing)
		Root_deleted = State()
		Root = CompositeState(Root_main_behaviour)
		Transition(None, Root_main_behaviour_initializing, Root_main_behaviour_bouncing)
		Transition(None, Root_main_behaviour_bouncing, Root_main_behaviour_bouncing)
		Transition(None, Root_main_behaviour_bouncing, Root_main_behaviour_selected)
		Transition(None, Root_main_behaviour_dragging, Root_main_behaviour_dragging)
		Transition(None, Root_main_behaviour_dragging, Root_main_behaviour_bouncing)
		Transition(None, Root_main_behaviour_selected, Root_main_behaviour_dragging)
		Transition(None, Root_main_behaviour_selected, Root_main_behaviour_selected)
		Transition(None, Root_main_behaviour, Root_deleted)
		


class Ball(AtomicDEVS):
	def __init__(self):
		AtomicDEVS.__init__(self)
		self.advance = INFINITY
		self.state = []

	def timeAdvance(self):
		pass
	def extTransition(self, inputs):
		pass
	def intTransition(self):
		pass
	def outputFnc(self):
		pass
