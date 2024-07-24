import target as target
from sccd.runtime.DEVS_loop import DEVSSimulator
from sccd.runtime.statecharts_core import Event

class OutputListener:
	def __init__(self, controller) -> None:
		self.controller = controller
		
	def add(self, events):
		events = events[0]
		for event in events:
			if event.name == "generate_input":
			    self.controller.addInput(Event("test", "Input"))

if __name__ == '__main__':
	model = target.Controller(name="controller")
	sim = DEVSSimulator(model)
	sim.setVerbose(None)
	listener = OutputListener(sim)

	sim.setListenPorts(model.out_Output, listener.add)
	sim.simulate()
