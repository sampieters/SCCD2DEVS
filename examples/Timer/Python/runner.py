import tkinter as tk
import target as target
from sccd.runtime.libs.ui import ui
from sccd.runtime.statecharts_core import Event
from sccd.runtime.tkinter_eventloop import *

if __name__ == '__main__':
	ui.window = tk.Tk()

	controller = target.Controller(TkEventLoop(ui.window))
	controller.start()
	ui.window.mainloop()
