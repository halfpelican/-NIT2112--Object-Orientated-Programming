
from abc import ABC, abstractmethod


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

class UndergraduateStudent(Student):
    """Represents an undergraduate student with a major field."""

    def __init__(self, student_id, first_name, last_name, major):
        """Initialise an undergraduate student."""
        super().__init__(student_id, first_name, last_name)
        self._major = major

    def display_info(self):
        """Print standard student details and the declared major."""
    #   super().display_info()
        print(self.get_student_id())
        print(f"{self._major}")

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

    def add_student(self, student: Student) -> str:
        """
        Enroll a student in this unit.

        Raises:
            EnrollmentError: If the object is not a Student, the student is already
                enrolled, or the unit is at capacity.
        """
        if not isinstance(student, Student):      # ✅ checks actual type
            raise EnrollmentError("Must be a Student.")                              #  guard clauses
        
        if student in self.students:     # duplicate check
            raise EnrollmentError(f"{student.get_full_name()} is already enrolled.")
        
        if len(self.students) >= self.max_students:
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
    """Singleton scaffold for managing student enrollments and schedules."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Create one shared EnrollmentSystem instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialise the system and capture the singleton SchoolRegistry instance."""
        self.registry = SchoolRegistry()
        self.units = {}

    def enroll_student_in_unit(self, student_id, unit_code):
        """Enroll a student identified by student_id into the unit identified by unit_code."""
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
        """Return enrollment information for the given unit code.

        Returns a dict with unit details and enrolled student names, or raises
        InvalidDataError when the unit code is not registered.
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
        """Return the list of units scheduled for the given student ID.

        Returns a list of unit repr strings, or raises InvalidDataError when
        the student ID is not present in the registry.
        """
        student = self.registry.get_person_by_id(student_id)
        if not isinstance(student, Student):
            raise InvalidDataError(f"No student found for ID: {student_id}")
        return [str(unit) for unit in student.units_enrolled]


class PersonFactory:
    """Factory for creating person-related objects from a type label."""

    def create_person(self, person_type, **kwargs):
        """Create and return a person object based on person_type and keyword data."""
        person_type = person_type.lower()  # normalise so "Student" and "student" both work
        try:
            if "last_name" not in kwargs:
                raise InvalidDataError(
                    f"Missing required data for '{person_type}': 'last_name'"
                )

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
                raise ValueError(f"Unknown person type: '{person_type}'")
        except ValueError as e:
            raise FactoryError(f"Failed to create person of type '{person_type}'") from e
        except KeyError as e:
            raise InvalidDataError(f"Missing required data for '{person_type}': {e}") from e
        except AttributeError as e:
            raise InvalidDataError(f"Invalid data provided for '{person_type}': {e}") from e
        finally:
            print("Person creation attempted with type:", person_type)


def iterate(mix):
    """Call display_info on every object in the provided collection."""
    for obj in mix:
        obj.display_info()


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

    

if __name__ == "__main__":
    student1 = Student(1254, "Ben", "Morovan")
    student2 = Student(6454, "Billy", "Hartley")
    unit1 = Unit("NIT2215", "Data Revolution")
    unit1.add_student(student1)
    unit1.attach(student1)
    unit1.add_student(student2)
    factory = PersonFactory()
    student3 = factory.create_person("student", student_id=9000, first_name="John", last_name="Smith")
    try:
        print("Reading data...")
        student4 = factory.create_person("student", student_id=9001, first_name="Ana", last_name="Cruz")
    except (FactoryError, InvalidDataError) as e:
        print(f"Error creating person: {e}")
        print(f"Caused by: {e.__cause__}")   
    finally:
        print("Closing file...")
    register_student_for_unit(student3, unit1)
    reg1 = SchoolRegistry()
    reg2 = SchoolRegistry()
    print(reg1 is reg2)  # True
    reg1.add_person(student1)
    reg1.get_person_by_id(1254)

    # Review flow: create via factory, register, map unit, and test enrollment paths.
    student5 = factory.create_person(
        "student", student_id=9010, first_name="Lena", last_name="Parker"
    )
    student5.units_completed = ["NIT1201"]
    reg1.add_person(student5)

    enrollment_system = EnrollmentSystem()
    unit2 = Unit("NIT3001", "Advanced OOP")
    unit2.prerequisites = ["NIT1201"]
    enrollment_system.units[unit2.unit_code] = unit2

    print(enrollment_system.enroll_student_in_unit(9010, "NIT3001"))

    # Non-existent student ID — expect a graceful error message, not a crash.
    try:
        print(enrollment_system.enroll_student_in_unit(9999, "NIT3001"))
    except (InvalidDataError, EnrollmentError) as e:
        print(f"Could not enroll: {e}")

    # Non-existent unit code — expect a graceful error message, not a crash.
    try:
        print(enrollment_system.enroll_student_in_unit(9010, "UNKNOWN"))
    except (InvalidDataError, EnrollmentError) as e:
        print(f"Could not enroll: {e}")

    legacy = LegacyHRSystem()
    adapter = HRAdapter(legacy)
    teacher1 = adapter.get_teacher_details(8874)
    student6 = factory.create_person("undergraduate", student_id=9100, first_name="Kramer", last_name="Lauder", major="Computer Science")
    teacher1.display_info()
    student6.display_info()
