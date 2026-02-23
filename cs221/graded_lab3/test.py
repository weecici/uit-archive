import nltk
import json
from nltk import data
from nltk.corpus import treebank

texts = []
labels = []
for tagged_sent in treebank.tagged_sents():
    words, pos_tags = zip(*tagged_sent)
    texts.append(list(words))
    labels.append(list(pos_tags))


with open("test.json", "w") as f:
    for text, label in zip(texts, labels):
        f.write("\n")
        json.dump({"words": text, "labels": label}, f)
