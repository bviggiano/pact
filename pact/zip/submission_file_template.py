"""
create_submission_zip.py

Creates a zip version of the assignment directory that you can submit.

NOTE: You may need to pip install the `zipfile` package to run this script by
running the following command in your terminal: `pip install zipfile`

Usage:
    1) Specify your student ID in the variable provided below.
    2) Run this script from the root directory of the assignment to create a zip file
    named '<STUDENT_ID>_submission.zip' in the assignment directory.

Run this script from the root directory of the assignment to create a zip file
named '<STUDENT_ID>_submission.zip' in the assignment directory. 
"""

# TODO: Specify your SUNet ID here
STUDENT_ID = None


# =============================================================================
# You do not need to modify anything below this line.
# =============================================================================

import os
import re
import zipfile


if STUDENT_ID is None:
    raise ValueError(
        "Please specify your SUNet ID in the STUDENT_ID variable in create_submission_zip.py"
    )

# The name of the generated submission file
SUBMISSION_FILE_NAME = f"{STUDENT_ID}_submission.zip"


# The list of files to include in the submission
PATTERNS_TO_INCLUDE = []


def create_submission_zip(source_directory: str):
    """
    Creates a zip version of the assignment directory to be submitted.

    Args:
        source_directory (str): The path to the assignment directory.

    Returns:
        str: The path to the generated zip file.
    """

    # Create the destination zip file
    destination_zip = os.path.join(source_directory, SUBMISSION_FILE_NAME)

    # Zip the assignment directory
    with zipfile.ZipFile(destination_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_filter(file_path):

                    # Flatten the overall structure for submission zip
                    arcname = os.path.basename(file_path)

                    # If no patterns are provided, include all files with the same structure
                    if not PATTERNS_TO_INCLUDE:
                        arcname = os.path.relpath(file_path, source_directory)

                    zipf.write(file_path, arcname)


def file_filter(file: str) -> bool:
    """
    Determines whether a file should be included in the submission zip.

    Args:
        file (str): The file name.

    Returns:
        bool: True if the file should be included, False otherwise.
    """

    # Do not include the submission zip in the submission zip
    if file == SUBMISSION_FILE_NAME:
        return False

    # Do not include any __pycache__ files in the submission zip
    if "__pycache__" in file or ".pyc" in file:
        return False

    # If a pattern is provided, only include files that match the pattern
    if PATTERNS_TO_INCLUDE:
        for pattern in PATTERNS_TO_INCLUDE:
            if re.search(pattern, file):
                return True
        return False

    # Otherwise, include all files
    return True


if __name__ == "__main__":
    create_submission_zip(os.getcwd())
