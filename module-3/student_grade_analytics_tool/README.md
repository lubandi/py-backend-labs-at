# **Student Grade Analytics Tool**

## **Overview**
A Python application that processes student grade data using Python's advanced collections (`Counter`, `defaultdict`, `OrderedDict`, `deque`). The tool reads CSV files, performs statistical analysis, and generates JSON reports with visualizations.

## **Features**
- **Advanced Collections**: Uses all four required collections efficiently
- **Memory Optimization**: `NamedTuple` for grades, `dataclass(slots=True)` for Student/Course
- **Type Safety**: Comprehensive type hints with `TypedDict` for reports
- **Statistical Analysis**: Mean, median, mode, grade distributions, rankings
- **Visualization**: ASCII histograms of grade distributions
- **Scalable Processing**: Generator-based CSV reading for large files

## **Project Structure**
```
student_grade_analytics_tool/
├── __init__.py
├── models.py              # Data models (Student, Grade, Course, Report types)
├── analysis.py            # Statistical analysis using collections
├── io_manager.py          # File I/O operations with context managers
├── main.py               # Main application entry point
├── tests/
│   ├── __init__.py
│   ├── test_analysis.py  # Unit tests for analysis functions
│   └── test_integration.py # End-to-end testing
├── data/
│   └── sample_grades.csv  # Sample input data
├── requirements.txt       # Project dependencies
└── README.md             # This file
```

## **Installation**
```bash
git clone <repository-url>
cd student_grade_analytics_tool
pip install -r requirements.txt
```

## **Usage**
```bash
# Process a CSV file
python -m student_grade_analytics_tool.main data/sample_grades.csv

# Specify output file
python -m student_grade_analytics_tool.main data.csv report.json
```

## **Sample CSV Format**
```csv
student_id,first_name,last_name,major,year,course_id,course_name,credits,semester,score
S001,John,Doe,CS,2023,CS101,Intro CS,3,F23,95.5
S001,John,Doe,CS,2023,MATH101,Calculus,4,F23,88.0
```

## **Collections Implementation**

### **1. Counter - Grade Distribution**
```python
# Counts frequency of each letter grade
distribution = Counter(['A', 'B', 'A', 'C'])  # {'A': 2, 'B': 1, 'C': 1}
```

### **2. defaultdict - Grouping by Major**
```python
# Auto-initializes lists for grouping
grouped = defaultdict(list)
grouped['CS'].append(student)  # No KeyError checking
```

### **3. OrderedDict - Student Rankings**
```python
# Maintains sorted order by GPA
ranked = OrderedDict(sorted_students)  # Preserves ranking order
```

### **4. deque - Rolling Averages**
```python
# Efficient sliding window calculations
window = deque(maxlen=3)  # Automatically discards old values
```

### **5. NamedTuple - Immutable Grades**
```python
# Memory-efficient immutable records
grade = Grade(course_id="CS101", score=95.5, credits=3, semester="F23")
```

### **6. Dataclass with slots**
```python
# Reduces memory by preventing __dict__ overhead
@dataclass(slots=True)
class Student:
    student_id: str
    # ... other attributes
```

## **Performance Optimizations**
- **Generator CSV reading**: Processes large files line-by-line
- **slots=True**: 40% memory reduction per object
- **NamedTuple**: Extremely memory-efficient for immutable data
- **Registry pattern**: Prevents duplicate Student/Course objects

## **Testing**
```bash
# Run all tests
python -m pytest tests/ -v

# Type checking
python -m mypy student_grade_analytics_tool/
```

## **Sample Output**
```
Processing data from data/sample_grades.csv...
Loaded 3 students and 3 courses.

Grade Distribution:
A | ██████████████ (3)
B | ████████████ (2)
C | █████ (1)
D |  (0)
F |  (0)

Global Stats: Mean=87.33, Median=88.00, Mode=95.50
Analysis complete. Report saved to report.json
```

## **Sample JSON Report**
```json
{
    "summary": {"mean": 87.33, "median": 88.0, "mode": 95.5},
    "grade_distribution": {"A": 3, "B": 2, "C": 1, "D": 0, "F": 0},
    "top_performers": [
        {"name": "John Doe", "gpa": 91.75, "major": "CS"}
    ],
    "major_counts": {"CS": 1, "Math": 1, "Physics": 1},
    "courses_analyzed": 3,
    "departments": ["CS", "MATH", "PHYS"]
}
```


## Memory Comparison Module

The `memory_comparison` module demonstrates Python collection efficiencies:

### Run Full Comparison

```python
from memory_comparison.all_comparisons import run_all_comparisons
run_all_comparisons()
```

### Key Comparisons Included

1. **NamedTuple vs Class vs Dictionary**: Memory efficiency for data records
2. **Dataclass with/without `__slots__`**: 40-60% memory reduction
3. **List vs Set vs Dictionary**: O(n) vs O(1) membership testing
4. **List vs Deque**: O(n) vs O(1) queue operations
5. **Counter vs Manual Counting**: Cleaner API with similar performance
