from pypdevs.simulator import Simulator
import examples.BouncingBalls.PyDEVS.best_target as best_target

from tkinter import *
from sccd.runtime.libs.DEVui_v2 import UI

class OutputListener:
	def __init__(self, ui):
		self.ui = ui

	def add(self, event):
		if event.port == "ui":
			method = getattr(self.ui, event.name)
			method(*event.parameters)

if __name__ == '__main__':
	model = best_target.Controller(name="controller")
	refs = {"ui": model.ui, "field_ui": model.atomic1.field_ui, "button_ui": model.atomic2.button_ui, "ball_ui": model.atomic3.ball_ui}

	tkroot = Tk()
	tkroot.withdraw()
	sim = Simulator(model)
	sim.setRealTime(True)
	sim.setRealTimeInputFile(None)
	sim.setRealTimePorts(refs)
	sim.setVerbose(None)
	sim.setRealTimePlatformTk(tkroot)

	ui = UI(tkroot, sim)
	model.atomic1.addMyOwnOutputListener(OutputListener(ui))
	model.atomic2.addMyOwnOutputListener(OutputListener(ui))
	model.atomic3.addMyOwnOutputListener(OutputListener(ui))
	sim.simulate()
	tkroot.mainloop()
