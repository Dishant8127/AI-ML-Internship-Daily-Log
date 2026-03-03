import json
import os
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = os.getenv("DATA_FILE")


def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)