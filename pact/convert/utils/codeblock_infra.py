"""
Infrastructure related to codeblocks.
"""


class InvalidCodeBlockError(Exception):
    """
    Exception raised when codeblocks are not properly defined.
    """

    def __init__(self, message: str = "", error_code: int = 1):
        """
        Creates a new InvalidCodeBlockError.

        Args:
            message (str): The error message to display.
            error_code (int): The error code to exit with.
        """
        self.message = message
        self.error_code = error_code
        super().__init__(f"{self.message}, Error code: {self.error_code}")


class CodeBlockManager:
    """
    Manages codeblocks for the conversion process.
    """

    def __init__(self):
        """
        Creates a new CodeBlockManager.
        """
        # Stores the active block type
        self.active_block_type = None

        # Stores the active block type's indentation level
        self.block_indentation_str = ""

        # Store all codeblock types
        self.codeblock_types = []

    def add_codeblock_type(self, codeblock_type: "CodeBlockType") -> None:
        """
        Adds a codeblock to the manager.

        Args:
            codeblock (CodeBlock): The codeblock to add.
        """
        self.codeblock_types.append(codeblock_type)

    def get_replacement_str(self):
        """
        Returns the replacement string of the active codeblock type. If no active
        codeblock type is found, return an empty string.

        Returns:
            str: The replacement string of the active codeblock type.
        """

        # If no active codeblock type is found, raise an error
        if self.active_block_type is None:
            raise ValueError("No codeblock type is currently active.")

        return self.active_block_type.get_replacement_str(self.block_indentation_str)

    def end_of_file_check(self):
        """
        Ensures that all codeblocks are closed before the end of the file is reached.

        Raises:
            InvalidCodeBlockError: If any codeblocks are not closed.
        """
        if self.active_block_type is not None:
            raise InvalidCodeBlockError(
                f"Codeblock '{self.active_block_type.name}' is not closed."
            )

    def _activate_block(self, codeblock_type: "CodeBlockType", starting_line: str):
        """
        Activates a codeblock of the specified type.

        Args:
            codeblock_type (CodeBlockType): The codeblock type to activate.
            starting_line (str): The line where the codeblock starts.
        """

        # Ensure that no codeblocks are currently active
        if self.active_block_type is not None:
            raise InvalidCodeBlockError(
                f"Tried to activate codeblock '{codeblock_type.name}' while '{self.active_block_type.name}' is still active.",
                f"Starting line: {starting_line}",
            )

        self.active_block_type = codeblock_type
        self.block_indentation_str = get_line_indentation(starting_line)

    def _deactivate_block(self, codeblock_type: "CodeBlockType", current_line: str):
        """
        Deactivates the currently active codeblock.

        Args:
            codeblock_type (CodeBlockType): The codeblock type to deactivate.

        Raises:
            InvalidCodeBlockError: If the codeblocks are not properly defined.
        """
        # Ensure that the trigger is of the correct codeblock type
        if self.active_block_type != codeblock_type:
            raise InvalidCodeBlockError(
                f"Expected to deactivate codeblock '{self.active_block_type.name}', but found '{codeblock_type.name}' end trigger instead."
                f"Ending line: {current_line}"
            )

        self.active_block_type = None
        self.block_indentation_str = ""

    def _check_for_trigger(self, current_line: str):
        """
        Checks if the current line contains a codeblock trigger

        Args:
            current_line (str): The current line of the file.

        Raises:
            InvalidCodeBlockError: If the codeblocks are not properly defined.

        Returns:
            Tuple[CodeBlockType, str]: The codeblock type and "start" or "end"
                to indicate which trigger was found. Returns None if no trigger
                was found.
        """

        # Check if the current line contains a codeblock trigger
        found_trigger = None

        # For each codeblock type
        for codeblock_type in self.codeblock_types:

            # Check for both the start and end triggers
            for trigger, label in [
                (codeblock_type.start_trigger_str, "start"),
                (codeblock_type.end_trigger_str, "end"),
            ]:
                if trigger in current_line:

                    # If a trigger was already found, raise an error
                    # -> A line cannot contain multiple codeblock triggers
                    if found_trigger is not None:
                        raise InvalidCodeBlockError(
                            f"Line contains multiple codeblock triggers: {current_line}"
                        )

                    # Set the return value
                    found_trigger = (codeblock_type, label)

        return found_trigger

    def update_state(self, current_line: str):
        """
        Updates the state of the codeblock manager based on the current line.

        Args:
            current_line (str): The current line of the file.
        """
        # Check if the current line contains a codeblock trigger
        codeblock_trigger = self._check_for_trigger(current_line)

        # If no trigger was found, return
        if codeblock_trigger is None:
            return

        # Determine action based on trigger type
        if codeblock_trigger[1] == "start":
            self._activate_block(
                codeblock_type=codeblock_trigger[0], starting_line=current_line
            )
        else:
            self._deactivate_block(
                codeblock_type=codeblock_trigger[0], current_line=current_line
            )

    def is_codeblock_active(self):
        """
        Returns whether or not a codeblock is currently active.

        Returns:
            bool: True if a codeblock is active, False otherwise.
        """
        return self.active_block_type is not None


def get_line_indentation(current_line: str) -> int:
    """
    Returns the leading whitespace indentation of the current line.

    Parameters:
        current_line (str): The line to determine the indentation of.

    Returns:
        indentation (str): The leading whitespace indentation of the current line.
    """
    indentation_characters = ["\t", " "]

    # If the line does not start with a valid indentation character, return empty string
    if current_line[0] not in indentation_characters:
        return ""

    # Return the leading whitespace indentation of the current line
    for i, char in enumerate(current_line):
        if char not in indentation_characters:
            return current_line[:i]


class CodeBlockType:
    """
    CodeBlockType class that represents the various types of codeblocks that
    can be utilized in the conversion process.
    """

    def __init__(
        self,
        name: str,
        start_trigger_str: str,
        end_trigger_str: str,
        replacement_str: str = "",
    ):
        """
        Creates a new CodeBlockType.

        Args:
            name (str): The name of the codeblock.
            start_trigger_str (str): The substring that when found in a line will
                indicate the start of the codeblock.
            end_trigger_str (str): The substring that when found in a line will
                indicate the end of the codeblock.
            replacement_str (str): The string that will replace the text/code
                originally enclosed by the start and end trigger strings. Defaults
                to an empty string.
        """
        self.name = name
        self.start_trigger_str = start_trigger_str
        self.end_trigger_str = end_trigger_str
        self.replacement_str = replacement_str

    def get_replacement_str(self, indentation_str: str = "") -> str:
        """
        Returns the replacement string with all lines indented by the specified
        identation level.

        Args:
            indentation_str (str): The string to use for indentation.

        Returns:
            str: The replacement string with the specified indentation level.
        """
        # Remove one leading \n character if it exists
        if self.replacement_str[0] == "\n":
            replacement_str = self.replacement_str[1:]

        # Split the replacement string into lines
        replacement_lines = replacement_str.split("\n")

        # If there is only one line, return the replacement string
        if len(replacement_lines) == 1:
            return replacement_lines[0]

        # Modify each line to include the specified indentation level (except last)
        replacement_lines[:-1] = [
            f"{indentation_str}{line}" for line in replacement_lines[:-1]
        ]

        # Join all parts back into a single string with newline characters
        return "\n".join(replacement_lines)

    def __str__(self):
        return f"CodeBlockType(name={self.name}, start_trigger_str={self.start_trigger_str}, end_trigger_str={self.end_trigger_str})"

    def __repr__(self):
        return str(self)
