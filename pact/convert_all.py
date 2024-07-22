"""
convert_all.py

This script converts all solution versions of assignments in the assignments
folder into student versions.
"""

import os
from pact.convert_assignment import PrimeConverter

ASSIGNMENTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assignments"
)


if __name__ == "__main__":

    print("Converting all assignments...")

    # Create the assignments folder if it does not exist
    os.makedirs(ASSIGNMENTS_PATH, exist_ok=True)

    # Create a new PrimeConverter
    converter = PrimeConverter()

    # Convert each directory in the assignments folder
    for assignment_name in os.listdir(ASSIGNMENTS_PATH):

        # Get the source path of the assignment directory
        assignment_path = os.path.join(ASSIGNMENTS_PATH, assignment_name)

        # If the assignment is a directory, convert it
        if os.path.isdir(assignment_path):
            converter.convert(assignment_path)
            print(f"- Converted {assignment_name}")

    print("- All assignments converted.")
