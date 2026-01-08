from collections import Counter

import pytest
from src.student_grade_analytics_tool.analysis import GradeAnalyzer
from src.student_grade_analytics_tool.models import Grade, Student

# Test Fixtures


@pytest.fixture
def sample_students():
    s1 = Student("S1", "Alice", "A", "CS", 2023)
    s1.add_grade(Grade("C1", 95.0, 3, "F23"))
    s1.add_grade(Grade("C2", 85.0, 3, "F23"))

    s2 = Student("S2", "Bob", "B", "ENG", 2024)
    s2.add_grade(Grade("C1", 75.0, 3, "F23"))

    return [s1, s2]


def test_calculate_stats():
    analyzer = GradeAnalyzer()
    scores = [10.0, 20.0, 20.0, 40.0]
    expected = {"mean": 22.5, "median": 20.0, "mode": 20.0}
    assert analyzer.calculate_stats(scores) == expected


def test_calculate_stats_empty():
    analyzer = GradeAnalyzer()
    assert analyzer.calculate_stats([]) == {"mean": 0.0, "median": 0.0, "mode": 0.0}


def test_grade_distribution(sample_students):
    analyzer = GradeAnalyzer()
    dist = analyzer.get_grade_distribution(sample_students)
    # Scores: 95(A), 85(B), 75(C)
    assert dist == Counter({"A": 1, "B": 1, "C": 1})


def test_group_by_major(sample_students):
    analyzer = GradeAnalyzer()
    grouped = analyzer.group_students_by_major(sample_students)
    assert len(grouped["CS"]) == 1
    assert len(grouped["ENG"]) == 1
    assert grouped["CS"][0].first_name == "Alice"


def test_rank_students(sample_students):
    analyzer = GradeAnalyzer()
    # S1 avg: 90, S2 avg: 75
    ranked = analyzer.rank_students(sample_students)
    keys = list(ranked.keys())
    assert keys[0].student_id == "S1"
    assert keys[1].student_id == "S2"


def test_rolling_average():
    analyzer = GradeAnalyzer()
    scores = [10, 20, 30, 40]
    # Window 3:
    # [10] -> 10
    # [10, 20] -> 15
    # [10, 20, 30] -> 20
    # [20, 30, 40] -> 30
    expected = [10.0, 15.0, 20.0, 30.0]
    assert analyzer.calculate_rolling_average(scores, window_size=3) == expected


def test_ascii_histogram():
    analyzer = GradeAnalyzer()
    dist = Counter({"A": 5, "B": 3})
    hist = analyzer.generate_ascii_histogram(dist)
    # Scale is 20/5 = 4.
    # A bar: 5 * 4 = 20 hashes.
    # B bar: 3 * 4 = 12 hashes.
    assert "A | ████████████████████ (5)" in hist
    assert "B | ████████████ (3)" in hist
