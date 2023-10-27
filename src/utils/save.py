import pickle

def save_class(cls, savepath):
    with open(savepath, "wb") as f:
        pickle.dump(cls, f)

def load_class(file):
    with open(file, "rb") as f:
        return pickle.load(f)
