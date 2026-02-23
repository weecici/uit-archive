import pandas as pd
import ast
import re
from nltk.corpus import stopwords
from model import model
from sklearn.metrics import f1_score, confusion_matrix
from sklearn.model_selection import train_test_split


# print(stopwords.words("english"))
# exit()

train_set = pd.read_csv("data/_train.csv")
dev_set = pd.read_csv("data/_dev.csv")
test_set = pd.read_csv("data/_test.csv")
X_train = train_set["text"].to_numpy()
y_train = train_set["label"].to_numpy()
X_dev = dev_set["text"].to_numpy()
y_dev = dev_set["label"].to_numpy()
X_test = test_set["text"].to_numpy()
y_test = test_set["label"].to_numpy()

# print(len(X_train), len(X_dev), len(X_test))


model = model()
model.fit(X_train, y_train)
print("--- DEV SET RESULTS ---")
y_pred = model.predict(X_dev)
print("F1:", f1_score(y_dev, y_pred, average=None))
print("F1-macro:", f1_score(y_dev, y_pred, average="macro"))
print("\n--- TEST SET RESULTS ---")
y_pred = model.predict(X_test)
print("F1:", f1_score(y_test, y_pred, average=None))
print("F1-macro:", f1_score(y_test, y_pred, average="macro"))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
