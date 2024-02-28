'''
Created on 27-jul.-2014

@author: Simon
'''
import tkinter as tk
import target as target
from sccd.runtime.libs.ui import ui
from sccd.runtime.statecharts_core import Event
from sccd.runtime.tkinter_eventloop import *

if __name__ == '__main__':
	ui.window = tk.Tk()
	ui.window.withdraw()
	controller = target.Controller(TkEventLoop(ui.window))
	controller.start()
	ui.window.mainloop()