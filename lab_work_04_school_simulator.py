from abc import ABC, abstractmethod

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

class Unit(Enrollable):
    def __init__(self, unit_code, unit_name):
        self.unit_code = unit_code
        self.unit_name = unit_name
        self.students = []

    def __repr__(self):
        return f"{self.unit_code} - {self.unit_name}"

    def get_enrollment_count(self):
        return len(self.students)

    def add_student(self, student):
        if not isinstance(student, Student):      # ✅ checks actual type
            print("Must be a Student.")
            return                              #  guard clauses
        if student in self.students:     # duplicate check
            print(f"{student.get_full_name()} is already enrolled.")
            return          
        self.students.append(student)
        print(f"{student.get_full_name()} enrolled successfully.")
'''
    def add_student(self, student):
        if student.get_role() == "Student":
            self.students.append(student)
        else:
            print("Person must be a student")
'''
def iterate(mix):
    for obj in mix:
        obj.display_info()

def register_student_for_unit(student, unit):
    if isinstance(unit, Enrollable):
        unit.add_student(student)
    else:
        print("Error, unit can not be enrolled into")

    

if __name__ == "__main__":
    student1 = Student("1254", "Ben", "Morovan")
    student2 = Student("6454", "Billy", "Hartley")
    unit1 = Unit("NIT2215", "Data Revolution")
    student1.enroll(unit1)    
    print(student1.get_full_name())
    student1.display_details()
    teacher1 = Teacher("Terry", "Harrison", 8874, "Physics")
    print(teacher1.employee_id)
    print(teacher1.subject_taught)
    teacher1.subject_taught = "Biology"
    print(teacher1.subject_taught)
    print(student1.full_name)
    student1.display_info()
    teacher1.display_info()
    print("----___________-------------BREAK LINE---------_________---------")
    mix = [student1, student2, teacher1]
    iterate(mix)
    print(student1.get_role())
    print(teacher1.get_role())
#    rando = Person("Tommy", "Macron")
    undergraduate_student1 = UndergraduateStudent(5544, "Kelly", "Holmes", "Liberal Arts")
    undergraduate_student1.display_info()
    postgraduate_student1 = PostgraduateStudent(7744, "Michael", "Dus", "Supercomputing")
    print("----___________-------------BREAK LINE---------_________---------")
    postgraduate_student1.display_info()
    mix.append(undergraduate_student1)
    mix.append(postgraduate_student1)
    iterate(mix)
    print(Person.mro())
    unit1.add_student(student1)
    unit1.add_student(student2)
    print(f"Unit: {unit1}")
    print(f"Enrolled students: {unit1.get_enrollment_count()}")
    register_student_for_unit(teacher1, unit1)