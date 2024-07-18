import target as target
from sccd.runtime.statecharts_core import Event
import threading

class OutputListener:
	def __init__(self, controller) -> None:
		self.controller = controller

	def add(self, event):
		if event.port == "ui":
			#print(event.name, ", received on:", event.parameters[0], "seconds, parameters:", event.parameters[1:])
			if event.name == "generate_input":
				 self.controller.addInput(Event("test", "ui"))
			
				

if __name__ == '__main__':
	controller = target.Controller()
	controller.addMyOwnOutputListener(OutputListener(controller))
	controller.setVerbose(None)
	controller.start()