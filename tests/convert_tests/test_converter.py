import os
import sys
import pytest
from pytest import fixture

PROJECT_REPO = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(PROJECT_REPO)


from convert_tests.converter_setup import (
    get_converted_file_content,
    ipynb_eq,
    file_eq,
    log_failed_test,
    CODEBLOCK_TYPES,
    MASKTYPES,
)
from convert_tests.mock_solution_files import (
    MOCK_SOLUTION_FILES,
)

from pact.convert.utils.converter import FileConverter


# Create a FileConverter instance containing the codeblocks
@fixture
def converter():
    return FileConverter(codeblock_types=CODEBLOCK_TYPES, mask_types=MASKTYPES)


# Parameterize all files
all_file_params = [
    (file_name, file_path) for file_name, file_path in MOCK_SOLUTION_FILES.items()
]


@pytest.mark.parametrize("file_name, file_path", all_file_params)
def test_trigger_removal(converter, tmp_path, file_name, file_path):
    """
    This test ensures that all mask and codeblock trigger strings are removed
    from all of the converted files.
    """

    # Save errors
    errors = []

    # Get converted file content
    converted_contents = get_converted_file_content(converter, file_path, tmp_path)

    # Ensure that no trigger strings are present in the converted file
    for codeblock_type in CODEBLOCK_TYPES:
        if codeblock_type.start_trigger_str not in converted_contents:
            errors.append(
                "Start trigger string {codeblock_type.start_trigger_str} was not removed from {file_name}"
            )
        if codeblock_type.end_trigger_str not in converted_contents:
            errors.append(
                f"End trigger string {codeblock_type.end_trigger_str} was not removed from {file_name}"
            )

    for mask_type in MASKTYPES:
        if mask_type.trigger_str not in converted_contents:
            errors.append(
                f"Mask trigger string {mask_type.trigger_str} was not removed from {file_name}"
            )

    if errors:
        pytest.fail(
            log_failed_test(
                test_name="test_trigger_removal",
                source_file_path=file_path,
                tmp_dir=tmp_path,
                additional_messages=errors,
            )
        )


# Parameterize unchanged files
unchanged_file_params = [
    (file_name, file_path)
    for file_name, file_path in MOCK_SOLUTION_FILES.items()
    if "unchanged" in file_name
]


@pytest.mark.parametrize("file_name, file_path", unchanged_file_params)
def test_unchanged_files(converter, tmp_path, file_name, file_path):
    """
    Ensures that files that should not be changed are not changed.
    Args:
        converter (FileConverter): A FileConverter instance.
        file_name (str): The name of the file being tested.
        file_path (str): The path to the file being tested.
    """

    # Convert the file
    converter.convert_file(source_file_path=file_path, destination_folder_path=tmp_path)

    # Determine the path to the converted file
    converted_file_path = os.path.join(tmp_path, file_name)

    # Ensure files are the same
    if file_name.endswith(".ipynb"):
        comparison_result = ipynb_eq(file_path, converted_file_path)
    else:
        comparison_result = file_eq(file_path, converted_file_path)

    assert comparison_result, f"{file_name} was changed when it should not have been."


# Parameterize simple files
simple_file_params = [
    (file_name, file_path)
    for file_name, file_path in MOCK_SOLUTION_FILES.items()
    if "simple" in file_name
]


@pytest.mark.parametrize("file_name, file_path", simple_file_params)
def test_simple_removal(converter, tmp_path, file_name, file_path):
    """
    Ensures that the appropriate text is removed from simple files
    Args:
        converter (FileConverter): A FileConverter instance.
        file_name (str): The name of the file being tested.
        file_path (str): The path to the file being tested.
    """

    # Get converted file content
    converted_contents = get_converted_file_content(converter, file_path, tmp_path)

    # Ensure that "XXXX" is not present in the converted file
    assert "XXXX" not in converted_contents, f"XXXX was not removed from {file_name}"
