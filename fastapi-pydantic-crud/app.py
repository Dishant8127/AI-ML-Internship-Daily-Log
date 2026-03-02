from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = os.getenv("DATA_FILE", "data.json")

app = FastAPI()

def load_data():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

class User(BaseModel):
    id: int
    name: str
    age: int

@app.post("/users/", response_model=User)
def create_user(user: User):
    users = load_data()

    for u in users:
        if u["id"] == user.id:
            raise HTTPException(status_code=400, detail="User ID already exists")

    users.append(user.model_dump())
    save_data(users)

    return user

@app.get("/users/", response_model=List[User])
def get_users():
    return load_data()

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    users = load_data()

    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    users = load_data()

    for index, user in enumerate(users):
        if user["id"] == user_id:
            users[index] = updated_user.model_dump()
            save_data(users)
            return updated_user

    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    users = load_data()

    for index, user in enumerate(users):
        if user["id"] == user_id:
            users.pop(index)
            save_data(users)
            return {"message": "User deleted"}

    raise HTTPException(status_code=404, detail="User not found")