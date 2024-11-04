# -*- coding: utf-8 -*-
"""hw1c_220.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zQX5-m43mbKyU8UJczXzLDW_AbnGsuZ-

Kiara LaRocca | klarocca@ucsc.edu

NLP 220 | Assignment 1

October 25, 2024

This is Part C of Assignment One, in which I create a custom Naive-Bayes model. It is trained on the same data as Part B, but it follows the tasks in Part A. Using three different features, the custom model is trained and evaluated against the sk-learn model in Part A. A huge mistake here was actually loading the dataset from Part B instead of A, or not rerunning the SKLearn Naive-Bayes model on the new data set.
"""

# Import packages and libraries

import pandas as pd
import numpy as np
import gc
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.naive_bayes import MultinomialNB
from scipy import sparse

# Mount Colab in Google Drive for access to data.

from google.colab import drive
drive.mount('/content/drive')
path = '/content/drive/My Drive/sentiment.csv'
df = pd.read_csv(path)

test_path = '/content/drive/My Drive/sentiment_test.csv'
test_df = pd.read_csv(path)

# Function to process the dataset and train the models using different feature engineering approaches
def process_and_train_models(df):
    # Preprocessing: Drop any rows with NaN in the 'content' or 'sentiment' columns
    df_clean = df.dropna(subset=['content', 'sentiment'])

    # Features and labels
    X = df_clean['content']
    y = df_clean['sentiment'].map({'neg': 0, 'pos': 1})  # Labels

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42, shuffle=True)

    # Ensure no NaN values in y_train and y_test
    X_train = X_train[y_train.notnull()]
    y_train = y_train[y_train.notnull()]
    X_test = X_test[y_test.notnull()]
    y_test = y_test[y_test.notnull()]

    gc.collect()  # Free memory

    # Define vectorizers and feature extraction methods
    feature_eng_methods = {
        "Bag of Words": CountVectorizer(stop_words='english', max_features=5000),
        "TF-IDF": TfidfVectorizer(stop_words='english', max_features=5000),
        "N-grams (Bigrams)": CountVectorizer(ngram_range=(1, 2), stop_words='english', max_features=5000)
    }

    for method_name, vectorizer in feature_eng_methods.items():
        print(f"\n--- Training and Evaluating with {method_name} ---")

        # Transform features
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        # Custom Naive Bayes
        nb_model_custom = CustomNaiveBayes()
        nb_model_custom.fit(X_train_vec, y_train)
        y_test_pred_custom = nb_model_custom.predict(X_test_vec)

        # Evaluation for Custom Naive Bayes
        test_accuracy_custom = accuracy_score(y_test, y_test_pred_custom)
        f1_custom = f1_score(y_test, y_test_pred_custom, average='macro')
        conf_matrix_custom = confusion_matrix(y_test, y_test_pred_custom)

        print(f"{method_name} - Custom Naive Bayes - Test Accuracy: {test_accuracy_custom:.4f}")
        print(f"Macro F1 Score: {f1_custom:.4f}")
        print("Confusion Matrix:")
        print(conf_matrix_custom)

        # Scikit-learn Naive Bayes
        nb_model_sklearn = MultinomialNB()
        nb_model_sklearn.fit(X_train_vec, y_train)
        y_test_pred_sklearn = nb_model_sklearn.predict(X_test_vec)

        # Evaluation for Scikit-learn Naive Bayes
        test_accuracy_sklearn = accuracy_score(y_test, y_test_pred_sklearn)
        f1_sklearn = f1_score(y_test, y_test_pred_sklearn, average='macro')
        conf_matrix_sklearn = confusion_matrix(y_test, y_test_pred_sklearn)

        print(f"{method_name} - Scikit-learn Naive Bayes - Test Accuracy: {test_accuracy_sklearn:.4f}")
        print(f"Macro F1 Score: {f1_sklearn:.4f}")
        print("Confusion Matrix:")
        print(conf_matrix_sklearn)


# Custom Naive Bayes Classifier
class CustomNaiveBayes:
    def __init__(self):
        self.classes = None
        self.class_probs = {}
        self.feature_probs = {}

    def fit(self, X, y):
        # Store the unique class labels
        self.classes = np.unique(y)
        total_docs = X.shape[0]

        # Calculate class probabilities (P(class))
        for c in self.classes:
            class_count = np.sum(y == c)
            self.class_probs[c] = class_count / total_docs

            # Subset for each class
            X_c = X[y == c]
            # Calculate probabilities for each feature (P(feature | class))
            feature_count = X_c.sum(axis=0) + 1  # Laplace smoothing
            total_count = feature_count.sum()
            self.feature_probs[c] = feature_count / total_count

    def predict(self, X):
        preds = []
        for i in range(X.shape[0]):
            doc = X[i]
            class_scores = {}
            for c in self.classes:
                class_scores[c] = np.log(self.class_probs[c])  # P(class)
                feature_probs = self.feature_probs[c].A1
                class_scores[c] += np.sum(doc.multiply(np.log(feature_probs)))
            preds.append(max(class_scores, key=class_scores.get))
        return np.array(preds)

process_and_train_models(df)

process_and_train_models(test_df)

