import re

def extract_float(text):
    # Define a regex pattern to match the float value
    pattern = r"Current Time:\s+([-+]?\d*\.\d+|\d+)"
    
    # Search for the pattern in the text
    match = re.search(pattern, text)
    
    if match:
        # Extract the matched float value
        float_value = float(match.group(1))
        return float_value
    else:
        # Handle the case where no match is found
        return None

def extract_type(text):
    # Define a regex pattern to match the type value after 'Type:'
    pattern = r"Type:\s*(\w+)"
    
    # Search for the pattern in the text
    match = re.search(pattern, text)
    
    if match:
        # Extract the matched type value
        type_value = match.group(1)
        return type_value
    else:
        # Handle the case where no match is found
        return None
    
def extract_event_details(text):
    #pattern = r"event name:\s*([^;]+);\s*port:\s*([^;]+)(?:;\s*parameters:\s*(\[.*\]))?"
    pattern = r"event name:\s*([^;]+);\s*port:\s*([^\);]+)(?:;\s*parameters:\s*(\[.*\]))?"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        event_name = match.group(1).strip()
        port = match.group(2).strip()
        parameters = match.group(3).strip() if match.group(3) else 'None'
        return event_name, port, parameters
    else:
        return None, None, None


def generate_input_trace(input_trace, output_file):
    # Open the file in read mode
    with open(input_trace, 'r') as file:
        # Read all lines into a list
        lines = file.readlines()

    # Open the file in write mode ('w')
    with open(output_file, 'w') as file:
        # Traverse each line in the file
        i = 0
        current_time = None
        while i < len(lines):
            if lines[i].startswith('__'):
                current_time = extract_float(lines[i].strip())

            # Check if the line starts with 'INPUT'
            if lines[i].startswith('INPUT'):
                # Print the line that starts with 'INPUT'
                print(lines[i].strip())
                # Check if the next two lines exist and print them
                the_type = extract_type(lines[i + 1].strip())
                name, port, parameters = extract_event_details(lines[i + 2].strip())

                if name == None:
                    name = 'None'
                if port == None:
                    port = 'None'
                if parameters == None:
                    parameters = 'None'


                if the_type is not None:
                    to_write = str(current_time) + " " + the_type + " Event(\"" + name + "\",\"" + port + "\"," + parameters + ")\n"
                    file.write(to_write)            

                # Skip the next two lines to avoid reprocessing them
                i += 2
            # Move to the next line
            i += 1

def filter_lines(lines, filter_func):
    """
    Filter lines based on the provided filter function.
    """
    return [line for line in lines if not filter_func(line)]

def read_and_filter_file(file_path, filter_func):
    """
    Read a file and filter its lines using the filter function.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return filter_lines(lines, filter_func)

# Fitler, filtering what should be ignored
temp = False
def devs_filter(line):
    global temp
    if line.startswith('\tEXTERNAL'):
        temp = True
    
    if temp and line.startswith('\n'):
        temp = False

    condition = not line.startswith('\tEXTERNAL') and not line.startswith('__') and not temp

    return condition

i = 0
def sccd_filter(line):
    global i 

    if line.startswith('INPUT'):
        i = 2

    condition = (not line.startswith('INPUT') and not line.startswith('__'))

    if not line.startswith('INPUT') and i != 0:
        condition = False
        i -= 1
    return condition

def write_filtered_lines_to_file(filtered_lines, output_path):
    """
    Write the filtered lines to a file.
    """
    with open(output_path, 'w') as file:
        file.writelines(filtered_lines)

def compare_traces(file1_path, file2_path):
    """
    Compare two files line by line after filtering them.
    """

    filtered_lines1 = read_and_filter_file(file1_path, sccd_filter)
    filtered_lines2 = read_and_filter_file(file2_path, devs_filter)

    # Write the filtered lines to output files
    write_filtered_lines_to_file(filtered_lines1, "sccd_test.txt")
    write_filtered_lines_to_file(filtered_lines2, "devs_test.txt")

    line_num = 1
    differences = []

    max_lines = max(len(filtered_lines1), len(filtered_lines2))
    for i in range(max_lines):
        line1 = filtered_lines1[i] if i < len(filtered_lines1) else ''
        line2 = filtered_lines2[i] if i < len(filtered_lines2) else ''

        if line1 != line2:
            differences.append((line_num, line1, line2))

        line_num += 1

    return differences

def print_differences(differences):
    """
    Print the differences between the filtered files.
    """
    if not differences:
        print("The files are identical after filtering.")
    else:
        for line_num, line1, line2 in differences:
            print(f"Difference at line {line_num}:")
            print(f"File1: {line1.strip()}")
            print(f"File2: {line2.strip()}")
            print()

# Example filter function to exclude lines starting with a certain keyword
def example_filter_func(line):
    return line.startswith('IGNORE')

if __name__ == '__main__':
    SCCDFile = "./examples/BouncingBalls/Python/trace.txt"
    DEVSFile = "./examples/BouncingBalls/PyDEVS/trace.txt"

    inputTrace = "./examples/BouncingBalls/input_trace.txt"

    option = 2
    if option == 1:
        generate_input_trace(SCCDFile, inputTrace)
    if option == 2:
        compare_traces(SCCDFile, DEVSFile)
