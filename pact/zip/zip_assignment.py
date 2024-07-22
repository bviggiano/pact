"""
zip_utils.py

This module contains utility functions for zipping directories.
"""

import os
import zipfile


def zip_assignment_dir(dir_path: str, output_dir: str = None):
    """
    Zips a directory into a zip file. If zip_path is not provided, the zip file
    will be saved in the same directory as the directory being zipped.

    Args:
        dir_path (str): The path to the directory to zip.
        output_dir (str, optional): The path to the directory to save the zip file
            in. Defaults to None.
    """

    # Ensure the directory exists and is a directory
    if not os.path.isdir(dir_path):
        raise ValueError(f"{dir_path} is not a directory")

    # Get the directory name to name the zip file
    dir_name = os.path.basename(dir_path)

    # Set the zip path if not provided
    zip_path = None
    if output_dir is None:
        zip_path = os.path.join(os.path.dirname(dir_path), f"{dir_name}.zip")
    else:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Set the zip path
        zip_path = os.path.join(output_dir, f"{dir_name}.zip")

    # Create a zip file
    with zipfile.ZipFile(zip_path, "w") as zipf:
        # Add all files in the directory to the zip file
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, dir_path))
