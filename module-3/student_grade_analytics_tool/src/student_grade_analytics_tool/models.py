from dataclasses import dataclass, field
from typing import Dict, List, NamedTuple, TypedDict, Union


class Grade(NamedTuple):
    """
    Immutable representation of a single grade record.
    Using NamedTuple for memory efficiency and immutability.
    """

    course_id: str
    score: float
    credits: int
    semester: str


@dataclass(slots=True)
class Course:
    """
    Represents course metadata.
    """

    course_id: str
    name: str
    department: str

    def __str__(self) -> str:
        return f"{self.course_id}: {self.name}"


@dataclass(slots=True)
class Student:
    """
    Represents a student and their academic record.
    """

    student_id: str
    first_name: str
    last_name: str
    major: str
    year: int
    grades: List[Grade] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"Student({self.student_id}, {self.full_name}, {self.major})"

    def add_grade(self, grade: Grade) -> None:
        self.grades.append(grade)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return self.student_id == other.student_id

    def __hash__(self) -> int:
        return hash(self.student_id)


class ReportSummary(TypedDict):
    mean: float
    median: float
    mode: float


class Report(TypedDict):
    summary: ReportSummary
    grade_distribution: Dict[str, int]
    top_performers: List[Dict[str, Union[str, float]]]
    major_counts: Dict[str, int]
    courses_analyzed: int
    departments: List[str]
