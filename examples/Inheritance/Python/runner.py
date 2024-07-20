import target as target
from sccd.runtime.statecharts_core import Event
import threading

if __name__ == '__main__':
    controller = target.Controller() 
    
    controller.start()