import sys
from typing import Dict, List, Tuple

from student_grade_analytics_tool.analysis import GradeAnalyzer
from student_grade_analytics_tool.io_manager import IOManager
from student_grade_analytics_tool.models import Course, Grade, Report, Student


def parse_student_data(
    raw_data: List[Dict[str, str]]
) -> Tuple[List[Student], Dict[str, Course]]:
    """
    Parses raw CSV data into Student objects and tracks Courses.

    Args:
        raw_data: List of dictionaries from CSV

    Returns:
        Tuple containing:
        - List of Student objects with their grades
        - Dictionary of Course objects keyed by course_id

    Note:
        Assumes denormalized CSV format with one grade per row.
        Also builds a local registry of Courses found in the data.
    """
    students_registry: Dict[str, Student] = {}
    courses_registry: Dict[str, Course] = {}

    for row in raw_data:
        s_id = row["student_id"]
        c_id = row["course_id"]

        # Track Course
        if c_id not in courses_registry:
            courses_registry[c_id] = Course(
                course_id=c_id,
                name=row["course_name"],
                department=row["course_id"][:3],  # simple inference
            )

        if s_id not in students_registry:
            students_registry[s_id] = Student(
                student_id=s_id,
                first_name=row["first_name"],
                last_name=row["last_name"],
                major=row["major"],
                year=int(row["year"]),
            )

        student = students_registry[s_id]

        try:
            grade = Grade(
                course_id=row["course_id"],
                score=float(row["score"]),
                credits=int(row["credits"]),
                semester=row["semester"],
            )
            student.add_grade(grade)
        except ValueError as e:
            print(f"Skipping invalid grade record for student {s_id}: {e}")
            continue

    return list(students_registry.values()), courses_registry


def main():
    if len(sys.argv) < 2:
        input_file = "data/sample_grades.csv"
        print(f"No input file specified. Using default: {input_file}")
    else:
        input_file = sys.argv[1]

    output_file = sys.argv[2] if len(sys.argv) > 2 else "report.json"

    print(f"Processing data from {input_file}...")

    try:
        # 1. Load Data
        raw_data = list(IOManager.read_csv(input_file))
        students, courses_registry = parse_student_data(raw_data)
        print(f"Loaded {len(students)} students and {len(courses_registry)} courses.")

        if not students:
            print("No student data found.")
            return

        # 2. Analyze
        analyzer = GradeAnalyzer()

        distribution = analyzer.get_grade_distribution(students)
        grouped_by_major = analyzer.group_students_by_major(students)
        ranked_students = analyzer.rank_students(students)

        # Collect all scores for global stats
        all_scores = [g.score for s in students for g in s.grades]
        global_stats = analyzer.calculate_stats(all_scores)

        # 3. Visualize
        histogram = analyzer.generate_ascii_histogram(distribution)
        print("\n" + histogram + "\n")
        print(
            f"Global Stats: Mean={global_stats['mean']:.2f}, Median={global_stats['median']:.2f}, Mode={global_stats['mode']:.2f}"
        )

        # 4. Generate Report
        report: Report = {
            "summary": {
                "mean": global_stats["mean"],
                "median": global_stats["median"],
                "mode": global_stats["mode"],
            },
            "grade_distribution": dict(distribution),
            "top_performers": [
                {"name": s.full_name, "gpa": gpa, "major": s.major}
                for s, gpa in list(ranked_students.items())[:5]
            ],
            "major_counts": {m: len(s_list) for m, s_list in grouped_by_major.items()},
            "courses_analyzed": len(courses_registry),
            "departments": list(set(c.department for c in courses_registry.values())),
        }

        IOManager.write_json(report, output_file)
        print(f"Analysis complete. Report saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        print("Please check the file path and try again.")
        sys.exit(1)
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
