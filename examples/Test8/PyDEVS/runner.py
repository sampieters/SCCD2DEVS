import target as target
from sccd.runtime.DEVS_loop import DEVSSimulator
model = target.Controller(name="controller")
sim = DEVSSimulator(model)
sim.setRealTime(False)


sim.setVerbose("./examples/Test8/PyDEVS/log.txt")

sim.simulate()