import target as target
from sccd.runtime.DEVS_loop import DEVSSimulator
from sccd.runtime.statecharts_core import Event

class OutputListener:
	def __init__(self, controller) -> None:
		self.controller = controller

	def add(self, events):
		for event in events:
			if event.port == "ui":
				#print(event.name, ", received on:", event.parameters[0], "seconds, parameters:", event.parameters[1:])
				if event.name == "generate_input":
					self.controller.addInput(Event("test", "in_ui"))
				

if __name__ == '__main__':
	controller = target.Controller(name="controller")
	refs = {"in_ui": controller.in_ui}
	sim = DEVSSimulator(controller, refs)

	listener = OutputListener(sim)
	sim.setListenPorts(controller.out_ui, listener.add)
	sim.simulate()

