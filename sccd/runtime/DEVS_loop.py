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
		self.setClassicDEVS()

		# TODO: Add the input ports here so it works without manually adding them
		inputs ={}

		# Add global inports
		for global_in in model.IPorts:
			inputs[global_in.name] = global_in

		# Add private ports (can't send to it unless it knows the id)
		for aclass in model.atomics:
			for in_port in aclass.IPorts:
				if in_port.name == "obj_manager_in" or in_port.name == "input":
					pass
				else:
					inputs[in_port.name] = in_port

		self.setRealTimePorts(inputs)	
	
	def addInput(self, event):
		port_name = get_port(event.port)
		event_string = f"Event(\"{event.name}\",\"{event.port}\",{event.parameters})"
		event_string = event_string.replace(" ", "")
		interrupt_string = f"{port_name} {event_string}"
		self.realtime_interrupt(interrupt_string)
