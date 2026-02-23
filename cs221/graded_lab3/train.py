import json
import time
from model import *

file = open("train.json", "r")

texts = []
labels = []
for line in file:
    data = json.loads(line)
    texts.append(data["words"])
    labels.append(data["labels"])
file.close()

tagger = POSTagger()

tagger.fit(texts, labels)
tagger.save()

tagger = tagger.load()
start = time.time()
preds = tagger.predict(texts)
end = time.time()
print("Time:", end - start)


def accuracy(y_true, y_pred):
    correct = 0
    total = 0
    for true_labels, pred_labels in zip(y_true, y_pred):
        for t, p in zip(true_labels, pred_labels):
            if t == p:
                correct += 1
            total += 1
    return correct / total


print("Accuracy:", accuracy(labels, preds))
