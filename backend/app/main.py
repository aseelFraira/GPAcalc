# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import tempfile, os, inspect

from .models import Course
from .compute import compute_gpa_and_totals
from .extract import extract_courses

app = FastAPI(title="GPAcalc API", version="0.9.0")   # <— ADD THIS version marker

# --- ADD THIS: show EXACT file paths being loaded ---
print("MAIN LOADED FROM:", __file__)
print("extract_courses FROM:", inspect.getsourcefile(extract_courses))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "GPAcalc backend is running v0.9.0"}  # <— version in response

@app.post("/gpa")
def calculate_gpa(courses: List[Course]):
    payload = [c.model_dump() for c in courses]
    return compute_gpa_and_totals(payload)

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a .pdf file.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        parsed = extract_courses(path)
        return {"count": len(parsed), "courses": parsed}
    finally:
        os.unlink(path)

@app.post("/gpa-from-pdf")
async def gpa_from_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a .pdf file.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        parsed = extract_courses(path)
        payload = []
        for c in parsed:
            credits = None if c["credits"] in ("", "-", None) else float(c["credits"])
            gr = c["grade"]
            grade = int(gr) if isinstance(gr, str) and gr.isdigit() else gr
            payload.append({"credits": credits, "grade": grade})
        return {"parsed_count": len(parsed), "gpa_result": compute_gpa_and_totals(payload), "courses": parsed}
    finally:
        os.unlink(path)

# --- ADD THIS: print all routes at startup ---
from fastapi.routing import APIRoute
print("\n=== ROUTES LOADED ===")
for r in app.routes:
    if isinstance(r, APIRoute):
        print(f"{sorted(r.methods)} {r.path}")
print("=== END ROUTES ===\n")
