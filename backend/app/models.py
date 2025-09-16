from pydantic import BaseModel
from typing import Union

class Course(BaseModel):
    credits: float
    grade: Union[int, float, str]  # e.g., 92, 81.5, "Pass", "Exemption"
