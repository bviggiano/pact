"""
masker.py

This file contains the Masker class, which is used to partially mask sections
of code in a file.
"""


class InvalidMaskError(Exception):
    """
    Exception raised when masks are not properly defined.
    """

    def __init__(self, message: str = "", error_code: int = 1):
        """
        Creates a new InvalidMaskError.

        Args:
            message (str): The error message to display.
            error_code (int): The error code to exit with.
        """
        self.message = message
        self.error_code = error_code
        super().__init__(f"{self.message}, Error code: {self.error_code}")


class MaskManager:
    """
    Masks sections of code in a file.
    """

    def __init__(self):
        """
        Creates a new MaskManager.
        """

        # Store the current mask type
        self.active_mask_type = None

        # Stores the active block type's indentation level
        self.block_indentation_str = ""

        # Store all codeblock types
        self.mask_types = []

    def add_mask_type(self, mask_type: "MaskType") -> None:
        """
        Adds a mask to the manager.

        Args:
            mask_type (MaskType): The mask to add.
        """
        self.mask_types.append(mask_type)

    def get_masked_str(self, line: str) -> str:
        """
        Returns the mask string of the active mask type if the line contains the
        trigger string. If no active mask type is found, return an empty string.

        Args:
            line (str): The line containing the trigger string.

        Returns:
            str: The mask string of the active mask type.
        """

        # If no active mask type is found, raise an error
        if self.active_mask_type is None:
            raise ValueError("No mask type is currently active.")

        # Find the index of the start character
        start_char_index = line.find(self.active_mask_type.start_char)

        # If the start character is not found, raise an error
        if start_char_index == -1:
            raise InvalidMaskError(
                f"Start character '{self.active_mask_type.start_char}' not found in masked line: {line}"
                f"The first line of a mask must contain the mask type's start character."
            )

        # Return the mask string
        return line[:start_char_index] + self.active_mask_type.mask_str + "\n\n"

    def _activate_mask(self, mask_type: "MaskType") -> None:
        """
        Activates a mask type.

        Args:
            mask_type (MaskType): The mask type to activate.
        """

        # Ensure no other mask is active
        if self.active_mask_type is not None:
            raise InvalidMaskError(
                f"Tried to activate a second mask type '{mask_type.name}' while '{self.active_mask_type.name}' is still active."
                f"Ensure that newlines are present between mask use."
            )

        self.active_mask_type = mask_type

    def _deactivate_mask(self) -> None:
        """
        Deactivates the active mask type.
        """
        self.active_mask_type = None

    def _check_for_trigger(self, current_line: str):
        """
        Checks if the current line contains the trigger string for any of the mask types.
        If a trigger string is found, the corresponding mask type is activated.

        Args:
            current_line (str): The current line to check for trigger strings.

        Returns:
            bool: True if a trigger string is found, False otherwise.
        """
        # Check if the current line contains the trigger string
        found_mask_type = None

        # For each codeblock type
        for mask_type in self.mask_types:
            if mask_type.trigger_str in current_line:
                if found_mask_type is not None:
                    raise InvalidMaskError(
                        f"Multiple mask triggers found in line: {current_line}"
                    )

                # Set the return value
                found_mask_type = mask_type

        # Return the found mask type
        return found_mask_type

    def update_state(self, current_line: str):
        """
        Updates the start of the codeblock manager based on the current line.

        Args:
            current_line (str): The current line of the file.
        """

        # If this line is only whitespace, we deactivate the mask
        if line_is_only_whitespace(current_line):
            self._deactivate_mask()

        else:
            # Check if the current line contains the mask trigger
            mask_trigger = self._check_for_trigger(current_line)

            # If this line contains a mask trigger, we activate the mask
            if mask_trigger is not None:
                self._activate_mask(mask_trigger)

    def is_mask_active(self):
        """
        Returns whether or not a mask is currently active.

        Returns:
            bool: True if a mask is active, False otherwise.
        """
        return self.active_mask_type is not None


def line_is_only_whitespace(line: str) -> bool:
    """
    Returns True if the line is only whitespace, False otherwise.

    Args:
        line (str): The line to check.

    Returns:
        bool: True if the line is only whitespace, False otherwise.
    """
    return line.strip() == ""


class MaskType:
    """
    Used to define types of partial masks that can be applied to lines
    of code in a file.
    """

    def __init__(self, name: str, trigger_str: str, start_char: str, mask_str: str):
        """
        Creates a new MaskType. The mask will be applied starting at lines that
        contain the trigger string, masking all characters starting at the start_char
        index and replacing them with the mask string.

        Args:
            name (str): The name of the mask type.
            trigger_str (str): The string that triggers the mask.
            start_char (str): The character in the original line where the mask should start.
                NOTE: This character will also be replaced by the mask string.
            mask_str (str): The string that will replace the characters in the mask.
        """

        self.name = name
        self.trigger_str = trigger_str
        self.start_char = start_char
        self.mask_str = mask_str
