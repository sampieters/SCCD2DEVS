'''
Created on 27-jul.-2014

@author: Simon
'''
import tkinter as tk
import target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.tkinter_eventloop import TkEventLoop
import time

return_dict = {
	"create_window": "window_created"
}



class OutputListener:
	def __init__(self, ui, controller):
		self.ui = ui
		self.controller = controller

	def add(self, event):
		if event.port == "ui":
			method = getattr(self.ui, event.name)
			method(*event.parameters)

			#ret_event = return_dict[event.name]
		#time.sleep(5)
		#print("check")


if __name__ == '__main__':
	tkroot = tk.Tk()
	tkroot.withdraw()
	controller = target.Controller(TkEventLoop(tkroot))
	ui = UI(tkroot, controller)
	controller.addMyOwnOutputListener(OutputListener(ui, controller))

	controller.setVerbose("./examples/BouncingBalls/Python/trace.txt")

	controller.start()
	tkroot.mainloop()