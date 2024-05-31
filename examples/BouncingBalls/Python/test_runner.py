'''
Created on 27-jul.-2014

@author: Simon
'''
import tkinter as tk
import target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.tkinter_eventloop import TkEventLoop
import time

class OutputListener:
	def __init__(self, controller, ui, log_file):
		self.ui = ui
		self.controller = controller
		self.log_file = log_file

	def add(self, event):
		with open(self.log_file, 'a') as file:
			file.write(f'{self.controller.getSimulatedTime()/1000} {event}\n')
		if event.port == "ui":
			method = getattr(self.ui, event.name)
			method(*event.parameters)


if __name__ == '__main__':
	tkroot = tk.Tk()
	tkroot.withdraw()
	controller = target.Controller(TkEventLoop(tkroot))
	ui = UI(tkroot, controller)
	controller.addMyOwnOutputListener(OutputListener(controller, ui, "./examples/BouncingBalls/Python/output.txt"))

	controller.setVerbose("./examples/BouncingBalls/Python/trace.txt")

	controller.start()
	tkroot.mainloop()