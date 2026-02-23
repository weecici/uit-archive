import pickle
import random
from collections import defaultdict


class BaseLM:
    def __init__(self):
        self.sents = []

    def fit(self, data):
        self.sents = data

    def generate(self):
        return random.choice(self.sents)


class FirstLM(BaseLM):
    def save(self):
        with open("FirstLM.mdl", "wb") as f:
            pickle.dump(self, f)


class SecondLM(BaseLM):
    def save(self):
        with open("SecondLM.mdl", "wb") as f:
            pickle.dump(self, f)
