import tkinter as tk
import examples.FixedTimerEventloop.PyDEVS.target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.DEVS_loop import DEVSSimulator



class OutputListener:
	def __init__(self, ui):
		self.ui = ui

	def add(self, events):
		for event in events:
			if event[2].port == "ui":
				method = getattr(self.ui, event[2].name)
				method(*event[2].parameters)

if __name__ == '__main__':
	model = target.Controller(name="controller")
	refs = {"ui": model.in_ui, "field_ui": model.atomic0.field_ui}

	tkroot = tk.Tk()
	tkroot.withdraw()
	sim = DEVSSimulator(model)
	sim.setRealTime(True)
	#sim.setRealTimeInputFile("./examples/BouncingBalls/input_trace.txt")
	sim.setRealTimePorts(refs)
	sim.setVerbose("./examples/BouncingBalls/PyDEVS/trace.txt")
	
	sim.setRealTimePlatformTk(tkroot)

	ui = UI(tkroot, sim)
	listener = OutputListener(ui)
	sim.setListenPorts(model.out_ui, listener.add)
	model.atomic0.addMyOwnOutputListener(OutputListener(ui))
	sim.simulate()
	tkroot.mainloop()