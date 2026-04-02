import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("lab_work_08_school_simulator.py")
SPEC = importlib.util.spec_from_file_location("school_simulator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

Student = MODULE.Student
UndergraduateStudent = MODULE.UndergraduateStudent
PostgraduateStudent = MODULE.PostgraduateStudent
Unit = MODULE.Unit
EnrollmentError = MODULE.EnrollmentError
InvalidDataError = MODULE.InvalidDataError
EnrollmentSystem = MODULE.EnrollmentSystem
SchoolRegistry = MODULE.SchoolRegistry


class TestUnitAddStudent(unittest.TestCase):
    def test_valid_enrollment(self):
        unit = Unit("NIT2215", "Data Revolution", max_students=2)
        student = Student(1254, "Ben", "Morovan")

        result = unit.add_student(student)

        self.assertEqual(result, "Ben Morovan enrolled successfully.")
        self.assertEqual(unit.get_enrollment_count(), 1)
        self.assertIn(student, unit.students)

    def test_duplicate_enrollment_raises(self):
        unit = Unit("NIT2215", "Data Revolution", max_students=2)
        student = Student(1254, "Ben", "Morovan")
        unit.add_student(student)

        with self.assertRaises(EnrollmentError):
            unit.add_student(student)

    def test_invalid_type_raises(self):
        unit = Unit("NIT2215", "Data Revolution", max_students=2)

        with self.assertRaises(EnrollmentError):
            unit.add_student("not-a-student")

    def test_capacity_limit_raises(self):
        unit = Unit("NIT2215", "Data Revolution", max_students=2)
        student1 = Student(1254, "Ben", "Morovan")
        student2 = Student(6454, "Billy", "Hartley")
        student3 = Student(9000, "John", "Smith")

        unit.add_student(student1)
        unit.add_student(student2)

        with self.assertRaises(EnrollmentError):
            unit.add_student(student3)

        self.assertEqual(unit.get_enrollment_count(), 2)


class TestStudentGrading(unittest.TestCase):
    def setUp(self):
        self.student = Student(1001, "Test", "Student")

    def test_grade_boundaries(self):
        self.assertEqual(self.student.get_grade(49), "F")
        self.assertEqual(self.student.get_grade(50), "P")
        self.assertEqual(self.student.get_grade(79), "D")
        self.assertEqual(self.student.get_grade(80), "HD")

    def test_typical_values_each_grade_range(self):
        self.assertEqual(self.student.get_grade(30), "F")
        self.assertEqual(self.student.get_grade(55), "P")
        self.assertEqual(self.student.get_grade(65), "C")
        self.assertEqual(self.student.get_grade(75), "D")
        self.assertEqual(self.student.get_grade(90), "HD")

    def test_edge_values(self):
        self.assertEqual(self.student.get_grade(0), "F")
        self.assertEqual(self.student.get_grade(100), "HD")

        with self.assertRaises(InvalidDataError):
            self.student.get_grade(-1)

        with self.assertRaises(InvalidDataError):
            self.student.get_grade(101)


class TestSubclassGrading(unittest.TestCase):
    def test_undergraduate_uses_student_grading_rules(self):
        undergrad = UndergraduateStudent(2001, "Uma", "Ng", "Computer Science")
        self.assertEqual(undergrad.get_grade(50), "P")
        self.assertEqual(undergrad.get_grade(80), "HD")

    def test_postgraduate_uses_student_grading_rules(self):
        postgrad = PostgraduateStudent(3001, "Priya", "Shah", "AI in Education")
        self.assertEqual(postgrad.get_grade(49), "F")
        self.assertEqual(postgrad.get_grade(79), "D")


def _fresh_enrollment_system():
    """Return an isolated EnrollmentSystem instance for pytest-style tests."""
    EnrollmentSystem._instance = None
    SchoolRegistry._instances = {}
    return EnrollmentSystem()


def test_enroll_student_in_unit_unit_not_found(monkeypatch):
    import pytest

    enrollment_system = _fresh_enrollment_system()
    student = Student(9999, "No", "Unit")
    enrollment_system.registry.add_person(student)

    with pytest.raises(InvalidDataError) as exc_info:
        enrollment_system.enroll_student_in_unit(student_id=9999, unit_code="UNKNOWN")

    assert "No unit found for code: UNKNOWN" in str(exc_info.value)


def test_enroll_student_in_unit_prerequisite_not_met(monkeypatch):
    import pytest

    enrollment_system = _fresh_enrollment_system()
    student = Student(1000, "Lena", "Parker")
    student.units_completed = ["NIT1201"]
    enrollment_system.registry.add_person(student)

    unit = Unit("NIT3001", "Advanced OOP", max_students=2)
    unit.prerequisites = ["NIT1201", "NIT2201"]
    enrollment_system.units[unit.unit_code] = unit

    with pytest.raises(EnrollmentError) as exc_info:
        enrollment_system.enroll_student_in_unit(student_id=1000, unit_code="NIT3001")

    assert "does not meet prerequisites" in str(exc_info.value)
    assert "NIT2201" in str(exc_info.value)


def test_enroll_student_in_unit_capacity_full(monkeypatch):
    import pytest

    enrollment_system = _fresh_enrollment_system()

    student1 = Student(2001, "Ben", "Morovan")
    student2 = Student(2002, "Billy", "Hartley")
    enrollment_system.registry.add_person(student1)
    enrollment_system.registry.add_person(student2)

    unit = Unit("NIT2215", "Data Revolution", max_students=1)
    unit.add_student(student1)
    enrollment_system.units[unit.unit_code] = unit

    with pytest.raises(EnrollmentError) as exc_info:
        enrollment_system.enroll_student_in_unit(student_id=2002, unit_code="NIT2215")

    assert "now full" in str(exc_info.value)


if __name__ == "__main__":
    unittest.main()
