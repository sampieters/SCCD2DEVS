import target as target
from sccd.runtime.statecharts_core import Event
import threading

class OutputListener:
	def add(self, event):
		if event.port == "ui":
			print(event.name, ", received on:", event.parameters[0], "seconds, parameters:", event.parameters[1:])
				

if __name__ == '__main__':
	controller = target.Controller()
	controller.keep_running = False
	controller.addMyOwnOutputListener(OutputListener())
	controller.setVerbose(None)
	controller.start()