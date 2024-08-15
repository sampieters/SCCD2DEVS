import os
import shutil

# Path to the parent directory containing the test folders
parent_directory = './tests'

# Iterate over each folder inside the parent directory
for folder_name in os.listdir(parent_directory):
    folder_path = os.path.join(parent_directory, folder_name)
    
    # Check if the path is a directory and not a file
    if os.path.isdir(folder_path):
        # Delete PyDEVS folder if it exists
        pydevs_path = os.path.join(folder_path, 'ClassicDEVS')
        if os.path.exists(pydevs_path):
            shutil.rmtree(pydevs_path)
            print(f"Deleted {pydevs_path}")
        
        # Delete Python folder if it exists
        python_path = os.path.join(folder_path, 'Python')
        if os.path.exists(python_path):
            shutil.rmtree(python_path)
            print(f"Deleted {python_path}")