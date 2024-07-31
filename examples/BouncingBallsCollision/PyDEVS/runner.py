import tkinter as tk
import target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.DEVS_loop import DEVSSimulator

class OutputListener:
	def __init__(self, ui):
		self.ui = ui

	def add(self, events):
		for event in events:
			if event.port == "ui":
				method = getattr(self.ui, event.name)
				method(*event.parameters)

if __name__ == '__main__':
	model = target.Controller(name="controller")
	#refs = {"ui": model.in_ui, "field_ui": model.atomic1.field_ui, "button_ui": model.atomic2.button_ui, "ball_ui": model.atomic3.ball_ui}

	tkroot = tk.Tk()
	tkroot.withdraw()
	sim = DEVSSimulator(model)

	#sim.setVerbose()
	sim.setRealTimePlatformTk(tkroot)

	ui = UI(tkroot, sim)

	listener = OutputListener(ui)
	sim.setListenPorts(model.out_ui, listener.add)
	sim.simulate()
	tkroot.mainloop()
