import ast
import os
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib  # For saving the model
def parse_script(path):
    with open(path, 'r') as file:
        script = file.read()
    try:
        return ast.parse(script)
    except SyntaxError as e:
        print(f"Syntax error in file {path}: {e}")
        return None

def extract_features(path):
    tree = parse_script(path)
    if tree is None:
        return None

    feature = {
        "imports": [],
        "function_calls": [],
        "strings": []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                feature["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                feature["imports"].append(alias.name)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                feature["function_calls"].append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                feature["function_calls"].append(node.func.attr)
        elif isinstance(node, ast.Str):
            feature["strings"].append(node.s)
    return feature

def save_features(input_path, output_path):
    features = extract_features(input_path)
    if features is None:
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(features, f)

def process_directory(input_dir, output_dir):
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".py"):
                input_file = os.path.join(root, file)
                relative_path = os.path.relpath(input_file, input_dir)
                output_file = os.path.join(output_dir, relative_path[:-3]+'.json')
                save_features(input_file, output_file)

if __name__ == "__main__":
    input_directory = "data/generated_scripts"
    output_directory = "data/parsing"

    # Process directory and extract features
    process_directory(input_directory, output_directory)

