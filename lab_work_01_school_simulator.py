class Student:
    def __init__(self, student_id, first_name, last_name):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.units_enrolled = []

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def display_details(self):
        print(f"{self.student_id}\n{self.first_name} {self.last_name}\n{self.units_enrolled}")

    def enroll(self, unit_object):
        self.units_enrolled.append(unit_object)

class Unit:
    def __init__(self, unit_code, unit_name):
        self.unit_code = unit_code
        self.unit_name = unit_name
    def __repr__(self):
        return f"{self.unit_code} - {self.unit_name}"


if __name__ == "__main__":
    student1 = Student("1254", "Ben", "Morovan")
    student2 = Student("6454", "Billy", "Hartley")
    
    print(student1.get_full_name())
    print(student2.units_enrolled)
    unit1 = Unit("NIT2215", "Data Revolution")
    student2.enroll(unit1)
    student2.display_details()
    student1.display_details()
    print(unit1)
