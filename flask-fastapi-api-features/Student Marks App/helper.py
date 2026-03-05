def validate_marks(marks):
    if not isinstance(marks, list):
        return False, "Marks must be a list"

    for mark in marks:
        if not isinstance(mark, int):
            return False, "All marks must be integers"

        if mark < 0 or mark > 100:
            return False, "Marks must be between 0 and 100"

    return True, None


def calculate_average(marks):
    return sum(marks) / len(marks)