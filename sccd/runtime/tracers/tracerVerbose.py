from sccd.runtime.tracers.tracerBase import BaseTracer
import sys

class TracerVerbose(BaseTracer):
    """
    A tracer for simple verbose output
    """
    def __init__(self, filename):
        """
        Constructor

        :param uid: the UID of this tracer
        :param server: the server to make remote calls on
        :param filename: file to save the trace to, can be None for output to stdout
        """
        super(TracerVerbose, self).__init__()
        self.filename = filename
        self.prevtime = -1
        self.text = ""


    def startTracer(self, recover):
        """
        Starts up the tracer

        :param recover: whether or not this is a recovery call (so whether or not the file should be appended to)
        """
        if self.filename is None:
            self.verb_file = sys.stdout
        elif recover:
            self.verb_file = open(self.filename, 'a+')
        else:
            self.verb_file = open(self.filename, 'w')

    def stopTracer(self):
        """
        Stop the tracer
        """
        self.verb_file.flush()

    def trace(self, time):
        """
        Actual tracing function

        :param time: time at which this trace happened
        :param text: the text that was traced
        """
        string = ""
        if time > self.prevtime:
            string = ("__  Current Time: %10.6f " + "_"*42 + " \n") % (time / 1000)
        self.prevtime = time
        string += self.text + "\n"
        try:
            self.verb_file.write(string)
        except TypeError:
            self.verb_file.write(string.encode())
        self.text = ""
    
    def traceExitState(self, StateChart, State):
        self.text += "\n"
        self.text += "EXIT STATE in model <%s>\n" % StateChart
        self.text += "\t\tState: %s\n" % str(State)
        # TODO: This should be different because can also be written to a file, the DEVS implementation uses a server which i'm not going to do
        #print(text)

    def traceEnterState(self, StateChart, State):
        self.text += "\n"
        self.text += "ENTER STATE in model <%s>\n" % StateChart
        self.text += "\t\tState: %s\n" % str(State)
        #print(text)
    
    def traceOutput(self, event):
        self.text += "\n"
        self.text += "OUTPUT EVENT to port <%s>\n" % event.port
        self.text += "\t\Event: %s\n" % str(event)
        #print(text)

    def traceInput(self, listener, event):
        self.text += "\n"
        self.text += "INPUT EVENT from port <%s>\n" % event.port
        self.text += "\t\Type: %s\n" % listener.virtual_name
        self.text += "\t\Event: %s\n" % str(event)
        #print(text)

    def traceTransition(self, aStateChart):
        """
		Tracing done for the internal transition function

		:param aDEVS: the model that transitioned
		"""
        pass

    def traceExternal(self, aClass):
        """
        Tracing done for the external transition function

        :param aDEVS: the model that transitioned
        """
        pass

    def traceInit(self, aDEVS, t):
        """
        Tracing done for the initialisation

        :param aDEVS: the model that was initialised
        :param t: time at which it should be traced
        """
        pass
