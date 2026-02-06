"""
Memory and Performance Comparison Module
=======================================
This module demonstrates the memory usage and performance characteristics
of different Python data structures for various common operations.
"""

import sys
import timeit
from collections import Counter, deque
from dataclasses import dataclass
from typing import NamedTuple

from pympler.asizeof import asizeof

# ============================================================================
# 1. NAMEDTUPLE VS CLASS VS DICTIONARY COMPARISON
# ============================================================================


class Grade(NamedTuple):
    """
    Immutable grade record using NamedTuple.

    Advantages:
    - Memory efficient (same as tuple)
    - Readable attribute access (grade.course_id vs grade[0])
    - Type hints support
    - Immutable (thread-safe, hashable)

    Best for: Simple data records that don't change
    """

    course_id: str
    score: float
    credits: int
    semester: str


class RegularClass:
    """
    Regular Python class for comparison.

    Advantages:
    - Mutable (can change attributes)
    - Can add methods
    - Supports inheritance

    Disadvantages:
    - More memory than NamedTuple
    - More verbose for simple data containers
    """

    def __init__(self, course_id: str, score: float, credits: int, semester: str):
        self.course_id = course_id
        self.score = score
        self.credits = credits
        self.semester = semester


def compare_grade_structures():
    """
    Compare memory usage of different grade representations.

    Expected results:
    - Dictionary: Largest (~240 bytes) due to overhead of hash table
    - Regular Class: Medium (~56 bytes) due to __dict__ overhead
    - NamedTuple: Smallest (~48 bytes) same as regular tuple

    Returns:
        dict: Memory sizes for each structure
    """
    grade_dict = {
        "course_id": "CS101",
        "score": 95.5,
        "credits": 3,
        "semester": "Fall 2023",
    }
    grade_class = RegularClass("CS101", 95.5, 3, "Fall 2023")
    grade_namedtuple = Grade("CS101", 95.5, 3, "Fall 2023")

    return {
        "dict": sys.getsizeof(grade_dict),
        "class": sys.getsizeof(grade_class),
        "namedtuple": sys.getsizeof(grade_namedtuple),
    }


# ============================================================================
# 2. DATACLASS WITH/WITHOUT SLOTS COMPARISON
# ============================================================================


@dataclass
class StudentWithoutSlots:
    """
    Regular dataclass without __slots__.

    Uses __dict__ for attribute storage:
    - Flexible: Can add attributes dynamically
    - Higher memory: Each instance has a dictionary
    - Slower attribute access: Dictionary lookup

    Size: ~584 bytes
    """

    student_id: str
    first_name: str
    last_name: str
    major: str
    year: int
    gpa: float


@dataclass(slots=True)
class StudentWithSlots:
    """
    Dataclass with __slots__ for memory optimization.

    Uses fixed slots for attributes:
    - No __dict__ overhead
    - Cannot add new attributes dynamically
    - Faster attribute access: Direct memory access

    Size: ~256 bytes (56% memory saved!)

    Best for: Many instances of same structure
    """

    student_id: str
    first_name: str
    last_name: str
    major: str
    year: int
    gpa: float


def compare_slots_performance():
    """
    Compare memory and performance of slots vs no slots.

    Key Insight:
    - slots=True saves memory by preventing __dict__ creation
    - Particularly effective when creating many instances
    - Also improves attribute access speed

    Returns:
        dict: Memory usage comparison
    """
    student1 = StudentWithoutSlots("S12345", "Alice", "Johnson", "CS", 3, 3.8)
    student2 = StudentWithSlots("S12345", "Alice", "Johnson", "CS", 3, 3.8)

    memory_without = asizeof(student1)
    memory_with = asizeof(student2)
    memory_saved = (memory_without - memory_with) / memory_without * 100

    return {
        "without_slots_bytes": memory_without,
        "with_slots_bytes": memory_with,
        "memory_saved_percent": memory_saved,
    }


# ============================================================================
# 3. LIST VS SET VS DICTIONARY FOR MEMBERSHIP TESTING
# ============================================================================


def compare_membership_operations():
    """
    Compare performance of membership testing in different collections.

    Scenario: Checking if an item exists in a collection

    Collections compared:
    1. List: O(n) search time, scans entire list
    2. Set: O(1) average time, uses hash table
    3. Dictionary: O(1) average time, checks keys only

    Expected Results:
    - Set/Dict: ~1000x faster than List for large collections
    - Dict keys: Similar performance to Set

    Returns:
        dict: Execution times for membership testing
    """
    # Create collections with 10,000 items
    size = 10000
    test_list = list(range(size))
    test_set = set(range(size))
    test_dict = {i: f"value_{i}" for i in range(size)}

    # Item to search for (exists in collection)
    search_item = 5000

    # Time membership testing
    list_time = timeit.timeit(lambda: search_item in test_list, number=1000)
    set_time = timeit.timeit(lambda: search_item in test_set, number=1000)
    dict_time = timeit.timeit(lambda: search_item in test_dict, number=1000)

    return {
        "list_membership_ms": list_time * 1000,
        "set_membership_ms": set_time * 1000,
        "dict_membership_ms": dict_time * 1000,
        "list_vs_set_ratio": list_time / set_time if set_time > 0 else float("inf"),
    }


# ============================================================================
# 4. DEQUE VS LIST FOR QUEUE OPERATIONS
# ============================================================================


def compare_queue_operations():
    """
    Compare performance of deque vs list for queue operations.

    Operations compared:
    - Append left (add to front)
    - Pop left (remove from front)

    Key Insight:
    - List: O(n) for insert/pop at front (requires shifting elements)
    - Deque: O(1) for append/pop at both ends (double-linked list)

    Returns:
        dict: Execution times for queue operations
    """
    # Test with 1000 operations
    operations = 1000

    # Time list operations (inefficient as queue)
    def test_list_queue():
        lst = []
        for i in range(operations):
            lst.insert(0, i)  # O(n) - inefficient!
        for _ in range(operations):
            lst.pop(0)  # O(n) - inefficient!

    # Time deque operations (efficient as queue)
    def test_deque_queue():
        dq = deque()
        for i in range(operations):
            dq.appendleft(i)  # O(1) - efficient!
        for _ in range(operations):
            dq.popleft()  # O(1) - efficient!

    list_time = timeit.timeit(test_list_queue, number=100)
    deque_time = timeit.timeit(test_deque_queue, number=100)

    return {
        "list_queue_time_ms": list_time * 1000,
        "deque_queue_time_ms": deque_time * 1000,
        "deque_vs_list_speedup": list_time / deque_time
        if deque_time > 0
        else float("inf"),
    }


# ============================================================================
# 5. COUNTER VS MANUAL COUNTING
# ============================================================================


def compare_counting_methods():
    """
    Compare Counter vs manual dictionary counting.

    Scenario: Count frequency of items in a list

    Methods compared:
    1. Manual dict counting
    2. collections.Counter

    Key Insight:
    - Counter: Cleaner syntax, built-in methods (most_common, etc.)
    - Performance: Similar for basic counting

    Returns:
        dict: Memory and time comparison
    """
    import random

    # Generate random grades A-F
    grades = [random.choice(["A", "B", "C", "D", "F"]) for _ in range(1000)]

    # Manual counting
    def manual_count():
        counts = {}
        for grade in grades:
            if grade in counts:
                counts[grade] += 1
            else:
                counts[grade] = 1
        return counts

    # Counter approach
    def counter_count():
        return Counter(grades)

    # Time both approaches
    manual_time = timeit.timeit(manual_count, number=1000)
    counter_time = timeit.timeit(counter_count, number=1000)

    # Memory comparison
    manual_counts = manual_count()
    counter_counts = counter_count()

    return {
        "manual_time_ms": manual_time * 1000,
        "counter_time_ms": counter_time * 1000,
        "manual_memory_bytes": sys.getsizeof(manual_counts),
        "counter_memory_bytes": sys.getsizeof(counter_counts),
        "counter_has_extra_methods": True,  # most_common(), elements(), etc.
    }


# ============================================================================
# MAIN DEMONSTRATION FUNCTION
# ============================================================================


def run_all_comparisons():
    """
    Run all comparisons and print formatted results.

    This function demonstrates the efficiency trade-offs between
    different Python collections and data structures.
    """
    print("=" * 60)
    print("PYTHON COLLECTIONS EFFICIENCY COMPARISON")
    print("=" * 60)

    # 1. NamedTuple vs Class vs Dict
    print("\n1. MEMORY: NamedTuple vs Class vs Dictionary")
    print("-" * 40)
    grade_sizes = compare_grade_structures()
    print(f"Dictionary:      {grade_sizes['dict']:>6} bytes")
    print(f"Regular Class:   {grade_sizes['class']:>6} bytes")
    print(f"NamedTuple:      {grade_sizes['namedtuple']:>6} bytes")
    print(
        f"✓ NamedTuple saves {grade_sizes['dict'] - grade_sizes['namedtuple']} bytes vs Dictionary"
    )

    # 2. Slots vs No Slots
    print("\n2. MEMORY: Dataclass with/without __slots__")
    print("-" * 40)
    slot_results = compare_slots_performance()
    print(f"Without slots:   {slot_results['without_slots_bytes']:>6.0f} bytes")
    print(f"With slots:      {slot_results['with_slots_bytes']:>6.0f} bytes")
    print(f"✓ Memory saved:  {slot_results['memory_saved_percent']:.1f}%")

    # 3. Membership Testing
    print("\n3. PERFORMANCE: Membership Testing (in operator)")
    print("-" * 40)
    membership = compare_membership_operations()
    print(f"List (O(n)):     {membership['list_membership_ms']:>6.2f} ms")
    print(f"Set (O(1)):      {membership['set_membership_ms']:>6.2f} ms")
    print(f"Dict (O(1)):     {membership['dict_membership_ms']:>6.2f} ms")
    print(f"✓ Set is {membership['list_vs_set_ratio']:.0f}x faster than List")

    # 4. Queue Operations
    print("\n4. PERFORMANCE: Queue Operations (appendleft/popleft)")
    print("-" * 40)
    queue_results = compare_queue_operations()
    print(f"List (O(n)):     {queue_results['list_queue_time_ms']:>6.2f} ms")
    print(f"Deque (O(1)):    {queue_results['deque_queue_time_ms']:>6.2f} ms")
    print(f"✓ Deque is {queue_results['deque_vs_list_speedup']:.0f}x faster than List")

    # 5. Counting Methods
    print("\n5. COUNTER vs Manual Counting")
    print("-" * 40)
    count_results = compare_counting_methods()
    print(f"Manual dict:     {count_results['manual_time_ms']:>6.2f} ms")
    print(f"Counter:         {count_results['counter_time_ms']:>6.2f} ms")
    print(
        f"Memory similar:  {count_results['manual_memory_bytes']} vs {count_results['counter_memory_bytes']} bytes"
    )
    print("✓ Counter provides most_common(), elements(), +, - operators")

    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS:")
    print("-" * 60)
    print("• Use NamedTuple for immutable data records")
    print("• Use @dataclass(slots=True) when creating many instances")
    print("• Use Set/Dict for membership testing (O(1) vs O(n))")
    print("• Use Deque for queue/stack operations (O(1) at both ends)")
    print("• Use Counter for clean frequency counting")
    print("=" * 60)


if __name__ == "__main__":
    # Install required packages if running standalone
    try:
        from pympler.asizeof import asizeof  # noqa: F811
    except ImportError:
        print("Installing required packages...")
        import subprocess

        subprocess.check_call(["pip", "install", "pympler"])
        from pympler.asizeof import asizeof

    run_all_comparisons()
