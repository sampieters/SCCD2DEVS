from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY


class SCCDclass(AtomicDEVS):
    def __init__(self, name=None, default=False):
        AtomicDEVS.__init__(self, name)

        # Every SCCD class has a connection to each class
        self.OUT = self.addOutPort()
        self.IN = self.addInPort()

        #
        self.state = None

        # Initial SCCD class should initialize first
        self.advance = INFINITY
        self.default = default
        if default:
            self.advance = 0

        self.initialized = False

    def timeAdvance(self):
        return self.advance

    def extTransition(self, inputs):
        return self.state

    def intTransition(self):
        return self.state

    def outputFnc(self):
        return {}


class SCCD(CoupledDEVS):
    def __init__(self, sccdObject):
        CoupledDEVS.__init__(self, sccdObject.name)

        self.inports = []
        for _ in sccdObject.inports:
            self.inports.append(self.addInPort())

        self.outports = []
        for _ in sccdObject.outports:
            self.outports.append(self.addOutPort())

        self.DEVclasses = []
        for i in sccdObject.classes:
            # Check which class is the initial/default class
            default = (i == sccdObject.default_class)
            DEVclass = self.addSubModel(SCCDclass(i.name, default))
            self.DEVclasses.append(DEVclass)



        #self.connectPorts(self.main.OUT, self.field.IN)
        #self.connectPorts(self.field.OUT, self.main.IN)
