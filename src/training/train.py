import os
import json
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from scipy.sparse import hstack, csr_matrix
import numpy as np


# Load features from files
def load_features(directory):
    imports_data = []
    function_calls_data = []
    strings_data = []
    labels = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    features = json.load(f)

                    imports = " ".join(features["imports"])
                    function_calls = " ".join(features["function_calls"])
                    strings = " ".join(features["strings"])

                    imports_data.append(imports)
                    function_calls_data.append(function_calls)
                    strings_data.append(strings)

                    if 'benign' in file_path:
                        labels.append(0)  # Benign
                    else:
                        labels.append(1)  # Malicious

    return imports_data, function_calls_data, strings_data, labels


# Get top features to exclude based on feature importance
def get_top_features_to_exclude(model, top_n=1):
    feature_importances = model.feature_importances_
    sorted_indices = np.argsort(feature_importances)[-top_n:]  # Get the top_n most important features
    return sorted_indices, feature_importances


# Decode the excluded feature (convert feature index back to original feature name)
def decode_excluded_features(encoder_imports, encoder_calls, vectorizer_strings, exclude_feature_indices):
    import_features = encoder_imports.get_feature_names_out()
    call_features = encoder_calls.get_feature_names_out()
    string_features = vectorizer_strings.get_feature_names_out()

    all_feature_names = np.concatenate([import_features, call_features, string_features])
    return [all_feature_names[idx] for idx in exclude_feature_indices]


# Train model with PCA applied
def train_classifier_with_pca(imports_data, function_calls_data, strings_data, labels, pca_components=0.90):
    encoder_imports = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    X_imports = encoder_imports.fit_transform(np.array(imports_data).reshape(-1, 1))

    encoder_calls = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    X_calls = encoder_calls.fit_transform(np.array(function_calls_data).reshape(-1, 1))

    vectorizer_strings = TfidfVectorizer()
    X_strings = vectorizer_strings.fit_transform(strings_data)

    X = hstack([X_imports, X_calls, X_strings])
    X = csr_matrix(X)

    # Apply PCA
    if pca_components is not None:
        pca = PCA(n_components=pca_components)
        X_pca = pca.fit_transform(X.toarray())
    else:
        X_pca = X.toarray()

    X_train, X_test, y_train, y_test = train_test_split(X_pca, labels, test_size=0.3, stratify=labels, random_state=42)

    model = DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Model performance after this iteration:")
    print(classification_report(y_test, y_pred))

    return model, encoder_imports, encoder_calls, vectorizer_strings, X_pca


# Iteratively exclude important features
def iterative_feature_exclusion(imports_data, function_calls_data, strings_data, labels, num_iterations=100, top_n=1):
    model, encoder_imports, encoder_calls, vectorizer_strings, X_pca = train_classifier_with_pca(
        imports_data, function_calls_data, strings_data, labels, pca_components=0.9
    )

    for iteration in range(num_iterations):
        print(f"\nIteration {iteration + 1}:")

        # Get the most important features to exclude
        top_features_to_exclude_indices, feature_importances = get_top_features_to_exclude(model, top_n=top_n)

        # Decode and show excluded features
        decoded_excluded_features = decode_excluded_features(encoder_imports, encoder_calls, vectorizer_strings,
                                                             top_features_to_exclude_indices)
        print(f"Excluded Features (decoded): {decoded_excluded_features}")

        # Update X_pca by removing the most important features
        X_pca = np.delete(X_pca, top_features_to_exclude_indices, axis=1)

        print(f"Updated X_pca shape: {X_pca.shape}")

        # Train the model again with the updated X_pca
        X_train, X_test, y_train, y_test = train_test_split(X_pca, labels, test_size=0.3, stratify=labels,
                                                            random_state=42)
        model = DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Show model performance after each iteration
        print(f"Iteration {iteration + 1} Performance:")
        print(classification_report(y_test, y_pred))

        # Stop if all features are excluded
        if X_pca.shape[1] <= 1:
            print("All features have been excluded. Stopping.")
            break

    return X_pca


if __name__ == "__main__":
    input_directory = "src/training/data/data"

    # Load features and labels
    imports_data, function_calls_data, strings_data, labels = load_features(input_directory)

    # Perform iterative feature exclusion
    num_iterations = 100  # Adjust the number of iterations as needed
    iterative_feature_exclusion(imports_data, function_calls_data, strings_data, labels, num_iterations=num_iterations)
