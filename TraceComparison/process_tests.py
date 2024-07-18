import os
import re
import subprocess
import importlib.util
from sccd.runtime.DEVS_loop import DEVSSimulator


def import_target_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def compile_to_target(test_path, target_dir, tool_name):
    """
    Convert sccd.xml to target.py for the specified tool.
    """
    sccd_file = os.path.join(test_path, 'sccd.xml')
    output_file = os.path.join(test_path, target_dir, 'target.py')

    os.makedirs(os.path.join(test_path, target_dir), exist_ok=True)

    command = []
    if tool_name == "python":
        command = [
            "python", 
            os.path.join("sccd", "compiler", "sccdc.py"), 
            "-o", output_file, 
            "-p", "threads", 
            "-l", tool_name, 
            sccd_file
        ]
    elif tool_name == "pypDEVS":
        command = [
            "python", 
            os.path.join("sccd", "compiler", "sccdc.py"), 
            "-o", output_file, 
            "-p", tool_name, 
            sccd_file
        ]

    env = os.environ.copy()
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error converting {sccd_file} for {tool_name}: {result.stderr}")
    return result.returncode

def run_python_sccd(full_directory):
    python_target = os.path.join(full_directory, "Python", "target.py")

    # Dynamically import the target module
    target = import_target_module("target", python_target)

    controller = target.Controller()
    controller.keep_running = False

    # Create the full path for the log file
    log_file_path = os.path.join(full_directory, "Python", "log.txt")

    # Set verbose to the log file path
    controller.setVerbose(log_file_path)

    controller.start()

    controller.tracers.stopTracers()

def run_pydevs_sccd(full_directory):
    pydevs_target = os.path.join(full_directory, "PyDEVS", "target.py")
    # Dynamically import the target module
    target = import_target_module("target", pydevs_target)
    model = target.Controller(name="controller")
    refs = {"ui": model.in_ui}
    sim = DEVSSimulator(model, refs)
    sim.setRealTime(False)

	# Create the full path for the log file
    log_file_path = os.path.join(full_directory, "PyDEVS", "log.txt")

	# Set verbose to the log file path
    sim.setVerbose(log_file_path)

    sim.simulate()

def natural_sort_key(s):
    # Split the string into a list of strings and numbers
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def extract_pattern(log_file_path, pattern):
    """
    Extract lines from a log file that match a given pattern.

    Args:
        log_file_path (str): Path to the log file.
        pattern (str): Regular expression pattern to match lines.

    Returns:
        list: List of matched lines.
    """
    with open(log_file_path, 'r') as log_file:
        lines = log_file.readlines()

    matched_lines = [line.strip() for line in lines if re.search(pattern, line)]
    return matched_lines

def extract_devs_output_events(log_file_path):
    pattern = r'^\s*\(event name:.*\)$'
    return extract_pattern(log_file_path, pattern)

def extract_python_output_events(log_file_path):
    pattern = r'^\s*\\Event: \(event name:.*\)$'
    events = extract_pattern(log_file_path, pattern)
    # Remove everything before '(' in each string
    return [event[event.index('('):] for event in events]

def check_traces(full_directory):
    pydevs_log = os.path.join(full_directory, "PyDEVS", "log.txt")
    python_log = os.path.join(full_directory, "Python", "log.txt")

    pydevs_output_events = extract_devs_output_events(pydevs_log)
    python_output_events = extract_python_output_events(python_log)


    if len(pydevs_output_events) != len(python_output_events):
        return 0

    if len(pydevs_output_events) == 0 and len(python_output_events) == 0:
        return 2

    differences_found = False
    for index, (item1, item2) in enumerate(zip(pydevs_output_events, python_output_events)):
        if item1 != item2:
            print(f"Difference at index {index}:")
            print(f"   List 1 ({len(pydevs_output_events)} elements): {item1}")
            print(f"   List 2 ({len(python_output_events)} elements): {item2}")
            differences_found = True

    if differences_found:
        return 0
    else:
        return 1

if __name__ == '__main__':
    # ANSI color escape codes
    RED = '\033[91m'    # Red color
    GREEN = '\033[92m'  # Green color
    YELLOW = '\033[93m' # Yellow color
    ENDC = '\033[0m'    # Reset color to default

    tests_directory = "./tests"

    with os.scandir(tests_directory) as entries:
        sorted_entries = sorted(entries, key=lambda entry: entry.name)
        sorted_items = [entry.name for entry in sorted_entries]
    
    # Read directory names
    all_test_dirs = [d for d in os.listdir(tests_directory) if os.path.isdir(os.path.join(tests_directory, d))]
    # Sort the list of directories using natural sort
    sorted_dirs = sorted(all_test_dirs, key=natural_sort_key)
    
    results = []
    for directory_name in sorted_dirs:
        full_directory = os.path.join(tests_directory, directory_name)
        if os.path.isdir(full_directory):
            print(f"Processing {directory_name}...")
            if compile_to_target(full_directory, 'Python', 'python') != 0:
                raise RuntimeError("Could not compile to python model")
            if compile_to_target(full_directory, 'PyDEVS', 'pypDEVS') != 0:
                raise RuntimeError("Could not compile to pyDEVS model")
            run_python_sccd(full_directory)
            run_pydevs_sccd(full_directory)

            result = check_traces(full_directory)
            results.append(result)

            if result == 0:
                print(RED + "Failed" + ENDC)
            elif result == 1:
                print(GREEN + "Passed" + ENDC)
            else:
                print(YELLOW + "Check deeper" + ENDC)

    # Print summary
    print("\nTest Summary:")
    print(f"Passed: {GREEN}{results.count(1)}{ENDC}")
    print(f"Failed: {RED}{results.count(0)}{ENDC}")
    print(f"Check deeper: {YELLOW}{results.count(2)}{ENDC}")

