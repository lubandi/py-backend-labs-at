import sys
from typing import NamedTuple


class Grade(NamedTuple):
    course_id: str
    score: float
    credits: int
    semester: str


# NamedTuple vs Class vs Dictionary
class RegularClass:
    def __init__(self, course_id, score, credits, semester):
        self.course_id = course_id
        self.score = score
        self.credits = credits
        self.semester = semester


grade_dict = {
    "course_id": "CS101",
    "score": 95.5,
    "credits": 3,
    "semester": "Fall 2023",
}
grade_class = RegularClass("CS101", 95.5, 3, "Fall 2023")
grade_namedtuple = Grade("CS101", 95.5, 3, "Fall 2023")

print(f"Dict size: {sys.getsizeof(grade_dict)} bytes")  # ~240 bytes
print(f"Class size: {sys.getsizeof(grade_class)} bytes")  # ~56 bytes
print(
    f"NamedTuple size: {sys.getsizeof(grade_namedtuple)} bytes"
)  # ~48 bytes (smallest!)
