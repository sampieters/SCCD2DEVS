import target as target
from pypdevs.simulator import Simulator

if __name__ == '__main__':
	model = target.Controller(name="controller")
	sim = Simulator(model)
	sim.setRealTime(True)
	sim.simulate()
