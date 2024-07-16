import os
import shutil
import subprocess
import filecmp

def convert_sccd_to_target(test_path, target_dir, tool_name):
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

def run_runner_script(test_path, target_dir, tool):
    """
    Run the runner.py script in the context of the generated package.
    """
    runner_script = os.path.join(test_path, target_dir, 'runner.py')
    if not os.path.exists(runner_script):
        # Path to default runner.py
        runner_path = ""
        if tool == 'python':
            runner_path = os.path.join("TraceComparison", "Python_runner.py")
        elif tool == 'pypDEVS':
            runner_path = os.path.join("TraceComparison", "DEVS_runner.py")
        else:
            return None
        # Copy default runner.py to target_dir
        shutil.copy(runner_path, os.path.join(test_path, target_dir, 'runner.py'))
    
    command = ["python", runner_script]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {runner_script}: {result.stderr}")
    return result.stdout, result.stderr

def compare_logs(log1, log2):
    """
    Compare two log files and return if they are the same.
    """
    return filecmp.cmp(log1, log2, shallow=False)

def process_test(test_name, test_path):
    """
    Process a single test by converting, running, and comparing logs.
    """
    # Convert sccd.xml to target.py for Python and PyDEVS
    if convert_sccd_to_target(test_path, 'Python', 'python') != 0:
        return
    if convert_sccd_to_target(test_path, 'PyDEVS', 'pypDEVS') != 0:
        return
    
    # Run the runner.py script in the context of the generated package
    python_log, python_error = run_runner_script(test_path, 'Python', 'python')
    pydevs_log, pydevs_error = run_runner_script(test_path, 'PyDEVS', 'pypDEVS')
    
    # Save logs to files
    #python_log_file = os.path.join(test_path, 'Python', 'log.txt')
    #pydevs_log_file = os.path.join(test_path, 'PyDEVS', 'log.txt')
    
    #with open(python_log_file, 'w') as f:
    #    f.write(python_log)
    #    f.write(python_error)
    
    #with open(pydevs_log_file, 'w') as f:
    #    f.write(pydevs_log)
    #    f.write(pydevs_error)
    
    # Compare logs
    #if compare_logs(python_log_file, pydevs_log_file):
    #    print(f"Logs for test {test_name} match.")
    #else:
    #    print(f"Logs for test {test_name} do not match.")

if __name__ == '__main__':
    tests_directory = "./tests"
    # Read and sort directory names
    test_dirs = sorted([d for d in os.listdir(tests_directory) if os.path.isdir(os.path.join(tests_directory, d))])
    
    for test_name in test_dirs:
        test_path = os.path.join(tests_directory, test_name)
        if os.path.isdir(test_path):
            print(f"Processing {test_name}...")
            process_test(test_name, test_path)
