# backend/tests/test_compute.py
# backend/tests/test_compute.py
from backend.app.compute import compute_gpa_and_totals

def test_gpa_with_pass_and_exemption():
    courses = [
        {"grade": 90, "credits": 3},
        {"grade": 40, "credits": 4},          # fail → counts in GPA, not completed
        {"grade": "Pass", "credits": 2},      # completed, no GPA
        {"grade": "Exemption", "credits": 1}, # excluded
    ]
    result = compute_gpa_and_totals(courses)
    assert result["gpa"] == round((90*3 + 40*4) / 7, 2)
    assert result["completed_credits"] == 5  # 3 from pass + 2 numeric >=55
    assert result["excluded_credits"] == 1
