def calculate_grade(mark):
    if mark > 90: 
        print("Grade is 'HD'")
    elif mark > 80: 
        print("Grade is 'D'")
    elif mark > 70:
        print("Grade is 'C'")
    elif mark > 60:
        print("Grade is 'P'")
    else:
        print("Grade is 'N'")

number = 68


def calculate_grade(mark):
    if mark >= 80:
        return 'HD'
    elif mark >= 70:
        return 'D'
    elif mark >= 60:
        return 'C'
    elif mark >= 50:
        return 'P'
    else:
        return 'N'

if __name__ == "__main__":
    test_marks = [100, 85, 72, 61, 50, 30]
    for mark in test_marks:
        print(f"{mark}: {calculate_grade(mark)}")


