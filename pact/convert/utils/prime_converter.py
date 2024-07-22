"""
prime_converter.py

This module contains the PrimeConverter class, which is used to convert solution versions of assignments into student versions.
"""

import os
import shutil
from pact.convert.utils.file_converter import FileConverter
from pact.zip.zip_assignment import zip_assignment_dir

# The name of the generated student version of the assignment
GENERATED_LOCATION_NAME = "STUDENT_VERSION"


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

    def convert(self, source_file_or_folder: str):
        """
        Converts the solution version of the assignment file/folder into student versions.
        """

        # Set the master generation location (to be used by the conversion filter)
        self.master_generation_location = self._prepare_generation_location(
            source_file_or_folder
        )

        # Convert the source file/folder
        self._convert(source_file_or_folder, self.master_generation_location)

        # If the source file/folder is a folder, zip the folder
        if os.path.isdir(source_file_or_folder):
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

        # Ignore pycache files
        if "__pycache__" in source_file_or_folder or ".pyc" in source_file_or_folder:
            return False

        # Ignore .DS_Store files
        if ".DS_Store" in source_file_or_folder:
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
