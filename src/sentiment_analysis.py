import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from os_utility import *
import pandas as pd
import os

# Example: Predict sentiment on new text
def predict_sentiment(text):
    print("Loading joblib model")
    pipeline = joblib.load("sentiment140_model_pipeline.joblib")
    loaded_model = pipeline["model"]
    loaded_tfidf = pipeline["tfidf"]
    # Preprocess the input text (use the same function as before)
    clean_text = preprocess_text(text)
    # Convert text to TF-IDF vector
    text_vector = loaded_tfidf.transform([clean_text])
    # Predict
    prediction = loaded_model.predict(text_vector)
    # print(prediction)
    return "Positive" if prediction[0] == 4 else "Negative"

# Clean text (optional: define a preprocessing function)
def preprocess_text(text):
    text = text.lower()  # Lowercase
    text = re.sub(r"http\S+|www\S+|@\w+|#\w+", "", text)  # Remove URLs, mentions, hashtags
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text

# Train and create model if it doesn't exist in current directory
if not os.path.isfile('sentiment140_model_pipeline.joblib'):
    print("Model does not exist. Creating.")
    df = pd.read_csv("Sentiment140/training.1600000.processed.noemoticon.csv", encoding='ISO-8859-1', header=None, names=["target", "id", "date", "flag", "user", "text"])
    df = df[["target", "text"]]  # Keep only target and text
    df["clean_text"] = df["text"].apply(preprocess_text)
    tfidf = TfidfVectorizer(max_features=5000)  # Use top 5000 features for efficiency
    X = tfidf.fit_transform(df["clean_text"])
    y = df["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    # Initialize and train the model
    model = LogisticRegression(max_iter=1000)  # Increase max_iter for convergence
    model.fit(X_train, y_train)

    # Predict on test data
    y_pred = model.predict(X_test)

    # Calculate metrics
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
    joblib.dump(
        {"model": model, "tfidf": tfidf},
        "sentiment140_model_pipeline.joblib",
        compress=3  # Compression level (0-9)
    )