import os
import chardet
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

def FunderClassifier(funder_csv):
    csv_file_path = 'ml_models/funder_classifier_data.csv'

    if not os.path.exists(csv_file_path):
        # Create the CSV file with initial columns if it doesn't exist
        initial_data = pd.DataFrame(columns=['csv_string', 'funder'])
        initial_data.to_csv(csv_file_path, index=False)
        print(f"Created new file: {csv_file_path}")

    dataset = pd.read_csv(csv_file_path)

    if dataset.empty:
        print("Dataset is empty. Unable to train the model.")
        return "Unknown", 0.0

    # Prepare data for training
    X = dataset['csv_string']
    y = dataset['funder']

    # Convert text data into feature vectors using CountVectorizer
    vectorizer = CountVectorizer(stop_words=None, token_pattern=r'\b\w+\b')
    try:
        X_vectorized = vectorizer.fit_transform(X)
    except ValueError as e:
        print(f"Vectorization error: {e}")
        print("Sample data:", X.head())
        return "Unknown", 0.0

    if X_vectorized.shape[1] == 0:
        print("No features were extracted from the text. Check the data and preprocessing steps.")
        return "Unknown", 0.0

    X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

    # Train Random Forest Classifier
    classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    classifier.fit(X_train, y_train)    

    # Make predictions on the test set
    y_pred = classifier.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    def csv_to_string(csv_file):
        # Detect the file encoding
        with open(csv_file, 'rb') as file:
            raw_data = file.read()
            detected_encoding = chardet.detect(raw_data)['encoding']

        try:
            # Try to read the file with the detected encoding
            with open(csv_file, 'r', encoding=detected_encoding) as file:
                csv_string = file.read()
        except UnicodeDecodeError:
            # If that fails, try common encodings
            common_encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
            for encoding in common_encodings:
                try:
                    with open(csv_file, 'r', encoding=encoding) as file:
                        csv_string = file.read()
                    break  # If successful, exit the loop
                except UnicodeDecodeError:
                    continue  # If unsuccessful, try the next encoding
            else:
                # If all encodings fail, raise an exception
                raise ValueError(f"Unable to decode the file {csv_file} with any known encoding")

        return csv_string

    # Convert the input CSV to a string
    csv_string = csv_to_string(funder_csv)

    # Vectorize the input CSV string
    try:
        input_vectorized = vectorizer.transform([csv_string])
    except ValueError as e:
        print(f"Error vectorizing input: {e}")
        return "Unknown", 0.0

    # Make prediction
    predicted_funder = classifier.predict(input_vectorized)
    confidence_score = classifier.predict_proba(input_vectorized).max()

    return predicted_funder[0], confidence_score

    # Example usage:
    # predicted_funder, confidence = FunderClassifier(funder_csv)
    # print(f'Predicted Funder: {predicted_funder}, Confidence: {confidence:.2f}')

