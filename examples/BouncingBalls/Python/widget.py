import tkinter as tk
from sccd.runtime.statecharts_core import Event

class Widget:
	controller = None

	def __init__(self, configure_later=False):
		if not configure_later:
			self.set_bindable_and_tagorid(None, None)

	def set_bindable_and_tagorid(self, bindable=None, tagorid=None):
		if bindable is None:
			bindable = self
		self.bindable = bindable
		self.mytagorid = tagorid
		if isinstance(self, tk.Toplevel):
			self.protocol("WM_DELETE_WINDOW", self.window_close)
		if tagorid is not None:
			if not isinstance(tagorid, list):
				tagorid = [tagorid]
			for t in tagorid:
				self.bindable.tag_bind(t, "<Button>", self.on_click)
				self.bindable.tag_bind(t, "<ButtonRelease>", self.on_release)
				self.bindable.tag_bind(t, "<Motion>", self.on_motion)
				self.bindable.tag_bind(t, "<Enter>", self.on_enter)
				self.bindable.tag_bind(t, "<Leave>", self.on_leave)
				self.bindable.tag_bind(t, "<Key>", self.on_key)
				self.bindable.tag_bind(t, "<KeyRelease>", self.on_key_release)
		else:
			self.bindable.bind("<Button>", self.on_click)
			self.bindable.bind("<ButtonRelease>", self.on_release)
			self.bindable.bind("<Motion>", self.on_motion)
			self.bindable.bind("<Enter>", self.on_enter)
			self.bindable.bind("<Leave>", self.on_leave)
			self.bindable.bind("<Key>", self.on_key)
			self.bindable.bind("<KeyRelease>", self.on_key_release)
		self.last_x = 50
		self.last_y = 50
		self.selected_type = None

	def on_click(self, event):
		event_name = None

		if event.num == 1:
			event_name = "left-click"
		elif event.num == 2:
			event_name = "middle-click"
		elif event.num == 3:
			event_name = "right-click"

		if event_name:
			self.last_x = event.x
			self.last_y = event.y
			Widget.controller.addInput(Event(event_name, "input", [id(self)]))

	def on_release(self, event):
		event_name = None

		if event.num == 1:
			event_name = "left-release"
		elif event.num == 2:
			event_name = "middle-release"
		elif event.num == 3:
			event_name = "right-release"

		if event_name:
			self.last_x = event.x
			self.last_y = event.y
			Widget.controller.addInput(Event(event_name, "input", [id(self)]))

	def on_motion(self, event):
		self.last_x = event.x
		self.last_y = event.y
		Widget.controller.addInput(Event("motion", "input", [id(self)]))

	def on_enter(self, event):
		Widget.controller.addInput(Event("enter", "input", [id(self)]))

	def on_leave(self, event):
		Widget.controller.addInput(Event("leave", "input", [id(self)]))

	def on_key(self, event):
		event_name = None

		if event.keysym == 'Escape':
			event_name = "escape"
		elif event.keysym == 'Return':
			event_name = "return"
		elif event.keysym == 'Delete':
			event_name = "delete"
		elif event.keysym == 'Shift_L':
			event_name = "shift"
		elif event.keysym == 'Control_L':
			event_name = "control"

		if event_name:
			Widget.controller.addInput(Event(event_name, "input", [id(self)]))

	def on_key_release(self, event):
		event_name = None

		if event.keysym == 'Escape':
			event_name = "escape-release"
		elif event.keysym == 'Return':
			event_name = "return-release"
		elif event.keysym == 'Delete':
			event_name = "delete-release"
		elif event.keysym == 'Shift_L':
			event_name = "shift-release"
		elif event.keysym == 'Control_L':
			event_name = "control-release"

		if event_name:
			Widget.controller.addInput(Event(event_name, "input", [id(self)]))

	def window_close(self):
		Widget.controller.addInput(Event("window-close", "input", [id(self)]))