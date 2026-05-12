"""
prime_converter.py

This module contains the PrimeConverter class, which is used to convert solution versions of assignments into student versions.
"""

from __future__ import annotations

import logging
import os
import shutil
from pact.convert.utils.file_converter import FileConverter
from pact.zip.zip_assignment import zip_assignment_dir
from pact.zip.zip_submission import create_submission_file
import re

logger = logging.getLogger(__name__)

# The name of the generated student version of the assignment
GENERATED_LOCATION_NAME = "STUDENT_VERSION"

# Special file names to ignore during conversion
BLACK_LIST_FILE_NAME = "black_list.pact"
SUB_LIST_FILE_NAME = "sub_list.pact"
OPTIONS_FILE_NAME = "options.pact"

# Patterns always excluded from STUDENT_VERSION/ output, even without a
# per-assignment black_list.pact. Per-assignment black lists extend these.
#
# Patterns are Python regexes matched against the full path with re.search.
# Directory-style entries use (^|/)name($|/) so they only match the directory
# itself or descendants — not unrelated files that happen to contain the name
# as a substring (e.g. `venv` should not match `prevention.py`).
DEFAULT_BLACK_LIST = [
    # OS noise
    r"\.DS_Store$",
    r"(^|/)Thumbs\.db$",
    r"(^|/)desktop\.ini$",
    # Jupyter checkpoints (top-level or nested)
    r"\.ipynb_checkpoints",
    # Compiled Python / bytecode / native extensions
    r"__pycache__",
    r"\.py[cod]$",
    r"\$py\.class$",
    r"\.so$",
    # Python virtual environments
    r"(^|/)\.venv($|/)",
    r"(^|/)venv($|/)",
    r"(^|/)env($|/)",
    r"(^|/)ENV($|/)",
    # Build / packaging artifacts
    r"(^|/)build($|/)",
    r"(^|/)dist($|/)",
    r"(^|/)wheels($|/)",
    r"(^|/)eggs($|/)",
    r"(^|/)\.eggs($|/)",
    r"\.egg-info($|/)",
    r"\.egg$",
    r"(^|/)MANIFEST$",
    # IDE / editor metadata
    r"(^|/)\.idea($|/)",
    r"(^|/)\.vscode($|/)",
    r"\.swp$",
    # Type checker / linter caches
    r"(^|/)\.mypy_cache($|/)",
    r"(^|/)\.pytype($|/)",
    r"(^|/)\.ruff_cache($|/)",
    r"(^|/)\.?dmypy\.json$",
    # Test / coverage artifacts
    r"(^|/)\.pytest_cache($|/)",
    r"(^|/)\.tox($|/)",
    r"(^|/)\.nox($|/)",
    r"(^|/)\.coverage(\..*)?$",
    r"(^|/)coverage\.xml$",
    r"(^|/)htmlcov($|/)",
    r"(^|/)\.hypothesis($|/)",
    # pip artifacts
    r"(^|/)pip-log\.txt$",
    r"(^|/)pip-delete-this-directory\.txt$",
]


class PrimeConverter:
    """
    Converts solution versions of assignments into student versions.
    """

    def __init__(self):
        """
        Creates a new PrimeConverter.
        """

        # Create a file converter
        self.file_converter = FileConverter()

        # Placeholder for the master generation location
        self.master_generation_location = None

        # Black list starts with built-in defaults; per-assignment patterns
        # are appended in load_black_list().
        self.black_list = list(DEFAULT_BLACK_LIST)

        # Placeholder for white list
        self.sub_list = []

        # Placeholder for options
        self.options = []

    def reset(self):
        """
        Resets the PrimeConverter.
        """
        self.master_generation_location = None
        self.black_list = list(DEFAULT_BLACK_LIST)
        self.sub_list = []
        self.options = []

    def load_black_list(self, source_folder: str):
        """
        Loads the black list of files to ignore during conversion. Per-assignment
        patterns extend DEFAULT_BLACK_LIST rather than replacing it.
        """

        if not os.path.exists(os.path.join(source_folder, BLACK_LIST_FILE_NAME)):
            return

        # Load the black list
        with open(os.path.join(source_folder, BLACK_LIST_FILE_NAME), "r") as file:
            user_patterns = [
                line for line in file.read().splitlines() if line.strip()
            ]
        self.black_list = list(DEFAULT_BLACK_LIST) + user_patterns

    def load_sub_list(self, source_folder: str):
        """
        Loads the submission list of files include in student submission generator.
        """

        if not os.path.exists(os.path.join(source_folder, SUB_LIST_FILE_NAME)):
            return

        # Load the white list
        with open(os.path.join(source_folder, SUB_LIST_FILE_NAME), "r") as file:
            self.sub_list = file.read().splitlines()

    def load_options(self, source_folder: str):
        """
        Loads the options for the conversion.
        """

        if not os.path.exists(os.path.join(source_folder, OPTIONS_FILE_NAME)):
            return

        # Load the options
        with open(os.path.join(source_folder, OPTIONS_FILE_NAME), "r") as file:
            self.options = file.read().splitlines()

    def convert(self, source_file_or_folder: str):
        """
        Converts the solution version of the assignment file/folder into student versions.

        Args:
            source_file_or_folder (str): The path to the solution version of the assignment file/folder.
        """

        # Reset the converter
        self.reset()

        # If we have a folder, check if special files exist
        if os.path.isdir(source_file_or_folder):
            self.load_black_list(source_file_or_folder)
            self.load_sub_list(source_file_or_folder)
            self.load_options(source_file_or_folder)
            logger.debug("Black list: %s", self.black_list)
            logger.debug("Sub list: %s", self.sub_list)
            logger.debug("Options: %s", self.options)

        # Set the master generation location (to be used by the conversion filter)
        self.master_generation_location = self._prepare_generation_location(
            source_file_or_folder
        )

        # Convert the source file/folder
        self._convert(source_file_or_folder, self.master_generation_location)

        # If the source file/folder is a folder, zip the folder
        if os.path.isdir(source_file_or_folder):

            # Create the student submission zip file
            if "no_submission_file" not in self.options:
                create_submission_file(
                    os.path.join(
                        self.master_generation_location,
                        os.path.basename(source_file_or_folder),
                    ),
                    sub_list=self.sub_list,
                )

            # Create the zipped assignment folder
            zip_assignment_dir(
                os.path.join(
                    self.master_generation_location,
                    os.path.basename(source_file_or_folder),
                )
            )

    def _convert(self, source_file_or_folder: str, generation_location: str):
        """
        Recursively converts all files/folders in the source file/folder into student versions.
        """

        # Check if the file/folder should be converted
        if not self.conversion_filter(source_file_or_folder):
            return

        # Check if the source file/folder is a file
        if os.path.isfile(source_file_or_folder):

            # Convert the file at this location
            self.file_converter.convert_file(
                source_file_path=source_file_or_folder,
                destination_folder_path=generation_location,
            )

        # Check if the source file/folder is a folder
        elif os.path.isdir(source_file_or_folder):

            # For each file/dir in the folder
            for member_name in os.listdir(source_file_or_folder):

                # Get the source path of the directory member
                member_name = os.path.join(source_file_or_folder, member_name)

                # Create the new generation location for the member
                member_generation_location = os.path.join(
                    generation_location, os.path.basename(source_file_or_folder)
                )

                # Create the new generation location for the member
                os.makedirs(member_generation_location, exist_ok=True)

                # Convert the member
                self._convert(member_name, member_generation_location)
        else:
            raise ValueError(
                f"The source file/folder {source_file_or_folder} does not exist."
            )

    def conversion_filter(self, source_file_or_folder: str):
        """
        Filters the files/folders to convert. Returns True if the file/folder
        should be converted, False otherwise.
        """

        # If the file/folder is in the generated location, don't convert it
        if self.master_generation_location == source_file_or_folder:
            return False

        # Ignore special files
        if os.path.basename(source_file_or_folder) in [
            BLACK_LIST_FILE_NAME,
            SUB_LIST_FILE_NAME,
            OPTIONS_FILE_NAME,
        ]:
            return False

        # Ignore files in the black list
        for black_list_item in self.black_list:
            if re.search(black_list_item, source_file_or_folder):
                return False

        return True

    def _prepare_generation_location(self, source_file_or_folder: str) -> str:
        """
        Determines the appropriate location to generate student versions of the
        assignment files.
        """

        # Check if the source file/folder is a file
        if os.path.isfile(source_file_or_folder):
            # Get the directory of the file
            generation_location = os.path.dirname(source_file_or_folder)
        # Check if the source file/folder is a folder
        elif os.path.isdir(source_file_or_folder):
            # Use the folder as the generation location
            generation_location = source_file_or_folder
        else:
            raise ValueError("The source file/folder does not exist.")

        # Create the student version folder
        generation_location = os.path.join(generation_location, GENERATED_LOCATION_NAME)

        # Remove the student version folder if it already exists (and it's contents)
        if os.path.exists(generation_location):
            shutil.rmtree(generation_location)

        # Create the student version folder
        os.makedirs(generation_location, exist_ok=False)

        # Return the path to the generation location
        return generation_location
