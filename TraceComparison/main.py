def parse_line(line):
    """Parse a line into time and event."""
    parts = line.strip().split(' (event name: ')
    time_part, event_part = parts[0], parts[1]
    time_str = time_part.split()[0]
    time_val = float(time_str)
    return time_val, event_part

def compare_files(file1, file2):
    """Compare two files and return the maximum delta."""
    max_delta = 0
    events_match = True
    
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    
    # For every line in the two files
    for line1, line2 in zip(lines1, lines2):
        # Split it on the time value and the event
        time1, event1 = parse_line(line1)
        time2, event2 = parse_line(line2)
        # Calculate the absolute difference of the two times
        delta = abs(time1 - time2)
        # Update max_delta if necessary
        if delta > max_delta:
            max_delta = delta
        # Check if events are the same
        if event1 != event2:
            events_match = False

    return max_delta, events_match

# Example usage
file1 = "./examples/BouncingBalls/Python/output.txt"
file2 = "./examples/BouncingBalls/PyDEVS/output.txt"

max_delta, file_match = compare_files(file1, file2)
if file_match:
    print("Traces match")
    print("Maximum delta between the times:", max_delta)
else: 
    print("Traces don't match")