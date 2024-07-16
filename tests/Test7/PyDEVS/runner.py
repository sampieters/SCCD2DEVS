import target as target
from sccd.runtime.DEVS_loop import DEVSSimulator

import os

class OutputListener:
	def add(self, events):
		for event in events:
			if event.port == "ui":
				print(event.name, ":", event.parameters[0], "seconds")
				

if __name__ == '__main__':
	model = target.Controller(name="controller")
	refs = {"ui": model.in_ui}
	sim = DEVSSimulator(model, refs)
	sim.setRealTime(True)

	# Get the directory where the currently running Python file is located
	current_file_directory = os.path.dirname(os.path.abspath(__file__))

	# Create the full path for the log file
	log_file_path = os.path.join(current_file_directory, "new_log.txt")

	# Set verbose to the log file path
	sim.setVerbose(log_file_path)

	listener = OutputListener()
	sim.setListenPorts(model.out_ui, listener.add)
	sim.simulate()


