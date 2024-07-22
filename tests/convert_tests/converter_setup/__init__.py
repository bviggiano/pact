import json
import os
from convert_tests.converter_setup.ex_codeblock import CODEBLOCK_TYPES
from convert_tests.converter_setup.ex_masks import MASKTYPES
from convert_tests.converter_setup.fail_logging import (
    log_failed_test,
    failed_test_output_dir,
)


def get_converted_file_content(converter, file_path, tmp_path):
    """
    Converts a file and returns the contents of the converted file.
    """
    # Convert the file
    converter.convert_file(source_file_path=file_path, destination_folder_path=tmp_path)

    # Get the file name
    file_name = os.path.basename(file_path)

    # Read in the converted file
    converted_file_path = os.path.join(tmp_path, file_name)

    with open(converted_file_path, "r") as file:
        return file.read()


def file_eq(file_path_1: str, file_path_2: str) -> bool:
    """
    Determines if two files have the exact same contents.

    Args:
        file_path_1 (str): The path to the first file.
        file_path_2 (str): The path to the second file.
    """
    with open(file_path_1, "r") as file:
        file_1_contents = file.read()

    with open(file_path_2, "r") as file:
        file_2_contents = file.read()

    return file_1_contents == file_2_contents


def ipynb_eq(file_path_1: str, file_path_2: str) -> bool:
    """
    Determines if two ipynb should be considered equal, ignoring the metadata.

    Args:
        file_path_1 (str): The path to the first file.
        file_path_2 (str): The path to the second file.

    Returns:
        bool: True if the files are equal, False otherwise
    """

    with open(file_path_1, "r") as file:
        file_1_contents = file.read()

    with open(file_path_2, "r") as file:
        file_2_contents = file.read()

    # Load the json contents
    file_1_json = json.loads(file_1_contents)
    file_2_json = json.loads(file_2_contents)

    # Ensure all cells are the same
    return file_1_json["cells"] == file_2_json["cells"]
