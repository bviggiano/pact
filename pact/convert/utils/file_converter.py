"""
file_converter.py
"""

import os
import json
from typing import List
import shutil
from copy import deepcopy
from pact.convert.utils.codeblock_infra import CodeBlockManager, CodeBlockType
from pact.convert.utils.mask_infra import MaskManager, MaskType
from pact.convert.codeblocks import CODEBLOCK_TYPES
from pact.convert.masks import MASKTYPES


IPYNB_CELL_EXCLUDE = "ANSWER_KEY_CELL"
"""
IPYNB_CELL_EXCLUDE: If this string is found in a cell of an ipynb file, the entire
cell of the ipynb will be excluded in the student version of the file.
"""


class FileConverter:
    """
    Converts solution versions of assignment files into student versions.
    """

    def __init__(
        self,
        codeblock_types: List[CodeBlockType] = CODEBLOCK_TYPES,
        mask_types: List[MaskType] = MASKTYPES,
    ):
        """
        Creates a new FileConverter.

        Args:
            codeblock_types (List[CodeBlockType], optional): A list of codeblock
                types to use in the converter. Defaults to CODEBLOCK_TYPES as
                defined in the codeblocks module.
            mask_types (List[MaskType], optional): A list of mask types to use in
                the converter. Defaults to MASKTYPES.
        """

        # Create codeblock manager
        self.codeblock_manager = CodeBlockManager()

        # Add codeblock types to the manager
        for codeblock_type in codeblock_types:
            self.codeblock_manager.add_codeblock_type(codeblock_type)

        # Create mask manager
        self.mask_manager = MaskManager()

        # Add mask types to the manager
        for mask_type in mask_types:
            self.mask_manager.add_mask_type(mask_type)

    def convert_file(self, source_file_path: str, destination_folder_path: str) -> str:
        """
        Converts a solution version of an assignment file into a student version
        of the file.

        Args:
            source_file_path (str): The path to the file to convert.
            destination_folder_path (str): The path to the folder where the
                converted file should be saved.

        Returns:
            str: The converted file as a string.
        """

        # Create the destination folder if it does not exist
        os.makedirs(destination_folder_path, exist_ok=True)

        # Collect the file extension
        _, ext = os.path.splitext(source_file_path)

        # If this is an ipynb file, we need to handle it differently
        contents = None
        if ext == ".ipynb":
            contents = self._convert_ipynb_file(source_file_path)
        # Otherwise, we can convert the file as normal
        elif ext in [".png", ".jpg", ".jpeg", ".gif", ".tiff"]:
            # Copy the image file
            shutil.copyfile(
                source_file_path,
                os.path.join(
                    destination_folder_path, os.path.basename(source_file_path)
                ),
            )
            return
        else:

            # Read in the file as a string
            og_lines = None
            try:
                with open(source_file_path, "r") as file:
                    og_lines = file.readlines()
            except UnicodeDecodeError:
                print(f"- WARNING: Could not read file: {source_file_path}. Skipping.")
                return

            # Process the text in the file
            final_lines = self._convert_source_text(og_lines)

            # Convert the lines back into a string
            contents = "".join(final_lines)

        # Save the converted file to the destination folder
        file_name = os.path.basename(source_file_path)
        destination_file_path = os.path.join(destination_folder_path, file_name)

        with open(destination_file_path, "w") as file:
            file.write(contents)

    def _convert_ipynb_file(self, file_path: str) -> str:
        """
        Converts a solution version of an ipynb file into a student version of
        the file. Returns the contents of the student version as a string.

        Args:
            file_path (str): The path to the ipynb file to convert.

        Returns:
            str: The converted file as a string.
        """

        # Read in the file as a JSON
        with open(file_path, "r") as file:
            og_json = json.load(file)

        # Determine which cells (if any) should be excluded
        cells_to_remove = [False] * len(og_json["cells"])

        # Loop through each cell in the notebook
        for cell_i, cell in enumerate(og_json["cells"]):
            # If the cell contains text
            if len(cell["source"]) > 0:
                # For each line of text in the cell
                for line_of_text in cell["source"]:
                    # Remove if the line contains the exclusion indicator
                    if IPYNB_CELL_EXCLUDE in line_of_text:
                        cells_to_remove[cell_i] = True
                        break  # No need to check the rest of the lines

        # Create a new JSON object to store the student version of the notebook
        new_json = deepcopy(og_json)

        # Remove cells that should be excluded from the new JSON
        for remove_flag, cell in zip(cells_to_remove, og_json["cells"]):
            if remove_flag:
                new_json["cells"].remove(cell)

        # Process the text in each cell as we would for a normal file
        for cell in new_json["cells"]:
            cell["source"] = self._convert_source_text(cell["source"])

        # Convert the new JSON back into a string and return
        return json.dumps(new_json)

    def _convert_source_text(self, source_text_lines: List[str]) -> List[str]:
        """
        Converts source text from a solution version of an assignment file into
        a student version of the file. Returns the converted text as a string.

        Args:
            source_text_lines (List[str]): The lines of text to convert.

        Returns:
            List[str]: The converted lines of text as a list of strings.
        """

        # Create new list to store the converted text
        new_lines = []

        # Loop through each line in the source text
        inside_code_block = False
        inside_mask = False
        for line in source_text_lines:

            # Update the status of the code block manager based on the current line
            self.codeblock_manager.update_state(line)

            # Collect the current status of the code block manager
            codeblock_active = self.codeblock_manager.is_codeblock_active()

            # Update the status of the mask manager based on the current line
            self.mask_manager.update_state(line)

            # Collect the current status of the mask manager
            mask_active = self.mask_manager.is_mask_active()

            # If both a mask and code block are active, raise an error
            if mask_active and codeblock_active:
                raise ValueError("Both a mask and code block are active.")

            # If we are starting a code block, add the replacement text
            if not inside_code_block and codeblock_active:
                new_lines.append(self.codeblock_manager.get_replacement_str())

            # If we are starting a mask, add the replacement text
            elif not inside_mask and mask_active:
                new_lines.append(self.mask_manager.get_masked_str(line))

            # If we are not in a code block, AND not in a mask: add the line to the new text
            elif (not inside_code_block and not codeblock_active) and (
                not inside_mask and not mask_active
            ):
                new_lines.append(line)

            # Update the status of the inside code block flag
            inside_code_block = codeblock_active

            # Update the status of the inside mask flag
            inside_mask = mask_active

        # Check for open code block at end of file
        self.codeblock_manager.end_of_file_check()

        # Return the new lines
        return new_lines
