# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import Course
from .compute import compute_gpa_and_totals

app = FastAPI(title="GPAcalc API", version="0.1.0")
#Fast API  build a genric frontend!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "GPAcalc backend is running 🚀"}

@app.post("/gpa")
def calculate_gpa(courses: List[Course]):
    payload = [c.model_dump() for c in courses]
    return compute_gpa_and_totals(payload)
