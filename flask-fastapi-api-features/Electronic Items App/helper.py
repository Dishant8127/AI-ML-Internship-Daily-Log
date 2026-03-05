from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = os.getenv("DATA_FILE")


def get_items():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

class Item(BaseModel):
    id: int
    name: str
    price: float
    description: str


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    message: str

class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id


