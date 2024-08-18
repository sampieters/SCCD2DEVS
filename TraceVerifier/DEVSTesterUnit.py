import re
from pypdevs.DEVS import *
from sccd.runtime.DEVS_statecharts_core import Event
from sccd.runtime.libs import DEVSutils
from pypdevs.infinity import INFINITY

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

        # Open the input file and write lines to an array
        self.events = []
        if inputfile is not None:
            with open(inputfile, 'r') as file:
                lines = file.readlines()
            self.events = [line.strip() for line in lines]

        self.simulated_time = 0
        self.next_event_time = 0
        self.to_send = []

    def intTransition(self):
        # Update simulate time and clear the previous sended events
        self.simulated_time += self.next_event_time
        self.to_send = []

        if self.events:
            # Process events one at a time (for tracing purposes)
            event = self.events[0]
            # Check if line is correct. If not halt the simulation
            space_pos = event.find(' ')
            if space_pos == -1:
                raise ValueError("Line format is incorrect. No space found to split time and event.")
            # Extract the time and event part of a line
            self.next_event_time = float(event[:space_pos]) - self.simulated_time
            event_part = event[space_pos + 1:].strip()
            # Create an Event for SCCD and convert parameters to the proper format (String -> List)
            name, port, parameters = parse_event(event_part)
            actual_event = Event(name, port, eval(parameters))
            self.to_send.append(actual_event)
            self.events = self.events[1:]
        else:
            self.next_event_time = INFINITY

    def outputFnc(self):
        to_output = {}
        for event in self.to_send:
            # Check the corresponding port the event needs to be sended from
            for port in self.OPorts:
                real_port = DEVSutils.get_general_port(event.port)
                if f"Test_{real_port}" == port.name:
                    to_output[port] = [event]
        return to_output

    def timeAdvance(self):
        return self.next_event_time
    