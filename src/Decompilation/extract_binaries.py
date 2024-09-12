import os
import subprocess
import sys


filepath='../data/exec_record.txt'
def find_python_scripts(directory):
    python_scripts = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_scripts.append(os.path.join(root, file))
    return python_scripts

def read_progress(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()
            current_req_index = int(lines[0].strip())
            return current_req_index
    else:
        return 0


# Function to write progress to the record file
def write_progress(filepath, current_req_index):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    lines[0] = f"{current_req_index}\n"
    with open(filepath, 'w') as file:
        file.writelines(lines)
def binary_from_script(directory, output_directory,filepath):
    python_scripts = find_python_scripts(directory)
    index=read_progress(filepath)
    for i in range(index,len(python_scripts)):
        script=python_scripts[i]
        # Determine relative path from input directory
        rel_path = os.path.relpath(script, directory)
        output_dir = os.path.join(output_directory, os.path.dirname(rel_path))
        output_dir = os.path.abspath(output_dir)

        print(f'Pyinstalling script {script} -----------------------')

        try:
            subprocess.check_call(["pyinstaller", "--onefile", "--distpath", output_dir, script])
            print(f"Successfully created binary for {script}")
            write_progress(filepath, i)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while creating binary for {script}: {e}")


# Specify the input directory containing scripts
input_directory = os.environ['code_dir']

# Specify the output directory where binaries will be saved
output_directory = '../data/executables'

# Call the function to create binaries
binary_from_script(input_directory, output_directory,filepath)
