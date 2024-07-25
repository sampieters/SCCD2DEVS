import os
import subprocess
import importlib.util
import re
from sccd.runtime.DEVS_loop import DEVSSimulator
import Tester

def import_target_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def extract_pattern(log_file_path, pattern):
    with open(log_file_path, 'r') as log_file:
        lines = log_file.readlines()

    matched_lines = [line.strip() for line in lines if re.search(pattern, line)]
    return matched_lines

class SCCDTraceChecker:
    def compile(self, directory):
        raise NotImplementedError("Compile method must be implemented by the subclass")

    def run(self, directory):
        raise NotImplementedError("Run method must be implemented by the subclass")

    def check(self, directory, options):
        raise NotImplementedError("Chekc method must be implemented by the subclass")


class PythonSCCDTraceChecker(SCCDTraceChecker):
    def __init__(self) -> None:
        super().__init__()
    
    def __str__(self):
        return "Python"

    def compile(self, directory):
        """
        Convert sccd.xml to target.py for the specified tool.
        """
        sccd_file = os.path.join(directory, 'sccd.xml')
        output_file = os.path.join(directory, 'Python', 'target.py')

        os.makedirs(os.path.join(directory, 'Python'), exist_ok=True)

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

    def run(self, directory):
        python_target = os.path.join(directory, "Python", "target.py")

        # Dynamically import the target module
        target = import_target_module("target", python_target)

        controller = target.Controller()
        controller.keep_running = False

        # Create the full path for the log file
        log_file_path = os.path.join(directory, "Python", "log.txt")

        # Set verbose to the log file path
        controller.setVerbose(log_file_path)

        controller.start()

        controller.tracers.stopTracers()
    
    def extract_output_events(self, log_file_path):
        output_events = []
        current_time = None
        
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
            
            time_pattern = re.compile(r"__  Current Time: +([\d\.]+) +__________________________________________")
            event_pattern = re.compile(r'^\s*\\Event: \(event name:.*\)$')
            
            for line in lines:
                time_match = time_pattern.match(line)
                if time_match:
                    current_time = float(time_match.group(1))
                
                event_match = event_pattern.match(line)
                if event_match and current_time is not None:
                    event = line.strip()
                    # Remove everything before '(' in each string
                    event = event[event.index('('):]
                    output_events.append(f"{current_time:.2f} {event}")
        
        return output_events

    def check(self, directory, options):
        log = os.path.join(directory, "Python", "log.txt")

        expected_log = os.path.join(directory, "expected_trace.txt")

        expected_events = []
        if os.path.exists(expected_log):
            with open(expected_log, 'r') as file:
                expected_events = [line.strip() for line in file.readlines()]

        actual_events = self.extract_output_events(log)

        if len(expected_events) != len(actual_events):
            return 0

        if len(expected_events) == 0 and len(actual_events) == 0:
            return 2

        for index, (item1, item2) in enumerate(zip(expected_events, actual_events)):
            if item1 != item2:
                return 0
        return 1


class PydevsSCCDTraceChecker(SCCDTraceChecker):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self):
        return "PyDEVS"
    
    def compile(self, directory):
        """
        Convert sccd.xml to target.py for the specified tool.
        """
        sccd_file = os.path.join(directory, 'sccd.xml')
        output_file = os.path.join(directory, "PyDEVS", 'target.py')

        os.makedirs(os.path.join(directory, "PyDEVS"), exist_ok=True)

        command = [
            "python", 
            os.path.join("sccd", "compiler", "sccdc.py"), 
            "-o", output_file, 
            "-p", "pypDEVS", 
            sccd_file
        ]

        env = os.environ.copy()
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error converting {sccd_file} for PyDEVS: {result.stderr}")
        return result.returncode

    def run(self, directory):
        '''
        pydevs_target = os.path.join(directory, "PyDEVS", "target.py")
        # Dynamically import the target module
        target = import_target_module("target", pydevs_target)
        model = target.Controller(name="controller")
        refs = {"ui": model.in_ui}
        sim = DEVSSimulator(model, refs)
        sim.setRealTime(False)

        # Create the full path for the log file
        log_file_path = os.path.join(directory, "PyDEVS", "log.txt")

        # Set verbose to the log file path
        sim.setVerbose(log_file_path)

        sim.simulate()
        '''
        # Dynamically import the target module
        pydevs_target = os.path.join(directory, "PyDEVS", "target.py")
        target = import_target_module("target", pydevs_target)

        # Check if there is an input file
        input_file = os.path.join(directory, "input.txt")
        if not os.path.exists(input_file):
            input_file = None

        # Initialize the to be tested model
        test_model = target.Controller("Controller")

        # Add a new atomicDEVS to it which will be the Tester and link it to the model to sent events
        tester = test_model.addSubModel(Tester.TesterUnit("Tester", input_file))

        # Connect the outports of the tester to the global inports of the model
        # TODO: Now directly connected to the atomicDEVS because out/in relation can not be of coupled (SEE DEVS.PY)
        for in_port in test_model.IPorts:
            test_output = tester.addOutPort(f"Test_{in_port.name}")
            for atomic in test_model.atomics:
                test_model.connectPorts(test_output, atomic.input)


        #tester = Tester.Tester(test_model, input_file)

        sim = DEVSSimulator(test_model)
        sim.setRealTime(False)
        
        # Create the full path for the log file
        log_file_path = os.path.join(directory, "PyDEVS", "log.txt")

        # Set verbose to the log file path
        sim.setVerbose(log_file_path)

        #sim.setClassicDEVS()
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
        return None

    def extract_statechart(self, line, context):
        if line != "\n" and "\t\tNew State:" not in line:
            if "TRANSITION FIRED" in line:
                context["extra_info"] = ""
            elif "EXIT STATE" in line:
                context["extra_info"] = "Exit "
            elif "ENTER STATE" in line:
                context["extra_info"] = "Enter "
            else:
                line = line.replace('\n', '')
                line = line.replace('\t', '')  # Remove all tab characters
                return f"{context["time"]:.2f} {context["extra_info"]}{line}"
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
            pattern = r"<(.*?)>"
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
        elif "Output Port Configuration:" in line:
            context["context"] = "input"
        elif "Output Port Configuration:" in line:
            context["context"] = "output"
        elif "Next scheduled internal transition at time" in line:
            context["context"] = "next"
        return context
    
    def extract_info(self, log_file_path, options):
        output_events = []
        current_time = None

        context = {
            "time": None,
            "transition_type": None,
            "model": None,
            "context": None,
            "extra_info": None
        }
        
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
            
            time_pattern = re.compile(r"__  Current Time: +([\d\.]+) +__________________________________________")

            for line in lines:
                time_match = time_pattern.match(line)
                if time_match:
                    context["time"] = float(time_match.group(1))

                context = self.check_state(line, context)
                
                if "GLOBAL_IO" in options:
                    io_event = self.extract_globalio(line, context)
                    if io_event is not None:
                        output_events.append(io_event)
                
                if "INTERNAL_IO" in options:
                    internal_event = self.extract_internalio(line, context)
                    if internal_event is not None:
                        output_events.append(internal_event)
                
                if "STATECHART" in options:
                    if context['context'] == "state":
                        statechart_event = self.extract_statechart(line, context)
                        if statechart_event is not None:
                            output_events.append(statechart_event)
        
        return output_events

    def check(self, directory, options):
        log = os.path.join(directory, "PyDEVS", "log.txt")
        expected_log = os.path.join(directory, "expected_trace.txt")

        expected_events = []
        if os.path.exists(expected_log):
            with open(expected_log, 'r') as file:
                expected_events = [line.strip() for line in file.readlines()]
        
        actual_events = self.extract_info(log, options)

        return_code = 1
        if len(expected_events) != len(actual_events):
            return_code = 0

        if len(expected_events) == 0 and len(actual_events) == 0:
            return_code = 2

        for index, (item1, item2) in enumerate(zip(expected_events, actual_events)):
            if item1 != item2:
                return_code = 0

        if return_code == 0:
            # Write actual events to a file
            with open(os.path.join(directory, "PyDEVS", "faulty_log.txt"), 'w') as file:
                file.writelines([event + '\n' for event in actual_events])

        return return_code