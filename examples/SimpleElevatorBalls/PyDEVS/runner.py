import tkinter as tk
import examples.SimpleElevatorBalls.PyDEVS.target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.DEVS_loop import DEVSSimulator

class OutputListener:
	def __init__(self, ui):
		self.ui = ui

	def add(self, event):
		if event.port == "ui":
			method = getattr(self.ui, event.name)
			method(*event.parameters)

if __name__ == '__main__':
	model = target.Controller(name="controller")
	refs = {"ui": model.ui, "elevator_ui": model.atomic1.elevator_ui, "ball_ui": model.atomic2.ball_ui}

	tkroot = tk.Tk()
	tkroot.withdraw()
	sim = DEVSSimulator(model)
	sim.setRealTime(True)
	sim.setRealTimeInputFile(None)
	sim.setRealTimePorts(refs)
	sim.setVerbose(None)
	sim.setRealTimePlatformTk(tkroot)

	ui = UI(tkroot, sim)
	model.atomic1.addMyOwnOutputListener(OutputListener(ui))
	model.atomic2.addMyOwnOutputListener(OutputListener(ui))
	sim.simulate()
	tkroot.mainloop()
