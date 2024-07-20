import target as target
from sccd.runtime.DEVS_loop import DEVSSimulator

model = target.Controller(name="controller")
refs = {"ui": model.in_ui}
sim = DEVSSimulator(model, refs)
sim.setRealTime(False)

# Set verbose to the log file path
#sim.setVerbose(None)

sim.simulate()