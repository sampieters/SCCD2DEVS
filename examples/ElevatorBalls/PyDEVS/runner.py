import tkinter as tk
import target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.DEVSSimulatorWrapper import DEVSSimulator

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

	tkroot = tk.Tk()
	tkroot.withdraw()
	sim = DEVSSimulator(model)

	#sim.setVerbose("./examples/BouncingBalls/PyDEVS/log.txt")
	sim.setRealTimePlatformTk(tkroot)

	ui = UI(tkroot, sim)

	listener = OutputListener(ui)
	sim.setListenPorts(model.out_ui, listener.add)
	sim.simulate()
	tkroot.mainloop()
