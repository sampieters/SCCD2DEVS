import os
import re
import subprocess
import importlib.util
from sccd.runtime.DEVS_loop import DEVSSimulator
import TraceChecker

def sort_directories(test_directory):
    with os.scandir(tests_directory) as entries:
        sorted_entries = sorted(entries, key=lambda entry: entry.name)
        sorted_items = [entry.name for entry in sorted_entries]
    
    # Read directory names
    all_test_dirs = [d for d in os.listdir(tests_directory) if os.path.isdir(os.path.join(tests_directory, d))]
    # Sort the list of directories using natural sort
    return sorted(all_test_dirs, key=natural_sort_key)

def natural_sort_key(s):
    # Split the string into a list of strings and numbers
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

if __name__ == '__main__':
    # ANSI color escape codes
    RED = '\033[91m'    # Red color
    GREEN = '\033[92m'  # Green color
    YELLOW = '\033[93m' # Yellow color
    ENDC = '\033[0m'    # Reset color to default

    tests_directory = "./tests"

    sorted_dirs = sort_directories(tests_directory)

    checkers = {
        "Python": TraceChecker.PythonSCCDTraceChecker(),
        "Pydevs": TraceChecker.PydevsSCCDTraceChecker()
    }

    results = {checker_name: [] for checker_name in checkers}

    for directory_name in sorted_dirs:
        full_directory = os.path.join(tests_directory, directory_name)
        if os.path.isdir(full_directory):
            print(f"Processing {directory_name}...")
            for checker_name, checker in checkers.items():
                checker.compile(full_directory)
                checker.run(full_directory)
                result = checker.check(full_directory)
                results[checker_name].append(result)
                if result == 0:
                    print(f"{checker_name}: ", RED + "Failed" + ENDC)
                elif result == 1:
                    print(f"{checker_name}: ", GREEN + "Passed" + ENDC)
                else:
                    print(f"{checker_name}: ", YELLOW + "Need more detailed testing" + ENDC)

    # Print summary
    print("\nTest Summary:")
    for checker_name in checkers:
        print(f"\n{checker_name} Results:")
        print(f"Passed: {GREEN}{results[checker_name].count(1)}{ENDC}")
        print(f"Failed: {RED}{results[checker_name].count(0)}{ENDC}")
        print(f"Warnings: {YELLOW}{results[checker_name].count(2)}{ENDC}")
