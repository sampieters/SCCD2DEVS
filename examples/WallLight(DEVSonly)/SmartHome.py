from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY
  
class App(AtomicDEVS):
    def __init__(self):
        AtomicDEVS.__init__(self, "SmartHome")
        self.state = None
        self.inport = self.addInPort("inport")
        self.outport = self.addOutPort("outport")


class Light(AtomicDEVS):
    def __init__(self):
        AtomicDEVS.__init__(self, "Light")
        self.state = "off"
        self.processing_time = 5
        self.in_socket = self.addInPort("in_socket")
        self.out_socket = self.addOutPort("out_socket")

    def timeAdvance(self):
        if self.state is None:
            return INFINITY
        else:
            return self.processing_time

    def outputFnc(self):
        return {self.out_socket: self.state}

    def extTransition(self, inputs):
        self.state = inputs[self.inport]
        return self.state

    def intTransition(self):
        print(self.state)
        if self.state == "on":
            self.state = None
        else:
            self.state = "on"
        return self.state

class SmartHome(CoupledDEVS):
    def __init__(self, name):
        CoupledDEVS.__init__(self, name)
        self.router_in = self.addInPort("router_in")

        app = self.addSubModel(App())
        light = self.addSubModel(Light())
        self.connectPorts(app.outport, light.in_socket)
