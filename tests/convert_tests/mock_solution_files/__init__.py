import os

# Hardcode mock solution folder path
mock_solution_folder = "tests/convert_tests/mock_solution_files"


# Collect all the files in the mock solution folder (except __init__.py)
all_files = os.listdir(mock_solution_folder)

# Remove __init__.py and pycache
all_files.remove("__init__.py")
all_files.remove("__pycache__")

# Create a dictionary containing the file names as keys and their path's as values
MOCK_SOLUTION_FILES = {
    file_name: f"{mock_solution_folder}/{file_name}" for file_name in all_files
}
