from pypdevs.simulator import Simulator
import target as target

from tkinter import *
from sccd.runtime.libs.ui_v2 import UI

class OutputListener:
	def __init__(self, ui):
		self.ui = ui

	def add(self, event):
		if event.port == "ui":
			method = getattr(self.ui, event.name)
			method(*event.parameters)

if __name__ == '__main__':
	model = target.Controller(name="controller")
	refs = {"ui": model.ui, "field_ui": model.atomic1.field_ui}

	tkroot = Tk()
	tkroot.withdraw()
	sim = Simulator(model)
	sim.setRealTime(True)
	sim.setRealTimeInputFile(None)
	sim.setRealTimePorts(refs)
	sim.setVerbose(None)
	sim.setRealTimePlatformTk(tkroot)


	#controller = target.Controller(TkEventLoop(tkroot))
	ui = UI(tkroot, "controller")
	#controller.addMyOwnOutputListener(OutputListener(ui))
	#controller.start()
	sim.simulate()
	tkroot.mainloop()


"""
model = target.Controller(name="controller")
refs = {"ui": model.ui, "field_ui": model.atomic1.field_ui}
ui.window = Tk()
ui.window.withdraw()

sim = Simulator(model)
sim.setRealTime(True)
sim.setRealTimeInputFile(None)
sim.setRealTimePorts(refs)
sim.setVerbose(None)
sim.setRealTimePlatformTk(ui.window)

ui.simulator = sim

sim.simulate()
ui.window.mainloop()
"""
