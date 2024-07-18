import os
import subprocess
import importlib.util
import re
from sccd.runtime.DEVS_loop import DEVSSimulator




import target as target
from sccd.runtime.statecharts_core import Event
import threading

if __name__ == '__main__':
    controller = target.Controller()

    def raw_inputter():
        while 1:
            if controller.simulated_time is not None and controller.simulated_time > 1:
                controller.addInput(Event(input(), "ui", []))
    input_thread = threading.Thread(target=raw_inputter)
    input_thread.daemon = True
    input_thread.start()

    output_listener = controller.addOutputListener(["ui"])
    def outputter():
        while 1:
            print(str(controller.simulated_time) + " " + str(output_listener.fetch(-1)))
    output_thread = threading.Thread(target=outputter)
    output_thread.daemon = True
    output_thread.start()

    controller.start()
