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
		:param text: the text that was traced
		"""
		pass
	
	def traceExitState(self, StateChart, State):
		pass
	
	def traceEnterState(self, StateChart, State):
		pass
	
	def traceOutput(self, event):
		pass 

	def traceInput(self, listener, event):
		pass 
	
	def traceTransition(self, Transition):
		"""
		Tracing done for the internal transition function

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
