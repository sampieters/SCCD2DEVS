import difflib

def are_files_identical(file1_path, file2_path):
    """Check if two files have the same contents."""
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        file1_contents = file1.read()
        file2_contents = file2.read()
        
        return file1_contents == file2_contents

def show_file_differences(file1_path, file2_path):
    """Show differences between two files."""
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()
        
        diff = difflib.unified_diff(file1_lines, file2_lines, fromfile='file1', tofile='file2')
        return ''.join(diff)

# Example usage
file1_path = "./examples/BouncingBalls/Python/output.txt"
file2_path = "./examples/BouncingBalls/PyDEVS/output.txt"

if are_files_identical(file1_path, file2_path):
    print("The files are identical.")
else:
    print("The files are different. Here are the differences:")
    differences = show_file_differences(file1_path, file2_path)
    print(differences)