import json
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def path(name):
    if name == "image":
        return os.path.join(BASE_DIR, "images.json")
    elif name == "quote":
        return os.path.join(BASE_DIR, "quotes.json")

def get_random_data(name):
    data = load_data(name)

    if not data:
        return None

    return random.choice(data)

def load_data(name):
    with open(path(name), "r") as f:
        return json.load(f)

def save_data(name, data):
    with open(path(name), "w") as f:
        json.dump(data, f, indent=4)

def add_data(name, content, author_id):
    data = load_data(name)

    data.append({
        "content": content,
        "author_id": author_id
    })

    save_data(name, data)
