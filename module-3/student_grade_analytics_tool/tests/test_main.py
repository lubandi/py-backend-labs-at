from src.student_grade_analytics_tool.main import parse_student_data


def test_end_to_end_parsing():
    """Test parsing from raw data to students"""
    raw_data = [
        {
            "student_id": "S1",
            "first_name": "Alice",
            "last_name": "A",
            "major": "CS",
            "year": "2023",
            "course_id": "CS101",
            "course_name": "Intro CS",
            "credits": "3",
            "semester": "F23",
            "score": "95.0",
        }
    ]
    students, courses = parse_student_data(raw_data)
    assert len(students) == 1
    assert len(students[0].grades) == 1
    assert len(courses) == 1
    assert "CS101" in courses
