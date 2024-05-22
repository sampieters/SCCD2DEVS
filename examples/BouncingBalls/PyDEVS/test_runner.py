import tkinter as tk
import examples.BouncingBalls.PyDEVS.target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.DEVS_loop import DEVSSimulator

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

class OutputListener(AtomicDEVS):
    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        self.simulated_time = 0
        self.input = self.addInPort("input")

    def extTransition(self, inputs):
        self.simulated_time += self.elapsed
        

    def intTransition(self):
        pass

    def outputFnc(self):
        pass
    
    def timeAdvance(self):
        return INFINITY

if __name__ == '__main__':
	model = target.Controller(name="controller")
	listener = model.addSubModel(OutputListener("listener"))
	model.connectPorts(model.ui, listener.input) 

	refs = {"ui": model.ui, "field_ui": model.atomic1.field_ui, "button_ui": model.atomic2.button_ui, "ball_ui": model.atomic3.ball_ui}

	tkroot = tk.Tk()
	tkroot.withdraw()
	sim = DEVSSimulator(model)
	sim.setRealTime(True)
	sim.setRealTimeInputFile("./examples/BouncingBalls/input_trace.txt")
	sim.setRealTimePorts(refs)
	sim.setVerbose("./examples/BouncingBalls/PyDEVS/trace.txt")
	sim.setRealTimePlatformTk(tkroot)
     


	#ui = UI(tkroot, sim)
	#model.atomic1.addMyOwnOutputListener(OutputListener(ui))
	#model.atomic2.addMyOwnOutputListener(OutputListener(ui))
	#model.atomic3.addMyOwnOutputListener(OutputListener(ui))
	sim.simulate()
	tkroot.mainloop()
