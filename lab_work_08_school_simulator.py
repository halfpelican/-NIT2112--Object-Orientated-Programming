
from abc import ABC, abstractmethod
from typing import cast


class SchoolSystemError(Exception):
    """Base class for other exceptions"""
    pass

class EnrollmentError(SchoolSystemError):
    """Raised when there is an error during enrollment"""
    pass

class FactoryError(SchoolSystemError):
    """Raised when there is an error in the factory method"""
    pass

class InvalidDataError(SchoolSystemError):
    """Raised when provided data is invalid"""
    pass

class LegacyHRSystem:
    """Represents a legacy HR data source used to look up teacher records."""

    def __init__(self):
        """Initialise in-memory employee data from the legacy system."""
        self.employees = {
            8874: {"first_name": "Terry", "last_name": "Harrison", "subject_taught": "Physics"},
            8875: {"first_name": "Alice", "last_name": "Johnson", "subject_taught": "Mathematics"},
        }

    def fetch_employee_data(self, employee_id):
        """Return employee details for a given ID, or None if not found."""
        return self.employees.get(employee_id, None)

class HRAdapter:
    """Adapts legacy HR data into Teacher objects for the school domain."""

    def __init__(self, legacy):
        """Store a reference to the legacy HR system instance."""
        self.legacy = legacy

    def get_teacher_details(self, employee_id):
        """Convert a legacy employee record into a Teacher object."""
        data = self.legacy.fetch_employee_data(employee_id)
        if data is not None:
           
           return Teacher(
            data["first_name"],
            data["last_name"],
            employee_id,
            data["subject_taught"]
        )
        else:
            raise ValueError(f"No employee found with ID: {employee_id}")

class Person(ABC):
    """Abstract base class representing a person in the school system."""

    def __init__(self, first_name, last_name):
        """Initialise a person with a first name and last name."""
        self._first_name = first_name
        self._last_name = last_name

    def display_info(self):
        """Print the person's full name."""
        print(f"{self._first_name} {self._last_name}")

    def get_first_name(self):
        """Return the person's first name."""
        return self._first_name
    
    def set_first_name(self, new_first_name):
        """Update the person's first name."""
        self._first_name = new_first_name

    def get_last_name(self):
        """Return the person's last name."""
        return self._last_name

    def set_last_name(self, new_last_name):
        """Update the person's last name."""
        self._last_name = new_last_name   
 
    def get_full_name(self):
        """
        Return the person's full name.

        Returns:
            str: The full name in the format 'FirstName LastName'.
        """
        return f"{self.get_first_name()} {self.get_last_name()}"    

    @property
    def full_name(self):
        """Return the full name as a read-only property."""
        return f"{self._first_name} {self._last_name}"
    
    @abstractmethod
    def get_role(self):
        """Return the role name for concrete subclasses."""
        pass

class Teacher(Person):
    """Represents a teacher with an employee ID and subject specialty."""

    def __init__(self, first_name, last_name, employee_id, subject_taught):
        """Initialise a teacher profile."""
        super().__init__(first_name, last_name)
        self.__employee_id = employee_id
        self._subject_taught = subject_taught
    
    def display_info(self):
        """Print teacher name, employee ID, and subject taught."""
        super().display_info()
        print(f"{self.__employee_id} {self._subject_taught}")

    def get_role(self):
        """Return the role label for this class."""
        return "Teacher"

    @property
    def employee_id(self):
        """Return the teacher's employee ID."""
        return self.__employee_id
    
    @property
    def subject_taught(self):
        """Return the subject taught by the teacher."""
        return self._subject_taught
    
    @subject_taught.setter
    def subject_taught(self, new_subject):
        """Set the subject taught when a non-empty value is provided."""
        if new_subject != "":
            self._subject_taught = new_subject
        else:
            print("Can not be left blank.")

class Student(Person):
    """Represents a student and tracks enrolled units."""

    def __init__(self, student_id, first_name, last_name):
        """Initialise a student with an ID and personal details."""
        super().__init__(first_name, last_name)
        self.__student_id = student_id
        self.units_enrolled = []
  
    def get_student_id(self):
        """Return the student's ID."""
        return self.__student_id
    
    def display_details(self):
        """Print full student details, including enrolled units."""
        print(f"{self.__student_id}\n{self.get_first_name()} {self.get_last_name()}\n{self.units_enrolled}")

    def enroll(self, unit_object):
        """Add a unit object to the student's enrolled list."""
        self.units_enrolled.append(unit_object)

    def display_info(self):
        """Print student name and student ID."""
        super().display_info()
        print(f"{self.__student_id}")

    def get_role(self):
        """Return the role label for this class."""
        return "Student"

    def update(self, message):
        """Receive and print a notification from an observed unit."""
        print(f"Notification for {self.get_full_name()}: {message}")

    def get_grade(self, score: int) -> str:
        """Return a grade for a score from 0 to 100 inclusive."""
        if score < 0 or score > 100:
            raise InvalidDataError("Score must be between 0 and 100.")

        if score >= 80:
            return "HD"
        if score >= 70:
            return "D"
        if score >= 60:
            return "C"
        if score >= 50:
            return "P"
        return "F"

class UndergraduateStudent(Student):
    """Represents an undergraduate student with a major field."""

    def __init__(self, student_id, first_name, last_name, major):
        """Initialise an undergraduate student."""
        super().__init__(student_id, first_name, last_name)
        self._major = major

    def display_info(self):
        """Print standard student details and the declared major."""
        super().display_info()
    #    print(self.get_student_id())
        print(f"{self._major}")

    def get_grade(self, score: int) -> str:
        """Return the undergraduate grade for a score from 0 to 100."""
        return super().get_grade(score)

class PostgraduateStudent(Student):
    """Represents a postgraduate student with a research topic."""

    def __init__(self, student_id, first_name, last_name, research_topic):
        """Initialise a postgraduate student."""
        super().__init__(student_id, first_name, last_name)
        self._research_topic = research_topic

    def display_info(self):
        """Print standard student details and the research topic."""
        super().display_info()
        print(f"{self._research_topic}")

    def get_grade(self, score: int) -> str:
        """Return the postgraduate grade for a score from 0 to 100."""
        return super().get_grade(score)

class Enrollable(ABC):
    """Interface for objects that can enroll students."""

    @abstractmethod
    def add_student(self, student):
        """Add a student to the enrollable object."""
        pass

    @abstractmethod
    def get_enrollment_count(self):
        """Return the number of enrolled students."""
        pass

class Reportable(ABC):
    """Interface for objects capable of generating reports."""

    @abstractmethod
    def generate_report(self):
        """Return a text report describing current state."""
        pass
    
class Unit(Enrollable, Reportable):
    """Represents a teaching unit and manages unit enrollment."""

    def __init__(self, unit_code, unit_name, max_students: int = 10):
        """Initialise a unit with code, name, and maximum class capacity."""
        self.unit_code = unit_code
        self.unit_name = unit_name
        self.max_students = max_students
        self.students = []
        self._observers: list[Student] = []


    def __repr__(self):
        """Return a short display string for the unit."""
        return f"{self.unit_code} - {self.unit_name}"

    def get_enrollment_count(self) -> int:
        """Return the current number of enrolled students."""
        return len(self.students)

    def _is_valid_student(self, student) -> bool:
        """Return True when the provided object is a Student instance."""
        return isinstance(student, Student)

    def _is_already_enrolled(self, student: Student) -> bool:
        """Return True when the student is already in this unit."""
        return student in self.students

    def _has_capacity(self) -> bool:
        """Return True when the unit can accept at least one more student."""
        return len(self.students) < self.max_students

    def add_student(self, student: Student) -> str:
        """
        Enroll a student in this unit.

        Raises:
            EnrollmentError: If the object is not a Student, the student is already
                enrolled, or the unit is at capacity.
        """
        if not self._is_valid_student(student):
            raise EnrollmentError("Must be a Student.")
        
        if self._is_already_enrolled(student):
            raise EnrollmentError(f"{student.get_full_name()} is already enrolled.")
        
        if not self._has_capacity():
            message = f"Unit {self.unit_code} is now full. Cannot enroll {student.get_full_name()}."
            self.notify(message)
            raise EnrollmentError(message)

        self.students.append(student)
        return f"{student.get_full_name()} enrolled successfully."
    
    def generate_report(self):
        """Generate and return a simple enrollment report for this unit."""
        student_list = "\n  ".join(str(student) for student in self.students)
        return f"Unit Code: {self.unit_code}\nName: {self.unit_name}\nStudents:\n  {student_list}"

    def attach(self, observer: 'Student'):
        """Attach a student observer to receive unit notifications."""
        self._observers.append(observer)

    def detach(self, observer: 'Student'):
        """Detach a student observer from unit notifications."""
        self._observers.remove(observer)

    def notify(self, message="Unit is already full"):
        """Send a notification message to all attached student observers."""
        for observer in self._observers:
            observer.update(message)


class Course:
    """Represents a course that contains multiple units."""

    def __init__(self, course_code: str, course_name: str):
        """Initialise a course with a code, name, and empty unit list."""
        self.course_code = course_code
        self.course_name = course_name
        self.units = []

    def add_unit(self, unit: Unit):
        """Add a unit to the course if it is not already present."""
        if unit not in self.units:
            self.units.append(unit)

    
'''
    def add_student(self, student):
        if student.get_role() == "Student":
            self.students.append(student)
        else:
            print("Person must be a student")
'''
class SchoolRegistryMeta(type):
    """Metaclass implementing singleton behaviour for registry classes."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Return an existing instance or create one if it does not yet exist."""
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class SchoolRegistry(metaclass=SchoolRegistryMeta):
    """Singleton registry for storing and looking up people by ID."""

    def __init__(self):
        """Initialise an empty internal registry dictionary."""
        self.registry = {}

    def add_person(self, person):
        """Add a student to the registry using their student ID as the key."""
        person_id = str(person.get_student_id())
        if person_id not in self.registry:
            self.registry[person_id] = person
    
    def get_person_by_id(self, person_id):
        """Print a person's details when the ID exists in the registry."""
        person_id = str(person_id)
        try:
            if person_id in self.registry:
                person = self.registry[person_id]
                print(f"{person_id} - {person.get_full_name()}")
                return person
            raise AttributeError(f"No person found for ID: {person_id}")
        except AttributeError as e:
            print(f"Error creating person: {e}")


class EnrollmentSystem:
    """Singleton service for managing enrollments and timetable queries.

    This class coordinates registry lookups and unit-level enrollment logic.
    It stores a mapping of unit codes to ``Unit`` objects and exposes helper
    methods for enrolling students and retrieving enrollment/schedule views.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Create or return the shared EnrollmentSystem singleton instance.

        Args:
            *args: Positional arguments passed during instantiation.
            **kwargs: Keyword arguments passed during instantiation.

        Returns:
            EnrollmentSystem: The single shared instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialise singleton dependencies and local unit storage.

        Creates/uses the shared ``SchoolRegistry`` instance and prepares an
        in-memory dictionary used to map ``unit_code`` to ``Unit`` objects.
        """
        self.registry = SchoolRegistry()
        self.units = {}

    def enroll_student_in_unit(self, student_id, unit_code):
        """Enroll a registered student into a registered unit.

        The method validates that the student exists in the registry and that the
        target unit exists in the system. It then checks prerequisite completion
        before delegating enrollment to ``Unit.add_student``. Any lookup/attribute
        problems are converted to ``InvalidDataError``. Enrollment rule failures
        (for example duplicate enrollment, full unit, or missing prerequisites)
        are raised as ``EnrollmentError`` with context.

        Args:
            student_id: Identifier used to locate the student in the registry.
            unit_code: Code used to locate the unit in ``self.units``.

        Returns:
            str: A success message returned by ``Unit.add_student`` when
                enrollment completes.

        Raises:
            InvalidDataError: If student_id does not map to a valid Student,
                unit_code does not map to a valid Unit, or required attributes
                are missing during lookup/validation.
            EnrollmentError: If prerequisites are not satisfied, the student is
                already enrolled, or the unit is at capacity.
        """
        try:
            registry = self.registry
            student = registry.get_person_by_id(student_id)
            if not isinstance(student, Student):
                raise AttributeError(f"No student found for ID: {student_id}")

            unit = self.units.get(unit_code)
            if not isinstance(unit, Unit):
                raise AttributeError(f"No unit found for code: {unit_code}")

            if not check_prerequisites(student, unit):
                prerequisites = getattr(unit, "prerequisites", [])
                completed = getattr(student, "units_completed", [])
                missing = [code for code in prerequisites if code not in completed]
                raise EnrollmentError(
                    f"Student {student.get_student_id()} does not meet prerequisites "
                    f"for {unit_code}. Missing: {missing}"
                )

            status_message = unit.add_student(student)
            print(f"Enrollment successful: {status_message}")
            return status_message
        
        except AttributeError as e:
            print(f"Attribute missing: {e}")
            raise InvalidDataError(f"Enrollment failed due to invalid data: {e}") from e
        except EnrollmentError as e:
            print(f"Enrollment error: {e}")
            raise EnrollmentError(f"Enrollment failed: {e}") from e

    def get_unit_enrollments(self, unit_code):
        """Return enrollment summary data for a specific unit code.

        Args:
            unit_code: Code of the unit to inspect.

        Returns:
            dict: Enrollment summary containing ``unit_code``, ``unit_name``,
                ``enrollment_count``, and a list of enrolled student names.

        Raises:
            InvalidDataError: If ``unit_code`` is not mapped to a valid
                ``Unit`` instance.
        """
        unit = self.units.get(unit_code)
        if not isinstance(unit, Unit):
            raise InvalidDataError(f"No unit found for code: {unit_code}")
        return {
            "unit_code": unit.unit_code,
            "unit_name": unit.unit_name,
            "enrollment_count": unit.get_enrollment_count(),
            "students": [s.get_full_name() for s in unit.students],
        }

    def get_student_schedule(self, student_id):
        """Return a student's enrolled-unit schedule as display strings.

        Args:
            student_id: Identifier used to locate the student in the registry.

        Returns:
            list[str]: List of unit string representations for the student's
                current ``units_enrolled``.

        Raises:
            InvalidDataError: If ``student_id`` is not mapped to a valid
                ``Student`` instance.
        """
        student = self.registry.get_person_by_id(student_id)
        if not isinstance(student, Student):
            raise InvalidDataError(f"No student found for ID: {student_id}")
        return [str(unit) for unit in student.units_enrolled]


class PersonFactory:
    """Factory for creating person-related objects from a type label."""

    def create_person(self, person_type, **kwargs):
        """Create and return a person object based on person_type and keyword data."""
        # Normalise input so callers can use mixed-case labels.
        person_type = person_type.lower()  # normalise so "Student" and "student" both work
        try:
            # Shared required field check before type-specific construction.
            if "last_name" not in kwargs:
                raise InvalidDataError(
                    f"Missing required data for '{person_type}': 'last_name'"
                )

            # Build the concrete object that matches the requested person type.
            if person_type == "student":
                print(f"Creating student... {kwargs['last_name']}")
                return Student(
                    kwargs["student_id"],
                    kwargs["first_name"],
                    kwargs["last_name"]
                )
            elif person_type == "teacher":
                print(f"Creating teacher... {kwargs['last_name']}")
                return Teacher(
                    kwargs["first_name"],
                    kwargs["last_name"],
                    kwargs["employee_id"],
                    kwargs["subject_taught"]
                )
            elif person_type == "undergraduate":
                print(f"Creating undergraduate student... {kwargs['last_name']}")
                return UndergraduateStudent(
                    kwargs["student_id"],
                    kwargs["first_name"],
                    kwargs["last_name"],
                    kwargs["major"]
                )
            elif person_type == "postgraduate":
                print(f"Creating postgraduate student... {kwargs['last_name']}")
                return PostgraduateStudent(
                    kwargs["student_id"],
                    kwargs["first_name"],
                    kwargs["last_name"],
                    kwargs["research_topic"]
                )
            else:
                # Unknown type values are treated as a factory-level error.
                raise ValueError(f"Unknown person type: '{person_type}'")
        except ValueError as e:
            # Wrap unsupported type requests with a domain-specific exception.
            raise FactoryError(f"Failed to create person of type '{person_type}'") from e
        except KeyError as e:
            # Missing constructor fields are reported as invalid input data.
            raise InvalidDataError(f"Missing required data for '{person_type}': {e}") from e
        except AttributeError as e:
            # Catch malformed input objects accessed during object construction.
            raise InvalidDataError(f"Invalid data provided for '{person_type}': {e}") from e
        finally:
            # Keep an audit-style log regardless of success or failure.
            print("Person creation attempted with type:", person_type)


def iterate(mix):
    """Call display_info on every object in the provided collection."""
    for obj in mix:
        obj.display_info()


def test_polymorphism():
    """Demonstrate polymorphism by calling display_info on mixed person types."""
    people = [
        Teacher("Terry", "Harrison", 8874, "Physics"),
        Student(3001, "Mia", "Lopez"),
        UndergraduateStudent(3002, "Ethan", "Ng", "Cybersecurity"),
        PostgraduateStudent(3003, "Ava", "Singh", "AI in Healthcare"),
    ]

    print("\n=== Polymorphism Demo ===")
    iterate(people)


def check_prerequisites(student, unit):
    """Return True when a student satisfies all prerequisites for a unit."""
    prerequisites = getattr(unit, "prerequisites", [])
    try:
        if not prerequisites:
            return True
    except NameError:
        return True

    units_completed = getattr(student, "units_completed", [])
    return set(prerequisites).issubset(set(units_completed))

def register_student_for_unit(student, unit):
    """Register a student into a unit and print status or enrollment errors."""
    if isinstance(unit, Enrollable):
        try:
            message = unit.add_student(student)
            if message:
                print(message)
        except EnrollmentError as e:
            print(f"Enrollment error: {e}")
    else:
        print("Error, unit can not be enrolled into")

def main():
    """Run focused tests for Unit.add_student behavior."""
    print("=== Unit.add_student Tests ===")

    unit = Unit("NIT2215", "Data Revolution", max_students=2)
    student1 = Student(1254, "Ben", "Morovan")
    student2 = Student(6454, "Billy", "Hartley")
    student3 = Student(9000, "John", "Smith")

    # Optional observer to show full-capacity notifications.
    unit.attach(student1)

    print("\n1) Valid enrollment")
    try:
        print(unit.add_student(student1))
    except EnrollmentError as e:
        print(f"Unexpected error: {e}")

    print("\n2) Duplicate enrollment")
    try:
        print(unit.add_student(student1))
    except EnrollmentError as e:
        print(f"Unexpected error: {e}")

    print("\n3) Invalid type enrollment")
    try:
        invalid_student = cast(Student, "not-a-student")
        print(unit.add_student(invalid_student))
    except EnrollmentError as e:
        print(f"Unexpected error: {e}")

    print("\n4) Capacity limit")
    try:
        print(unit.add_student(student2))
        print(unit.add_student(student3))
    except EnrollmentError as e:
        print(f"Unexpected error: {e}")
    print("--------line_break--------")
    test_polymorphism()


if __name__ == "__main__":
    main()
