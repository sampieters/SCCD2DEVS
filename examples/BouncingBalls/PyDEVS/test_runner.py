import tkinter as tk
import examples.BouncingBalls.PyDEVS.target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.DEVS_loop import DEVSSimulator
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

class OutputListener:
	def __init__(self, model, log_file):
		self.model = model
		self.log_file = log_file

		# Clear the log file when the listener is initialized
		with open(self.log_file, 'w') as file:
			file.write('')  # This will create a new empty file or clear the existing file
		
	def add(self, events):
		with open(self.log_file, 'a') as file:
			for event in events:
				file.write(f'{event}\n')

				# IMPORTANT: This is here because we add our own inputs but tkinter will not close properly because of this
				#if event.name == "destroy_all":
					#self.tk.destroy()

if __name__ == '__main__':
	model = target.Controller(name="controller")
	refs = {"ui": model.in_ui, "field_ui": model.atomic1.field_ui, "button_ui": model.atomic2.button_ui, "ball_ui": model.atomic3.ball_ui}

	tkroot = tk.Tk()
	tkroot.withdraw()
	sim = DEVSSimulator(model, refs)
	sim.setRealTimeInputFile("./examples/BouncingBalls/input_trace.txt")
	
	sim.setRealTimePlatformTk(tkroot)

	listener = OutputListener(model, "./examples/BouncingBalls/PyDEVS/output.txt")
	sim.setListenPorts(model.out_ui, listener.add)

	sim.simulate()
	tkroot.mainloop()