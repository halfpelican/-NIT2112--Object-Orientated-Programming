class Student:
    def __init__(self, student_id, first_name, last_name):
        self.__student_id = student_id
        self._first_name = first_name
        self._last_name = last_name
        self.units_enrolled = []

    def get_full_name(self):
        return f"{self._first_name} {self._last_name}"
    
    def display_details(self):
        print(f"{self.__student_id}\n{self._first_name} {self._last_name}\n{self.units_enrolled}")

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
    print(student1._Student__student_id)
