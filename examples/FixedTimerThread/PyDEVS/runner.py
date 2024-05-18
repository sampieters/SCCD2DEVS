import target as target
from sccd.runtime.DEVS_statecharts_core import Event
import threading


if __name__ == '__main__':
    controller = target.Controller() 
    
    def raw_inputter():
        while 1:
            controller.addInput(Event(input(), "input", []))
    input_thread = threading.Thread(target=raw_inputter)
    input_thread.daemon = True
    input_thread.start()
    
    output_listener = controller.addOutputListener(["output"])
    def outputter():
        while 1:
            event = output_listener.fetch(-1)
            print("SIMTIME: %.2fs" % (event.getParameters()[0] / 1000.0))
            print("ACTTIME: %.2fs" % (event.getParameters()[1]))
    output_thread = threading.Thread(target=outputter)
    output_thread.daemon = True
    output_thread.start()
    
    controller.start()




import tkinter as tk
import examples.BouncingBalls.PyDEVS.target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.DEVS_loop import DEVSSimulator

class OutputListener:
	def __init__(self, ui):
		self.ui = ui

	def add(self, event):
		if event.port == "ui":
			method = getattr(self.ui, event.name)
			method(*event.parameters)

if __name__ == '__main__':
	model = target.Controller(name="controller")
	refs = {"ui": model.ui, "field_ui": model.atomic1.field_ui, "button_ui": model.atomic2.button_ui, "ball_ui": model.atomic3.ball_ui}


	sim = DEVSSimulator(model)
	sim.setRealTime(True)
	sim.setRealTimeInputFile(None)
	sim.setRealTimePorts(refs)
	sim.setVerbose(None)
	#sim.setRealTimePlatformTk(tkroot)

	model.atomic1.addMyOwnOutputListener(OutputListener(ui))
	model.atomic2.addMyOwnOutputListener(OutputListener(ui))
	model.atomic3.addMyOwnOutputListener(OutputListener(ui))
	sim.simulate()
	#tkroot.mainloop()
