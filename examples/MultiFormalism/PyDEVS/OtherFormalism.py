from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY

from sccd.runtime.statecharts_core import Event

class Generator(AtomicDEVS):
    def __init__(self):
        AtomicDEVS.__init__(self, "Generator")
        self.state = True
        self.outport = self.addOutPort("outport")

    def timeAdvance(self):
        if self.state:
            return 1.0
        else:
            return INFINITY

    def outputFnc(self):
        # Our message is simply the integer 5, though this could be anything
        return {self.outport: Event("produce_ball", "ui")}

    def intTransition(self):
        #self.state = False
        return self.state