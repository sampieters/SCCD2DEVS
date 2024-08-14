import target as target
from sccd.runtime.DEVSSimulatorWrapper import DEVSSimulator

class OutputListener:
	def add(self, events):
		for event in events:
			sim_time = event.getParameters()[0] / 1000.0  # Convert from milliseconds to seconds
			act_time = event.getParameters()[1]
			print("SIMTIME: %.2fs" % (sim_time))
			print("ACTTIME: %.2fs" % (act_time))

if __name__ == '__main__':
	model = target.Controller(name="controller")

	sim = DEVSSimulator(model)
	sim.setRealTime()

	listener = OutputListener()
	sim.setListenPorts(model.out_output, listener.add)
	sim.simulate()

	while 1:
		pass
