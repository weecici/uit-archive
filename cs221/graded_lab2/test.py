from model import FirstLM, SecondLM
import pickle

first = pickle.load(open("FirstLM.mdl", "rb"))
second = pickle.load(open("SecondLM.mdl", "rb"))

print("FIRST LM")
for i in range(10):
    print(f"{i}. {first.generate()}")

print("SECOND LM")
for i in range(10):
    print(f"{i}. {second.generate()}")
