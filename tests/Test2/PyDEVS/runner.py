import tests.Test2.PyDEVS.target as target
from sccd.runtime.DEVS_loop import DEVSSimulator

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

	listener = OutputListener()
	sim.setListenPorts(model.out_ui, listener.add)
	sim.simulate()

