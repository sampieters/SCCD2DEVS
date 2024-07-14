import tests.Test5.PyDEVS.target as target
from sccd.runtime.DEVS_loop import DEVSSimulator
from sccd.runtime.statecharts_core import Event

class OutputListener:
	def add(self, events):
		for event in events:
			if event.port == "ui":
				print(event.name, ", received on:", event.parameters[0], "seconds")
				if event.name == "output_event":
					sim.addInput(Event("input_event", "ui", []))
				

if __name__ == '__main__':
	controller = target.Controller(name="controller")
	refs = {"ui": controller.in_ui}
	sim = DEVSSimulator(controller, refs)

	listener = OutputListener()
	sim.setListenPorts(controller.out_ui, listener.add)
	sim.simulate()

