import os
import subprocess

# File path for recording progress
filepath = '../data/pyc_record.txt'

def find_python_exes(directory):
    """
    Recursively finds all Python executable files (.exe) in the specified directory.

    Args:
    - directory (str): Directory to search for Python executable files.

    Returns:
    - list: List of paths to Python executable files found.
    """
    python_exes = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.exe'):
                python_exes.append(os.path.join(root, file))
    return python_exes

def read_progress(filepath):
    """
    Reads the current progress index from the record file.

    Args:
    - filepath (str): Path to the record file.

    Returns:
    - int: Current index read from the record file.
    """
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()
            current_req_index = int(lines[0].strip())
            return current_req_index
    else:
        return 0

def write_progress(filepath, current_req_index):
    """
    Writes the current progress index to the record file.

    Args:
    - filepath (str): Path to the record file.
    - current_req_index (int): Current index to write to the record file.
    """
    with open(filepath, 'r') as file:
        lines = file.readlines()
    lines[0] = f"{current_req_index}\n"
    with open(filepath, 'w') as file:
        file.writelines(lines)

def create_binary_from_exe(exe_path, output_directory, record_filepath):
    """
    Creates a binary from a Python executable using pyinstxtractor.

    Args:
    - exe_path (str): Path to the Python executable (.exe) file.
    - output_directory (str): Directory where the extracted binary will be saved.
    - record_filepath (str): Path to the record file to track progress.
    """
    try:
        # Determine relative path from input directory
        rel_path = os.path.relpath(exe_path, input_directory)
        output_dir = os.path.join(output_directory, os.path.dirname(rel_path))
        output_dir = os.path.abspath(output_dir)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        os.chdir(output_dir)
        current_directory = os.getcwd()
        print(f"Current working directory: {current_directory}")

        # Run pyinstxtractor to extract the binary
        subprocess.check_call(["python3", "../../pyinstxtractor.py", "../../" + exe_path])
        print(f"Successfully created binary for {exe_path}")

        # Reset back to the original directory
        os.chdir('/mnt/data')

        # Record the progress index
        write_progress(record_filepath, i)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while creating binary for {exe_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def code_from_exe(input_directory, output_directory, record_filepath):
    """
    Main function to iterate through Python executable files and create binaries.

    Args:
    - input_directory (str): Directory containing Python executable (.exe) files.
    - output_directory (str): Directory where the extracted binaries will be saved.
    - record_filepath (str): Path to the record file to track progress.
    """
    # Find all Python executable files in the input directory
    python_exes = find_python_exes(input_directory)
    current_index = read_progress(record_filepath)

    # Iterate through each Python executable file
    for i in range(current_index, len(python_exes)):
        exe_path = python_exes[i]
        print(f"Processing {exe_path} ({i+1}/{len(python_exes)})")
        create_binary_from_exe(exe_path, output_directory, record_filepath)

# Specify the input directory containing Python executable files (.exe)
input_directory = '../data/executables'

# Specify the output directory where binaries will be saved
output_directory = '../data/pyc_files'

# Call the function to create binaries from Python executable files
code_from_exe(input_directory, output_directory, filepath)
