import os
import re
import subprocess
import importlib.util
from sccd.runtime.statecharts_core import Event
import TraceVerifier.DEVSTesterUnit as DEVSTesterUnit
from sccd.runtime.DEVSSimulatorWrapper import DEVSSimulator

def import_target_module(module_name, file_path):
    # Dynamically import a target module for the runner to execute
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class SCCDTraceChecker:
    '''
    Abstract class, this class defines the methods and parameters a custom trace checker 
    needs to function in the testing framework
    '''
    def __init__(self) -> None:
        self.config = None
        self.directory = None
        
    def compile(self):
        raise NotImplementedError("Compile method must be implemented by the subclass")

    def run(self):
        raise NotImplementedError("Run method must be implemented by the subclass")

    def filter(self):
        raise NotImplementedError("Check method must be implemented by the subclass")


class PythonSCCDTraceChecker(SCCDTraceChecker):
    def __init__(self) -> None:
        super().__init__()
        self.id_dict = {}
    
    def __str__(self):
        return "Python"

    def compile(self):
        '''
        Convert sccd.xml to target.py for the specified tool.
        '''
        sccd_file = os.path.join(self.directory, self.config['model'])
        output_file = os.path.join(self.directory, 'Python', 'target.py')
        os.makedirs(os.path.join(self.directory, 'Python'), exist_ok=True)

        command = [
            "python", 
            os.path.join("sccd", "compiler", "sccdc.py"), 
            "-o", output_file, 
            "-p", "threads", 
            "-l", "python", 
            sccd_file
        ]

        env = os.environ.copy()
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error converting {sccd_file} for python: {result.stderr}")
        return result.returncode

    def run(self):
        '''
        Run the model (target.py) with a defined execution function
        '''
        # Dynamically import the target module
        python_target = os.path.join(self.directory, "Python", "target.py")
        target = import_target_module("target", python_target)
        controller = target.Controller()
        controller.keep_running = False

        # Check if there is an input file for input events
        input_file = os.path.join(self.directory, self.config["input"])
        if os.path.exists(input_file):
            # add the inputs before the simulation is started with the correct event time 
            with open(input_file, 'r') as file:
                lines = file.readlines()
            input_events = [line.strip() for line in lines] 
            for event in input_events:
                space_pos = event.find(' ')
                if space_pos == -1:
                    raise ValueError("Line format is incorrect. No space found to split time and event.")
                
                # Extract the time and event parts
                next_event_time = float(event[:space_pos]) * 1000
                event_part = event[space_pos + 1:].strip()  # Strip to remove any leading/trailing whitespace

                name, port, parameters = DEVSTesterUnit.parse_event(event_part)
                # list is as string, convert it to actual list
                parameters = eval(parameters)
                actual_event = Event(name, port, parameters)
                controller.addInput(actual_event, next_event_time)

        # Create the full path for the log file
        log_file_path = os.path.join(self.directory, "Python", "log.txt")

        # Set verbose to the log file path
        controller.setVerbose(log_file_path)
        # Start the execution
        controller.start()
        controller.tracers.stopTracers()
    
    def extract_globalio(self, line, context):
        # Extract global output event from the line if present
        event_pattern = re.compile(r'^\s*\\Event: \(event name:.*\)$')
        event_match = event_pattern.match(line)
        if event_match and context["time"] is not None:
            if context["context"] == "global output":
                # Remove everything before the event string
                event = line.strip()
                event = event[event.index('('):]
                # Narrow casts are also matched by regex so filter these out
                if not "<narrow_cast>" in event:
                    return f"{context["time"]:.2f} {event}"
        return None
        
    def extract_internalio(self, line, context):
        # Extract internal events, e.g. events sended to and from the object manager and classes
        event_pattern = re.compile(r'^\s*\\Event: \(event name:.*\)$')
        event_match = event_pattern.match(line)

        if event_match and context["context"] is not None:
            if context["context"] == "internal input" or context["context"] == "internal output":
                # Remove everything before the event in string
                event = line.strip()
                event = event[event.index('('):]

                # Special for python SCCD, the first parameter is sometimes the source but the source is a memory address, give it a unique index 
                # So that it will match DEVS and is consistent in traces. 
                id_pattern = re.compile(
                    r'.*\(event name:.*; port:.*; parameters: \[\<[\w\.]+ object at (0x[0-9a-fA-F]+)\>.*\]'
                )
                id_match = id_pattern.search(event)
                if id_match:
                    address = id_match.group(1)
                    if address not in self.id_dict:
                        self.id_dict[address] = len(self.id_dict)

                    # Replace the entire object reference wit a unique id
                    start_idx = event.find('<')
                    end_idx = event.find('>', start_idx) + 1
                    if start_idx != -1 and end_idx != -1:
                        event = event[:start_idx] + str(self.id_dict[address]) + event[end_idx:]
                return f"{context["time"]:.2f} {event}"
        return None

    def extract_statechart(self, line, context):
        # extract statechart statements
        if line != "\n":
            if "TRANSITION FIRED" in line:
                context["extra_info"] = "transition"
            elif "EXIT STATE" in line:
                context["extra_info"] = "exit"
            elif "ENTER STATE" in line:
                context["extra_info"] = "enter"
            else:
                # Remove all unnecessary characters
                if context["extra_info"] == "transition":
                    line = line[line.index('('):line.rfind(')')+1]
                else:
                    line = line[line.index('/'):]
                line = line.replace('\n', '')
                line = line.replace('\t', '')
                return f"{context["time"]:.2f} {context['model']}: {context["extra_info"]} {line}"
        return None

    def check_state(self, line, context):
        time_pattern = re.compile(r"__  Current Time: +([\d\.]+) +__________________________________________")
        time_match = time_pattern.match(line)
        if time_match:
            context = {
                "time": float(time_match.group(1)),
                "model": None,
                "context": None,
                "extra_info": None
            }

        if "INPUT EVENT from <ObjectManager>" in line:
            context = {
                "time": context["time"],
                "context": "internal input",
            }
        elif "OUTPUT EVENT to <ObjectManager>" in line:
            context = {
                "time": context["time"],
                "context": "internal output",
            }
        elif "INPUT EVENT" in line:
            context = {
                "time": context["time"],
                "context": "global input",
            }
        elif "OUTPUT EVENT" in line:
            context = {
                "time": context["time"],
                "context": "global output",
                "extra_info": None
            }

        elif "EXIT STATE" in line:
            pattern = r"<(.*?)>"
            # Search for the pattern in the string
            match = re.search(pattern, line)
            context = {
                "time": context["time"],
                "model": match.group(1),
                "context": "state",
                "extra_info": "Exit "
            }
        
        elif "ENTER STATE" in line:
            pattern = r"<(.*?)>"
            # Search for the pattern in the string
            match = re.search(pattern, line)
            context = {
                "time": context["time"],
                "model": match.group(1),
                "context": "state",
                "extra_info": "Enter "
            }

        elif "TRANSITION FIRED" in line:
            pattern = r"<(.*?)>"
            # Search for the pattern in the string
            match = re.search(pattern, line)
            context = {
                "time": context["time"],
                "model": match.group(1),
                "context": "state",
                "extra_info": "Transition "
            }
        return context

    def filter(self):
        log = os.path.join(self.directory, "Python", "log.txt")
        output_events = []
        context = {
            "time": None,
            "model": None,
            "context": None,
            "extra_info": None
        }
        
        # Clean id dictionary for following test
        self.id_dict = {}
        with open(log, 'r') as file:
            lines = file.readlines()
            
            for line in lines:
                context = self.check_state(line, context)
                
                if "external" in self.config["trace"]:
                    io_event = self.extract_globalio(line, context)
                    if io_event is not None:
                        output_events.append(io_event)
                
                if "internal" in self.config["trace"]:
                    internal_event = self.extract_internalio(line, context)
                    if internal_event is not None:
                        output_events.append(internal_event)
                
                if "statechart" in self.config["trace"]:
                    if context['context'] == "state":
                        statechart_event = self.extract_statechart(line, context)
                        if statechart_event is not None:
                            output_events.append(statechart_event)
        return output_events


class ClassicDevsSCCDTraceChecker(SCCDTraceChecker):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self):
        return "ClassicDEVS"
    
    def compile(self):
        """
        Convert sccd.xml to target.py.
        """
        sccd_file = os.path.join(self.directory, self.config["model"])
        output_file = os.path.join(self.directory, "ClassicDEVS", 'target.py')

        os.makedirs(os.path.join(self.directory, "ClassicDEVS"), exist_ok=True)

        command = [
            "python", 
            os.path.join("sccd", "compiler", "sccdc.py"), 
            "-o", output_file, 
            "-p", "classicdevs", 
            sccd_file
        ]

        env = os.environ.copy()
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error converting {sccd_file} for ClassicDEVS: {result.stderr}")
        return result.returncode

    def run(self):
        # Dynamically import the target module
        pydevs_target = os.path.join(self.directory, "ClassicDEVS", "target.py")
        target = import_target_module("target", pydevs_target)

        # Check if there is an input file
        input_file = os.path.join(self.directory, self.config["input"])
        if not os.path.exists(input_file):
            input_file = None

        # Initialize the to be tested model
        test_model = target.Controller("Controller")

        # Add a new atomicDEVS to it which will be the Tester and link it to the model to sent events
        tester = test_model.addSubModel(DEVSTesterUnit.TesterUnit("Tester", input_file))

        # Connect the outports of the tester to the global inports of the model
        # Now directly connected to the atomicDEVS input because out/in relation can not be of coupled (SEE DEVS.PY)
        for in_port in test_model.IPorts:
            test_output = tester.addOutPort(f"Test_{in_port.name}")
            for atomic in test_model.atomics:
                test_model.connectPorts(test_output, atomic.input)

        # Connect the private ports (with their general names)
        for an_atomic in test_model.atomics:
            for private_port in an_atomic.IPorts:
                if private_port.name != 'obj_manager_in' and private_port.name != 'input':
                    test_output = tester.addOutPort(f"Test_{private_port.name}")
                    test_model.connectPorts(test_output, private_port)

        sim = DEVSSimulator(test_model)
        sim.setRealTime(False)
        
        # Add the verbose tracer to add traces to .txt file
        log_file_path = os.path.join(self.directory, "ClassicDEVS", "log.txt")
        sim.setVerbose(log_file_path)
        # Start the simulation correctly
        sim.setClassicDEVS()
        sim.simulate()

    def extract_globalio(self, line, context):
        event_pattern = re.compile(r'^\s*\(event name:.*\)$')
        event_match = event_pattern.match(line)
        if event_match and context["time"] is not None:
            event = line.strip()
            # Remove everything before '(' in each string
            event = event[event.index('('):]
            return f"{context["time"]:.2f} {event}"
        return None
        
    def extract_internalio(self, line, context):
        if (context["extra_info"] == "obj_manager_out" and context['transition_type'] == 'internal'):
            # Pattern to match the outermost '(event name: ...)' including a single nested '(event name: ...)'
            event_pattern = re.compile(r'\(event name:.*?(?:\(event name:.*?\))?.*?\)')
            event_match = re.search(event_pattern, line)
            if event_match and context["time"] is not None:
                event = event_match.group(0)
                # quick fix
                if "event name: narrow_cast" in event:
                    event += "])"
                return f"{context["time"]:.2f} {event}"
            
        elif (context["extra_info"] == "obj_manager_in" and context['transition_type'] == 'external') and ("<narrow_cast>" in line):
            event_pattern = r'\(event name.*?\)'
            event_matches = re.findall(event_pattern, line)
            if event_matches and context["time"] is not None:
                if len(event_matches) > 1:
                    pass
                # Get the last match
                event = event_matches[-1]
                return f"{context['time']:.2f} {event}"
        return None

    def extract_statechart(self, line, context):
        if line != "\n" and "\t\tNew State:" not in line:
            if "TRANSITION FIRED" in line:
                context["extra_info"] = "transition"
            elif "EXIT STATE" in line:
                context["extra_info"] = "exit"
            elif "ENTER STATE" in line:
                context["extra_info"] = "enter"
            else:
                if context["extra_info"] == "transition":
                    line = line[line.index('('):line.rfind(')')+1]
                    line = line.replace('\n', '')
                    line = line.replace('\t', '')  # Remove all tab character
                else:
                    line = line[line.index('/'):line.rfind(')')]
                    line = line.replace('\n', '')
                    line = line.replace('\t', '')  # Remove all tab characters
                return f"{context["time"]:.2f} {context['model']}: {context["extra_info"]} {line}"
        return None

    def check_state(self, line, context):
        if "EXTERNAL TRANSITION" in line:
            # Use regular expressions to find everything between <>
            pattern = r"<(.*?)>"
            # Search for the pattern in the string
            match = re.search(pattern, line)
            context = {
                "time": context["time"],
                "transition_type": "external",
                "model": match.group(1),
                "context": None,
                "extra_info": None
            }
        elif "INTERNAL TRANSITION" in line:
            # Use regular expressions to find everything between <>
            pattern = r"<Controller.(.*?)>"
            # Search for the pattern in the string
            match = re.search(pattern, line)
            context = {
                "time": context["time"],
                "transition_type": "internal",
                "model": match.group(1),
                "context": None,
                "extra_info": None
            }   
        elif "New State:" in line:
            context["context"] = "state"
        elif "Input Port Configuration:" in line:
            context["context"] = "input"
        elif "Output Port Configuration:" in line:
            context["context"] = "output"
        elif "Next scheduled internal transition at time" in line:
            context["context"] = "next"
        elif context["context"] == "input" and "obj_manager_in" in line:
            context["extra_info"] = "obj_manager_in"
        elif context["context"] == "output" and "obj_manager_out" in line:
            context["extra_info"] = "obj_manager_out"
        elif context["context"] == "output" and "port <" in line:
            context["extra_info"] = "other_port"
            
        return context

    def filter(self):
        log = os.path.join(self.directory, "ClassicDEVS", "log.txt")
        output_events = []
        current_time = None

        context = {
            "time": None,
            "transition_type": None,
            "model": None,
            "context": None,
            "extra_info": None
        }
        
        with open(log, 'r') as file:
            lines = file.readlines()
            
            time_pattern = re.compile(r"__  Current Time: +([\d\.]+) +__________________________________________")

            for line in lines:
                time_match = time_pattern.match(line)
                if time_match:
                    context["time"] = float(time_match.group(1))

                context = self.check_state(line, context)
                
                if "external" in self.config["trace"]:
                    io_event = self.extract_globalio(line, context)
                    if io_event is not None:
                        output_events.append(io_event)
                
                if "internal" in self.config["trace"]:
                    internal_event = self.extract_internalio(line, context)
                    if internal_event is not None:
                        output_events.append(internal_event)
                
                if "statechart" in self.config["trace"]:
                    if context['context'] == "state":
                        statechart_event = self.extract_statechart(line, context)
                        if statechart_event is not None:
                            output_events.append(statechart_event)
        
        return output_events