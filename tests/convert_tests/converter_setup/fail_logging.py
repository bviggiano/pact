import os
import shutil

failed_test_output_dir = "tests/failed_test_output"


def log_failed_test(
    test_name: str, source_file_path: str, tmp_dir, additional_messages=""
):
    """
    Logs the failed test to a file in the failed_test_output directory.

    Returns an error message that can be used in the test output.

    Args:
        test_name (str): The name of the test that failed.
        source_file_path (str): The path to the source file that caused the test to fail.
        tmp_dir (str): The directory where the converted file is
        additional_message (List[str] or str): Additional messages to include in the error message.

    Returns:
        str: The error message that can be used in the test output.
    """

    # Create the directory if it does not exist
    os.makedirs(failed_test_output_dir, exist_ok=True)

    # Get the file name
    file_name = os.path.basename(source_file_path)

    # Get the file name without the extension
    no_ext_name = os.path.splitext(file_name)[0]

    # Create the file path to the converted file
    converted_file_path = os.path.join(tmp_dir, file_name)

    # Create a folder to store the failed test output
    failed_test_folder = os.path.join(
        failed_test_output_dir, "fail_" + test_name + "_" + no_ext_name
    )

    # Create the folder if it does not exist
    os.makedirs(failed_test_folder, exist_ok=True)

    # Copy the source file to the failed test folder
    source_file_destination = os.path.join(failed_test_folder, "source_" + file_name)
    shutil.copy(source_file_path, source_file_destination)

    # Copy the converted file to the failed test folder
    converted_file_destination = os.path.join(
        failed_test_folder, "converted_" + file_name
    )
    shutil.copy(converted_file_path, converted_file_destination)

    # Create the additional message string
    if isinstance(additional_messages, str):
        add_string = additional_messages
    if isinstance(additional_messages, list):
        add_string = "\n-".join(additional_messages)
    add_string = "-" + add_string

    # Create fail message file
    with open(os.path.join(failed_test_folder, "fail_message.txt"), "w") as file:
        file.write(f"Test {test_name} fail message(s):" + f"\n{add_string}")

    # Return the error message
    return f"Test {test_name} failed. See: {failed_test_folder}" f"\n{add_string}"
