'''
Created on 27-jul.-2014

@author: Simon
'''
import tkinter as tk
import target as target
from sccd.runtime.libs.ui_v2 import UI
from sccd.runtime.tkinter_eventloop import TkEventLoop

from sccd.runtime.statecharts_core import Event

class OutputListener:
	def __init__(self, ui):
		self.ui = ui

	def add(self, event):
		if event.port == "ui":
			method = getattr(self.ui, event.name)
			method(*event.parameters)

if __name__ == '__main__':
	tkroot = tk.Tk()
	tkroot.withdraw()
	controller = target.Controller(TkEventLoop(tkroot))
	ui = UI(tkroot, controller)
	controller.addMyOwnOutputListener(OutputListener(ui))

	controller.setVerbose("./examples/BouncingBalls/Python/trace.txt")

	controller.start()
	tkroot.mainloop()