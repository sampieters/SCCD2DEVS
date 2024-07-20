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

    def check(self, directory):
        expected_log = os.path.join(directory, "expected_trace.txt")
        if os.path.exists(expected_log):
            lines_array = []
            with open(expected_log, 'r') as file:
                lines_array = file.readlines()
            return lines_array
        else:
            print(f"The file {expected_log} does not exist.")
            return None


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

    def check(self, directory):
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

        test_model = target.Controller("Controller")
        tester = Tester.Tester(test_model, input_file)

        sim = DEVSSimulator(tester)
        sim.setRealTime(False)
        
        # Create the full path for the log file
        log_file_path = os.path.join(directory, "PyDEVS", "log.txt")

        # Set verbose to the log file path
        sim.setVerbose(log_file_path)

        #sim.setClassicDEVS()
        sim.simulate()

    def extract_output_events(self, log_file_path):
        output_events = []
        current_time = None
        
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
            
            time_pattern = re.compile(r"__  Current Time: +([\d\.]+) +__________________________________________")
            event_pattern = re.compile(r'^\s*\(event name:.*\)$')
            
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

    def check(self, directory):
        log = os.path.join(directory, "PyDEVS", "log.txt")
        expected_log = os.path.join(directory, "expected_trace.txt")

        expected_events = []
        if os.path.exists(expected_log):
            with open(expected_log, 'r') as file:
                expected_events = [line.strip() for line in file.readlines()]

        actual_events = self.extract_output_events(log)

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