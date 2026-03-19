class Teacher:
    def __init__(self, employee_id, subject_taught):
        self.__employee_id = employee_id
        self._subject_taught = subject_taught
    
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

class Student:
    def __init__(self, student_id, first_name, last_name):
        self.__student_id = student_id
        self._first_name = first_name
        self._last_name = last_name
        self.units_enrolled = []

    def get_full_name(self):
        return f"{self.get_first_name()} {self.get_last_name()}"
    
    def get_student_id(self):
        return self.__student_id
    
    def get_first_name(self):
        return self._first_name
    
    def set_first_name(self, new_first_name):
        self._first_name = new_first_name

    def get_last_name(self):
        return self._last_name

    def set_last_name(self, new_last_name):
        self._last_name = new_last_name   
    
    def display_details(self):
        print(f"{self.__student_id}\n{self.get_first_name()} {self.get_last_name()}\n{self.units_enrolled}")

    def enroll(self, unit_object):
        self.units_enrolled.append(unit_object)

    @property
    def full_name(self):
        return f"{self._first_name} {self._last_name}"
    
class Unit:
    def __init__(self, unit_code, unit_name):
        self.unit_code = unit_code
        self.unit_name = unit_name
    def __repr__(self):
        return f"{self.unit_code} - {self.unit_name}"


if __name__ == "__main__":
    student1 = Student("1254", "Ben", "Morovan")
    student2 = Student("6454", "Billy", "Hartley")
    unit1 = Unit("NIT2215", "Data Revolution")
    student1.enroll(unit1)    
    print(student1.get_full_name())
    student1.display_details()
    teacher1 = Teacher("8874", "Physics")
    print(teacher1.employee_id)
    print(teacher1.subject_taught)
    teacher1.subject_taught = ""
    print(teacher1.subject_taught)
    print(student1.full_name)

