import tests.Test1.PyDEVS.target as target
from sccd.runtime.DEVS_loop import DEVSSimulator

if __name__ == '__main__':
	model = target.Controller(name="controller")
	sim = DEVSSimulator(model)
	sim.setVerbose()
	sim.simulate()

