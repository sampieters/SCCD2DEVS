import os
import re
import json
import shutil
import difflib
import argparse
import TraceChecker

# ANSI color escape codes
RED = '\033[91m'    # Red color
GREEN = '\033[92m'  # Green color
YELLOW = '\033[93m' # Yellow color
ENDC = '\033[0m'    # Reset color to default

def sort_directories(test_directory):
    # Read directory names and sort using natural sort
    all_test_dirs = [d for d in os.listdir(test_directory) if os.path.isdir(os.path.join(test_directory, d))]
    return sorted(all_test_dirs, key=natural_sort_key)

def natural_sort_key(s):
    # Split the string into a list of strings and numbers
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

if __name__ == '__main__':
    # Create the parser to get arguments of command line
    parser = argparse.ArgumentParser(description="Process a test folder.")
    parser.add_argument(
        '-i', '--input', 
        type=str, 
        required=True, 
        help='Path to the test folder'
    )

    parser.add_argument(
        '-c', '--clear', 
        action='store_true', 
        help='Clear the output after execution'
    )

    args = parser.parse_args()
    source = args.input

    # Define the default configuration if no configuration file is given 
    default_config = {
        "model": "sccd.xml",
        "input": "input.txt",
        "trace": "external",
        "platforms": ["Python", "ClassicDEVS"],
        "check_file": "expected_trace.txt"
    }

    # Add here all possible platforms (Not only the one that need to be tested but all --> resolved in config file)
    platforms = [TraceChecker.PythonSCCDTraceChecker(), TraceChecker.ClassicDevsSCCDTraceChecker()]
    sorted_dirs = sort_directories(source)
    results = {str(platform): [] for platform in platforms}
    for directory_name in sorted_dirs:
        full_directory = os.path.join(source, directory_name)
        if os.path.isdir(full_directory):
            print(f"Processing {directory_name}...")
            # Check if a user defined config exists otherwise default to the default config file
            config_file = os.path.join(full_directory, 'config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as file:
                    config_data = json.load(file)
                    # If an option in user config is empty, replace with default
                    for key, value in default_config.items():
                        if key not in config_data:
                            config_data[key] = value
            else:
                # If there is no config file found in the test, give the default config file
                config_data = default_config
            for platform in platforms:
                platform_name = str(platform)
                # For each platform to be checked for the test, compile, run, and filter necessary traces
                if platform_name in config_data['platforms']:
                    platform.directory = full_directory
                    platform.config = config_data

                    platform.compile()
                    platform.run()
                    result = platform.filter()
                    # Open the log to be compared to and write them in same format as filtered traces (list of strings)
                    expected_log = os.path.join(full_directory, config_data["check_file"])
                    expected_events = []
                    if os.path.exists(expected_log):
                        with open(expected_log, 'r') as file:
                            expected_events = [line.strip() for line in file.readlines()]
                    # Compare traces
                    return_code = 1
                    # If both traces are not the same in length, test fails
                    if len(expected_events) != len(result):
                        return_code = 0
                    # If one of the trace files is empty, likely not a good option in config file
                    if len(expected_events) == 0 and len(result) == 0:
                        return_code = 2
                    # Check if each line is exactly the same in both files
                    for index, (line1, line2) in enumerate(zip(expected_events, result)):
                        if line1 != line2:
                            return_code = 0
                    results[platform_name].append(return_code)
                    # Notice the user about the test (by printing in terminal)
                    if return_code == 0:
                        print(f"{platform_name}: ", RED + "Failed" + ENDC)
                        # If test fails, write the traces to a log for checking
                        faulty_log = os.path.join(full_directory, platform_name, "faulty_log.txt")
                        with open(faulty_log, 'w') as file:
                            file.writelines([event + '\n' for event in result])
                        # Use the difflib package to check on a deeper level what is different
                        with open(expected_log, "r") as f1, open(faulty_log, "r") as f2:
                            diff = difflib.unified_diff(f1.readlines(), f2.readlines(), fromfile=expected_log, tofile=faulty_log)
                            for line in diff:
                                print("\t" + line)
                    elif return_code == 1:
                        print(f"{platform_name}: ", GREEN + "Passed" + ENDC)
                    else:
                        print(f"{platform_name}: ", YELLOW + "Need more detailed testing" + ENDC)

    # Print summary
    print("\nTest Summary:")
    for platform in platforms:
        platform_name = str(platform)
        print(f"\n{platform_name} Results:")
        print(f"Passed: {GREEN}{results[platform_name].count(1)}{ENDC}")
        print(f"Failed: {RED}{results[platform_name].count(0)}{ENDC}")
        print(f"Warnings: {YELLOW}{results[platform_name].count(2)}{ENDC}")

    # If clear option (-c) is specified, perform the clear operation
    if args.clear:
        print("Resetting environment...")
        # Iterate over each folder inside the parent directory
        for folder_name in os.listdir(source):
            folder_path = os.path.join(source, folder_name)
            # Check if the path is a directory and not a file
            if os.path.isdir(folder_path):
                for platform in platforms:
                    platform_name = str(platform)
                    path = os.path.join(folder_path, platform_name)
                    if os.path.exists(path):
                        shutil.rmtree(path)
                        print(f"Deleted {path}")