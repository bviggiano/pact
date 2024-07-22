"""
zip_submission.py

This file creates a python file students can utilize to submit their assignments.
"""

import os
import zipfile
import shutil
import re
import tempfile
from typing import List

TEMPLATE = os.path.join(os.path.dirname(__file__), "submission_file_template.py")

REPLACE_STRING = "PATTERNS_TO_INCLUDE = []"


def create_submission_file(output_directory: str, sub_list: List[str] = None):
    """
    Creates a submission file for students to submit their assignments.

    Args:
        output_directory (str): The path to the directory to save the submission file in.
        sub_list (List[str], optional): A list of files to include in the submission.
            Defaults to None.
    """

    # Read in the template file
    with open(TEMPLATE, "r") as file:
        template = file.read()

    # If a sub list is provided, add it to the template
    if sub_list:
        template = template.replace(REPLACE_STRING, f"PATTERNS_TO_INCLUDE = {sub_list}")

    # Write the template to the output directory
    with open(os.path.join(output_directory, "create_submission_zip.py"), "w") as file:
        file.write(template)
