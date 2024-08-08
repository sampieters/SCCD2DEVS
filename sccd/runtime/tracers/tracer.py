class Tracers(object):
    """
    Interface for all tracers
    """
    def __init__(self):
        """
        Constructor
        """
        self.tracers = []
        self.tracers_init = []
        self.uid = 0

    def registerTracer(self, tracer, server, recover):
        """
        Register a tracer, so that it will also receive all transitions.

        :param tracer: tuple of the form (file, classname, [args])
        :param server: the server object to be able to make remote calls
        :param recover: whether or not this is a recovered registration (used during checkpointing)
        """
        loc = {}
        try:
            exec("from sccd.runtime.tracers.%s import %s" % (tracer[0], tracer[1]), {}, loc)
        except:
            exec("from %s import %s" % (tracer[0], tracer[1]), {}, loc)
        self.tracers.append(loc[tracer[1]](*tracer[2]))
        self.tracers_init.append(tracer)
        self.uid += 1
        self.tracers[-1].startTracer(recover)

    def hasTracers(self):
        """
        Checks whether or not there are any registered tracers

        :returns: bool
        """
        return len(self.tracers) > 0

    def getByID(self, uid):
        """
        Gets a tracer by its UID

        :param uid: the UID of the tracer to return
        :returns: tracer
        """
        return self.tracers[uid]

    def stopTracers(self):
        """
        Stop all registered tracers
        """
        for tracer in self.tracers:
            tracer.stopTracer()

    def traces(self, time):
        for tracer in self.tracers:
            try:
                tracer.trace(time)
            except AttributeError:
                pass


    def tracesUser(self, time, aDEVS, variable, value):
        """
        Perform all tracing actions for a user imposed modification. This is NOT supported by default DEVS, so we don't require tracers to handle this either.

        :param time: the time at which the modification happend; this will be the termination time of the previous simulation run and **not** the time at which the timeAdvance was recomputed!
        :param aDEVS: the atomic DEVS model that was altered
        :param variable: the variable that was altered (as a string)
        :param value: the new value of the variable
        """
        for tracer in self.tracers:
            try:
                tracer.traceUser(time, aDEVS, variable, value)
            except AttributeError:
                # Some tracers choose to ignore this event
                pass

    def tracesInit(self, aDEVS, t):
        """
        Perform all tracing actions for an initialisation
        
        :param aDEVS: the model that was initialised
        :param t: the time at which the initialisation should be logged
        """
        if aDEVS.full_name is None:
            return
        for tracer in self.tracers:
            tracer.traceInit(aDEVS, t)
    
    def tracesExitState(self, StateChartName, StateName):
        if StateChartName is None:
            return
        for tracer in self.tracers:
            tracer.traceExitState(StateChartName, StateName)

    def tracesEnterState(self, StateChartName, StateName):
        if StateChartName is None:
            return
        for tracer in self.tracers:
            tracer.traceEnterState(StateChartName, StateName)
        
    def tracesTransition(self, StateChartName, Transition):
        if StateChartName is None:
            return
        for tracer in self.tracers:
            tracer.traceTransition(StateChartName, Transition)

    def tracesInternalOutput(self, event):
        for tracer in self.tracers:
            tracer.traceInternalOutput(event)
    
    def tracesInternalInput(self, event):
        for tracer in self.tracers:
            tracer.traceInternalInput(event)

    def tracesOutput(self, event):
        for tracer in self.tracers:
            tracer.traceOutput(event)

    def tracesInput(self, listener, event):
        if listener is None:
            return
        for tracer in self.tracers:
            tracer.traceInput(listener, event)

