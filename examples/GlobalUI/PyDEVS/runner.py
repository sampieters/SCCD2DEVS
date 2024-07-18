import target as target
from sccd.runtime.DEVS_loop import DEVSSimulator
from sccd.runtime.statecharts_core import Event

class OutputListener:
	def __init__(self, controller) -> None:
		self.controller = controller
		
	def add(self, events):
		for event in events:
			if event.name == "generate_input":
			    self.controller.addInput(Event("test", "ui"))

if __name__ == '__main__':
	model = target.Controller(name="controller")
	refs = {
		"ui": model.in_ui,  
	}

	sim = DEVSSimulator(model, refs)
	sim.setVerbose(None)
	listener = OutputListener(sim)
	sim.setListenPorts(model.out_ui, listener.add)
	sim.simulate()
