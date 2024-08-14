class BaseTracer:
	"""
	The baseclass for the tracers, allows for inheritance.
	"""
	def __init__(self):
		"""
		Constructor
		"""

	def startTracer(self, recover):
		"""
		Starts up the tracer

		:param recover: whether or not this is a recovery call (so whether or not the file should be appended to)
		"""
		pass

	def stopTracer(self):
		"""
		Stop the tracer
		"""
		pass

	def trace(self, time):
		"""
		Actual tracing function

		:param time: time at which this trace happened
		"""
		pass

	def traceInit(self, Statechart, t):
		pass

	def traceTransition(self, Transition):
		pass
	
	def traceExitState(self, StateChart, State):
		pass
	
	def traceEnterState(self, StateChart, State):
		pass

	def traceInternalInput(self, event):
		pass

	def traceInternalOutput(self, event):
		pass
	
	def traceOutput(self, event):
		pass 

	def traceInput(self, listener, event):
		pass 

