from pypdevs.simulator import Simulator
import target as target

from tkinter import *
from sccd.runtime.libs.DEVui import ui



model = target.Controller(name="controller")
#refs = {"ui": model.ui, "field_ui": model.atomic1.field_ui}
ui.window = Tk()
ui.window.withdraw()

sim = Simulator(model)
sim.setRealTime(True)
sim.setRealTimeInputFile(None)
#sim.setRealTimePorts(refs)
sim.setVerbose(None)
sim.setRealTimePlatformTk(ui.window)

ui.simulator = sim

sim.simulate()
ui.window.mainloop()
