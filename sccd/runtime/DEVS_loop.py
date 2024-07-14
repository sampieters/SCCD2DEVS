from pypdevs.simulator import Simulator
import re

def get_port(text):
	match = re.search(r'private_\d+_(\w+)', text)

	if match:
		result = match.group(1)
		return result
	else:
		return text


class DEVSSimulator(Simulator):
	def __init__(self, model, inputs={}):
		super().__init__(model)
		self.setRealTimePorts(inputs)	
	
	def addInput(self, event):
		port_name = get_port(event.port)
		event_string = f"Event(\"{event.name}\",\"{event.port}\",{event.parameters})"
		event_string = event_string.replace(" ", "")
		interrupt_string = f"{port_name} {event_string}"
		self.realtime_interrupt(interrupt_string)
