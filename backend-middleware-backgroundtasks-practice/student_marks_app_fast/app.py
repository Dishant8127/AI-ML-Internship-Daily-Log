from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import time
from helpers import read_data , write_data

app = FastAPI()

class Student(BaseModel):
    name: str
    marks: int
    subject: str

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    print("------ API LOG ------")
    print("Endpoint:", request.url.path)
    print("Method:", request.method)
    print(f"Time Taken: {process_time:.4f} seconds")
    print("---------------------")

    return response

@app.get("/students")
def get_students():
    return read_data()

@app.post("/students")
def add_student(student: Student):
    data = read_data()
    student_dict = student.dict()
    student_dict["id"] = len(data) + 1
    data.append(student_dict)
    write_data(data)
    return {"message": "Student added successfully", "student": student_dict}

@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):
    data = read_data()

    for student in data:
        if student["id"] == student_id:
            student["name"] = updated_student.name
            student["marks"] = updated_student.marks
            student["subject"] = updated_student.subject
            write_data(data)
            return {"message": "Student updated successfully"}

    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    data = read_data()

    for student in data:
        if student["id"] == student_id:
            data.remove(student)
            write_data(data)
            return {"message": "Student deleted successfully"}

    raise HTTPException(status_code=404, detail="Student not found")
