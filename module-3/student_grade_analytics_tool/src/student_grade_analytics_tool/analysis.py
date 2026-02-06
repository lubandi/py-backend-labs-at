import statistics
from collections import Counter, OrderedDict, defaultdict, deque
from typing import Dict, List

from .models import Student


class GradeAnalyzer:
    """
    Performs specific statistical analysis on student grade data.
    """

    @staticmethod
    def calculate_stats(scores: List[float]) -> Dict[str, float]:
        """
        Calculates mean, median, and mode for a list of scores.

        Example:
            >>> GradeAnalyzer.calculate_stats([95.5, 88.0, 91.0])
            {
                'mean': 91.5,
                'median': 91.0,
                'mode': 95.5
            }

            >>> GradeAnalyzer.calculate_stats([])
            {
                'mean': 0.0,
                'median': 0.0,
                'mode': 0.0
            }
        """
        if not scores:
            return {"mean": 0.0, "median": 0.0, "mode": 0.0}

        stats = {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
        }

        try:
            stats["mode"] = statistics.mode(scores)
        except statistics.StatisticsError:
            stats["mode"] = 0.0

        return stats

    @staticmethod
    def get_grade_distribution(students: List[Student]) -> Counter:
        """
        Computes the frequency of each letter grade across all students.
        Uses Counter as requested.

        Example:
            >>> GradeAnalyzer.get_grade_distribution(students)
            Counter({
                'A': 4,
                'B': 3,
                'C': 2,
                'D': 0,
                'F': 1
            })
        """
        all_grades = []
        for student in students:
            for grade in student.grades:
                if grade.score >= 90:
                    letter = "A"
                elif grade.score >= 80:
                    letter = "B"
                elif grade.score >= 70:
                    letter = "C"
                elif grade.score >= 60:
                    letter = "D"
                else:
                    letter = "F"
                all_grades.append(letter)

        return Counter(all_grades)

    @staticmethod
    def group_students_by_major(students: List[Student]) -> defaultdict:
        """
        Groups students by their major.
        Uses defaultdict as requested.

        Example:
            >>> grouped = GradeAnalyzer.group_students_by_major(students)

            >>> grouped['CS']
            [
                Student(student_id='S001', ...),
                Student(student_id='S004', ...)
            ]

            >>> grouped['ENG']
            [
                Student(student_id='S002', ...)
            ]
        """
        grouped = defaultdict(list)
        for student in students:
            grouped[student.major].append(student)
        return grouped

    @staticmethod
    def rank_students(students: List[Student]) -> OrderedDict:
        """
        Ranks students by their overall GPA.
        Uses OrderedDict to maintain the sorted order.

        Example:
            >>> ranked = GradeAnalyzer.rank_students(students)

            >>> list(ranked.items())
            [
                (Student(student_id='S004', ...), 98.0),
                (Student(student_id='S001', ...), 91.5),
                (Student(student_id='S002', ...), 83.75)
            ]
        """
        student_gpas = {}
        for student in students:
            scores = [g.score for g in student.grades]
            gpa = statistics.mean(scores) if scores else 0.0
            student_gpas[student] = gpa

        sorted_students = sorted(
            student_gpas.items(), key=lambda item: item[1], reverse=True
        )
        return OrderedDict(sorted_students)

    @staticmethod
    def calculate_rolling_average(
        scores: List[float], window_size: int = 3
    ) -> List[float]:
        """
        Calculates rolling average using deque.

        Example:
            >>> GradeAnalyzer.calculate_rolling_average(
            ...     [95.5, 88.0, 91.0, 85.0],
            ...     window_size=3
            ... )
            [95.5, 91.75, 91.5, 88.0]
        """
        if not scores:
            return []

        rolling_avgs = []
        window = deque(maxlen=window_size)

        for score in scores:
            window.append(score)
            rolling_avgs.append(sum(window) / len(window))

        return rolling_avgs

    @staticmethod
    def generate_ascii_histogram(distribution: Counter) -> str:
        """
        Generates a text-based histogram of grade distribution.

        Example:
            >>> distribution = Counter({'A': 4, 'B': 3, 'C': 2, 'F': 1})
            >>> print(GradeAnalyzer.generate_ascii_histogram(distribution))

            Grade Distribution:
            A | ████████████████ (4)
            B | ████████████ (3)
            C | ████████ (2)
            D |  (0)
            F | ████ (1)
        """
        if not distribution:
            return "No data for histogram."

        grades = ["A", "B", "C", "D", "F"]
        max_count = max(distribution.values()) if distribution.values() else 0
        scale = 20 / max_count if max_count > 0 else 1

        output = ["Grade Distribution:"]
        for grade in grades:
            count = distribution[grade]
            bar = "█" * int(count * scale)
            output.append(f"{grade} | {bar} ({count})")

        return "\n".join(output)
