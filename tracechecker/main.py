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

def compare_traces(SCCDTrace, DEVSTrace):
    pass

if __name__ == '__main__':
    SCCDFile = "./examples/BouncingBalls/Python/trace.txt"
    DEVSFile = "./examples/BouncingBalls/PyDEVS/trace.txt"

    inputTrace = "./examples/BouncingBalls/input_trace.txt"

    option = 1
    if option == 1:
        generate_input_trace(SCCDFile, inputTrace)
    if option == 2:
        compare_traces(SCCDFile, DEVSFile)
