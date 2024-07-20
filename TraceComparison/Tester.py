import re
from pypdevs.DEVS import *
from pypdevs.simulator import Simulator
from sccd.runtime.DEVS_statecharts_core import Event
from pypdevs.infinity import INFINITY

import tests.Test3.PyDEVS.target as target

def parse_event(line):
    # Regular expression to match the desired parts of the line
    pattern = re.compile(r'\(event name: (.*?); port: (.*?); parameters: (.*?)\)$')
    match = pattern.match(line)
    if match:
        event_name = match.group(1)
        port = match.group(2)
        parameters = match.group(3)
        return event_name, port, parameters
    else:
        raise ValueError(f"Line format is incorrect: {line}")

class TesterUnit(AtomicDEVS):
    def __init__(self, name, inputfile=None):
        AtomicDEVS.__init__(self, name)

        self.events = []
        if inputfile is not None:
            with open(inputfile, 'r') as file:
                lines = file.readlines()
            self.events = [line.strip() for line in lines]

        self.total_time = 0
        self.next_event_time = 0

        self.to_send = []


        self.first = True
    
    def extTransition(self, inputs):
        pass

    def intTransition(self):
        self.total_time += self.next_event_time

        self.to_send = []
        if self.events:
            event = self.events[0]

            space_pos = event.find(' ')
            if space_pos == -1:
                raise ValueError("Line format is incorrect. No space found to split time and event.")
            
            # Extract the time and event parts
            self.next_event_time = float(event[:space_pos]) - self.total_time
            event_part = event[space_pos + 1:].strip()  # Strip to remove any leading/trailing whitespace

            name, port, parameters = parse_event(event_part)
            actual_event = Event(name, port, parameters)
            self.to_send.append(actual_event)

            self.events = self.events[1:]
        else:
            self.next_event_time = INFINITY

    def outputFnc(self):
        to_output = {}
        for event in self.to_send:
            for port in self.OPorts:
                if event.port == port.name:
                    #to_output[port] = event
                    if port in to_output:
                        to_output[port].append(event)
                    else:
                        to_output[port] = [event]
        return to_output

    def timeAdvance(self):
        return self.next_event_time
    

class Tester(CoupledDEVS):
    def __init__(self, model, inputfile=None):
        CoupledDEVS.__init__(self, "Tester")

        self.model = self.addSubModel(model)
        self.tester = self.addSubModel(TesterUnit("Tester", inputfile))

        # Connect to global ports
        for model_input_ports in self.model.IPorts:
            an_output = self.tester.addOutPort(name=model_input_ports.name)
            self.connectPorts(an_output, model_input_ports)