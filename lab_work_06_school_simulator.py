
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


class Person(ABC):
    def __init__(self, first_name, last_name):
        self._first_name = first_name
        self._last_name = last_name

    def display_info(self):
        print(f"{self._first_name} {self._last_name}")

    def get_first_name(self):
        return self._first_name
    
    def set_first_name(self, new_first_name):
        self._first_name = new_first_name

    def get_last_name(self):
        return self._last_name

    def set_last_name(self, new_last_name):
        self._last_name = new_last_name   
 
    def get_full_name(self):
        return f"{self.get_first_name()} {self.get_last_name()}"    

    @property
    def full_name(self):
        return f"{self._first_name} {self._last_name}"
    
    @abstractmethod
    def get_role(self):
        pass

class Teacher(Person):
    def __init__(self, first_name, last_name, employee_id, subject_taught):
        super().__init__(first_name, last_name)
        self.__employee_id = employee_id
        self._subject_taught = subject_taught
    
    def display_info(self):
        super().display_info()
        print(f"{self.__employee_id} {self._subject_taught}")

    def get_role(self):
        return "Teacher"

    @property
    def employee_id(self):
        return self.__employee_id
    
    @property
    def subject_taught(self):
        return self._subject_taught
    
    @subject_taught.setter
    def subject_taught(self, new_subject):
        if new_subject != "":
            self._subject_taught = new_subject
        else:
            print("Can not be left blank.")

class Student(Person):
    def __init__(self, student_id, first_name, last_name):
        super().__init__(first_name, last_name)
        self.__student_id = student_id
        self.units_enrolled = []
  
    def get_student_id(self):
        return self.__student_id
    
    def display_details(self):
        print(f"{self.__student_id}\n{self.get_first_name()} {self.get_last_name()}\n{self.units_enrolled}")

    def enroll(self, unit_object):
        self.units_enrolled.append(unit_object)

    def display_info(self):
        super().display_info()
        print(f"{self.__student_id}")

    def get_role(self):
        return "Student"

    def update(self, message):
        print(f"Notification for {self.get_full_name()}: {message}")

class UndergraduateStudent(Student):
    def __init__(self, student_id, first_name, last_name, major):
        super().__init__(student_id, first_name, last_name)
        self._major = major

    def display_info(self):
        super().display_info()
        print(f"{self._major}")

class PostgraduateStudent(Student):
    def __init__(self, student_id, first_name, last_name, research_topic):
        super().__init__(student_id, first_name, last_name)
        self._research_topic = research_topic

    def display_info(self):
        super().display_info()
        print(f"{self._research_topic}")

class Enrollable(ABC):

    @abstractmethod
    def add_student(self, student):
        pass

    @abstractmethod
    def get_enrollment_count(self):
        pass

class Reportable(ABC):
    @abstractmethod
    def generate_report(self):
        pass
    
class Unit(Enrollable, Reportable):
    def __init__(self, unit_code, unit_name):
        self.unit_code = unit_code
        self.unit_name = unit_name
        self.students = []
        self._observers: list[Student] = []


    def __repr__(self):
        return f"{self.unit_code} - {self.unit_name}"

    def get_enrollment_count(self):
        return len(self.students)

    def add_student(self, student):
        if not isinstance(student, Student):      # ✅ checks actual type
            raise EnrollmentError("Must be a Student.")                              #  guard clauses
        elif student in self.students:     # duplicate check
            raise EnrollmentError(f"{student.get_full_name()} is already enrolled.")
        elif len(self.students) > 0:
            self.notify()
            message = f"Unit {self.unit_code} is now full. Cannot enroll {student.get_full_name()}."
            raise EnrollmentError(message)
        else:
            self.students.append(student)
            print(f"{student.get_full_name()} enrolled successfully.")
    
    def generate_report(self):
        student_list = "\n  ".join(str(student) for student in self.students)
        return f"Unit Code: {self.unit_code}\nName: {self.unit_name}\nStudents:\n  {student_list}"

    def attach(self, observer: 'Student'):
        self._observers.append(observer)

    def detach(self, observer: 'Student'):
        self._observers.remove(observer)

    def notify(self, message="Unit is already full"):
        for observer in self._observers:
            observer.update(message)

    
'''
    def add_student(self, student):
        if student.get_role() == "Student":
            self.students.append(student)
        else:
            print("Person must be a student")
'''
class SchoolRegistryMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class SchoolRegistry(metaclass=SchoolRegistryMeta):
    def __init__(self):
        self.registry = {}

    def add_person(self, person):
        if person.get_student_id() not in self.registry:
            self.registry[f"{person.get_student_id()}"] = f"{person._first_name} {person._last_name}"
    
    def get_person_by_id(self, person_id):
        person_id = str(person_id)
        if person_id in self.registry:
            print(f"{person_id} - {self.registry[person_id]}")
        else:
            print("Error")


class PersonFactory:
    def create_person(self, person_type, **kwargs):
        person_type = person_type.lower()  # normalise so "Student" and "student" both work
        try:
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
            print(f"Error creating person: {e}")
            raise FactoryError(f"Failed to create person of type '{person_type}'") from e
        except KeyError as e:
            print(f"Incorrect keyword: {e}")
            raise InvalidDataError(f"Missing required data for '{person_type}': {e}") from e
        finally:
            print("Person creation attempted with type:", person_type)


def iterate(mix):
    for obj in mix:
        obj.display_info()

def register_student_for_unit(student, unit):
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
    student3 = factory.create_person("student",   student_id=9001,  first_name="Ana",   last_name="Cruz")
    teacher1 = factory.create_person("teacher",   first_name="Terry", last_name="Harrison", employee_id=8874, subject_taught="Physics")
    register_student_for_unit(student3, unit1)
    register_student_for_unit(teacher1, unit1)