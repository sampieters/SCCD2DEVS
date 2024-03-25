from pypdevs.simulator import Simulator

class DEVSSimulator(Simulator):
	def __init__(self, model):
		Simulator.__init__(self, model)	
	
	def addInput(self, event):
		event_string = f"Event(\"{event.name}\",\"{event.port[0]}\",{event.parameters},{event.port[1]})"
		event_string = event_string.replace(" ", "")
		interrupt_string = f"{event.port[0]} {event_string}"
		self.realtime_interrupt(interrupt_string)