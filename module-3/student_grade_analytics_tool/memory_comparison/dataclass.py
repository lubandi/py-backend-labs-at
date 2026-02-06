from dataclasses import dataclass

from pympler.asizeof import asizeof


@dataclass
class StudentWithoutSlots:
    student_id: str
    first_name: str
    last_name: str
    major: str
    year: int
    gpa: float


@dataclass(slots=True)
class StudentWithSlots:
    student_id: str
    first_name: str
    last_name: str
    major: str
    year: int
    gpa: float


# Create instances
student1 = StudentWithoutSlots("S12345", "Alice", "Johnson", "CS", 3, 3.8)
student2 = StudentWithSlots("S12345", "Alice", "Johnson", "CS", 3, 3.8)

# Memory usage
print("=== MEMORY USAGE COMPARISON ===")
print(f"Without slots: {asizeof(student1)} bytes")
print(f"With slots:    {asizeof(student2)} bytes")
print(
    f"Memory saved:  {(asizeof(student1) - asizeof(student2)) / asizeof(student1) * 100:.1f}%"
)

# Typical output:
# Without slots: 584 bytes
# With slots:    256 bytes
# Memory saved:  56.2%  ← HALF THE MEMORY!
