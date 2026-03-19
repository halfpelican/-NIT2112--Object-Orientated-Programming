"""1. Python Basics Review"""


def calculate_grade(mark):
        if mark >= 90:
            return 'HD'
        elif mark >= 80:
            return 'D'
        elif mark >= 70:
            return 'C'
        elif mark >= 60:
            return 'P'
        else:
            return 'N'
    

mark = 88
print(calculate_grade(mark))

"""2. Define the Student Class"""

class Student:
    def __init__(self, student_id, first_name, last_name):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.units_enrolled = []

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def display_details(self):
        print(f"Student ID: {self.student_id}")
        print(f"Full Name: {self.first_name} {self.last_name}")

    def enroll(self, unit_object):
        self.units_enrolled.append(unit_object)

class Unit:
    def __init__(self, unit_code, unit_name):
        self.unit_code = unit_code
        self.unit_name = unit_name

    def __repr__(self):
        return f"Unit(unit_code='{self.unit_code}', unit_name='{self.unit_name}')"

    def __str__(self):
        return f"{self.unit_code} - {self.unit_name}"

if __name__ == "__main__":
    student1 = Student("12345", "John", "Doe")
    student1.display_details()
    student2 = Student("67890", "Jane", "Smith")
    student2.display_details()
    print(student1.get_full_name())
    
    unit1 = Unit("CS101", "Introduction to Computer Science")
    student1.enroll(unit1)
    print(student1.units_enrolled)



