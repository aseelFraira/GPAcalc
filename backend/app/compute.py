# backend/app/compute.py

from typing import List, Dict, Union

Numeric = Union[int, float]

def compute_gpa_and_totals(courses: List[Dict]) -> Dict[str, Union[int, float]]:
    """
    Each course dict at least: {"credits": float, "grade": int|float|str}
    grade examples: 92, 81, "Pass", "Exemption", "Exemption without points", "Exemption with points"
    """
    gpa_points = 0.0          # Σ(grade * credits) for numeric grades only
    gpa_credits = 0.0         # Σ credits counted in GPA
    completed_credits = 0.0   # Σ credits successfully completed (includes Pass, Exemption with points)
    excluded_credits = 0.0    # Σ credits that don't count toward GPA or completion

    included_courses = 0
    excluded_courses = 0

    for c in courses:
        credits = float(c.get("credits", 0) or 0)
        grade = c.get("grade")

        # Numeric grade → counts for GPA and completion
        if isinstance(grade, (int, float)):
            gpa_points += float(grade) * credits
            gpa_credits += credits
            if grade >= 55:
                completed_credits += credits
            included_courses += 1
            continue

        # Non-numeric (strings like Pass/Exemption)
        if isinstance(grade, str):
            gl = grade.strip().lower()
            # Pass counts toward completion, not GPA
            if gl == "pass":
                completed_credits += credits
                excluded_courses += 1
                continue
            # Exemption: only count if it explicitly has points
            if "exemption with points" in gl:
                completed_credits += credits
                excluded_courses += 1
                continue
            # Common cases that do NOT add to completion or GPA
            if gl in {"exemption", "exemption without points"}:
                excluded_credits += credits
                excluded_courses += 1
                continue

        # Anything else unrecognized → exclude
        excluded_credits += credits
        excluded_courses += 1

    gpa = (gpa_points / gpa_credits) if gpa_credits > 0 else 0.0

    return {
        # GPA-related
        "gpa": round(gpa, 2),
        "gpa_points": round(gpa_points, 2),
        "gpa_credits": round(gpa_credits, 2),

        # Progress/degree-related
        "completed_credits": round(completed_credits, 2),  # includes Pass (+ Exemption with points)
        "excluded_credits": round(excluded_credits, 2),

        # Counts
        "included_courses": included_courses,  # numeric-graded
        "excluded_courses": excluded_courses,  # non-numeric or excluded by rules
    }
