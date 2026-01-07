import json
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "images.json")

def get_random_image():
    data = load_images()

    if not data:
        return None

    return random.choice(data)

def load_images():
    with open(JSON_PATH, "r") as f:
        return json.load(f)

def save_images(data):
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=4)

def add_image(image_url, author_id):
    data = load_images()

    data.append({
        "image_url": image_url,
        "author_id": author_id
    })

    save_images(data)
