import re

def get_general_port(text):
    # Get the general name of a private port with regex
    match = re.search(r'private_\d+_(\w+)', text)

    if match:
        result = match.group(1)
        return result
    else:
        return text
