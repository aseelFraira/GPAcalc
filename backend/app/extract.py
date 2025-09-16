# parse_transcript.py
import re
from typing import List, Dict, Optional
import pdfplumber

# --- patterns tailored to your transcript layout ---
SEM_RE   = r"\d{4}-\d{4}\s+(Spring|Winter|Summer|Fall)"
GRADE_EX = r"Exemption(?:\s+with(?:out)?\s+points)?"
GRADE_TX = rf"(?:{GRADE_EX}|Pass|\d{{1,3}})"       # numeric 0–100 OR Pass/Exemption...
CRED_RE  = r"\d+(?:\.\d+)?"                        # e.g., 3, 5.5
CODE_RE  = r"[A-Z]?\d{5,8}"                        # optional code like 02340118

# optional code + name + credits + grade + semester
ROW_WITH_CRED = re.compile(
    rf"^(?:{CODE_RE}\s+)?(?P<course>.+?)\s+"
    rf"(?P<credits>{CRED_RE})\s+"
    rf"(?P<grade>{GRADE_TX})\s+"
    rf"(?P<semester>{SEM_RE})\s*$"
)

# optional code + name + grade + semester   (no credits column)
ROW_NO_CRED = re.compile(
    rf"^(?:{CODE_RE}\s+)?(?P<course>.+?)\s+"
    rf"(?P<grade>{GRADE_TX})\s+"
    rf"(?P<semester>{SEM_RE})\s*$"
)

def _norm(s: Optional[str]) -> str:
    return (s or "").strip()

def _read_lines(pdf_path: str) -> List[str]:
    lines: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            for ln in txt.splitlines():
                ln = ln.rstrip()
                if ln:
                    lines.append(ln)
    return lines

def _crop_to_table(lines: List[str]) -> List[str]:
    # keep only between the header and "END OF TRANSCRIPT"
    start = None
    for i, ln in enumerate(lines):
        L = ln.lower()
        if "subject" in L and "credits" in L and "grade" in L and "semester" in L:
            start = i + 1
            break
    if start is None:
        start = 0
    end = next((i for i, ln in enumerate(lines) if "END OF TRANSCRIPT" in ln), len(lines))
    return lines[start:end]

def extract_courses(pdf_path: str) -> List[Dict[str, str]]:
    """
    Returns a list of dicts like:
      {"course": "<name>", "credits": "5" or "5.5" or "-", "grade": "92"/"Pass"/"Exemption ...", "semester": "2023-2024 Spring"}
    Designed to work with your main that prints these fields directly.
    """
    lines = _read_lines(pdf_path)
    lines = _crop_to_table(lines)

    courses: List[Dict[str, str]] = []
    buf = ""

    def _try_match(s: str) -> Optional[Dict[str, str]]:
        s = " ".join(s.split())  # collapse whitespace so wrapped names join correctly
        m = ROW_WITH_CRED.match(s)
        if m:
            return {
                "course": m.group("course"),
                "credits": m.group("credits"),
                "grade": m.group("grade"),
                "semester": m.group("semester")
            }
        m = ROW_NO_CRED.match(s)
        if m:
            return {
                "course": m.group("course"),
                "credits": "-",                # no credits column in this row
                "grade": m.group("grade"),
                "semester": m.group("semester")
            }
        return None

    for raw in lines:
        line = _norm(raw)

        # skip obvious non-row lines if they appear mid-table
        if not line or "Page " in line or "Grade Scale" in line or line.startswith("Transcript of "):
            continue
        if all(k in line for k in ("SUBJECT", "CREDITS", "GRADE")):
            continue

        # accumulate and try to match a complete row
        buf = f"{buf} {line}".strip() if buf else line
        rec = _try_match(buf)
        if rec:
            courses.append(rec)
            buf = ""  # reset for next row

    # final flush (in case last row ended at EOF)
    if buf:
        rec = _try_match(buf)
        if rec:
            courses.append(rec)

    return courses
