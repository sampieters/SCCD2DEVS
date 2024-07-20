import tkinter as tk
import target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.DEVS_loop import DEVSSimulator

if __name__ == '__main__':
	model = target.Controller(name="controller")

	sim = DEVSSimulator(model)
	sim.setRealTime(False)

	sim.setVerbose(None)

	sim.simulate()
