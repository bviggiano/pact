"""
codeblocks.py

This module contains instances of the CodeBlockType class, which are utilized to
replace sections of text/code within the assignment files using predefined trigger
strings.

You can create custom codeblock instances by following the examples below.
"""

from page.convert.utils.codeblock_infra import (
    CodeBlockType,
)


# ================ A few Codeblock Types are implemented below ================

# =====
# Student Code Block: This codeblock is used to mask sections of python
# code that students must implement. Notice that the replacement string contains
# a "pass" statement. This is to ensure that the code is syntactically correct
# when converted.

# Here we define the replacement string for the TODO_STUDENT_CODE block
student_code_replacement_str = """
# ==================== YOUR CODE HERE ====================

# TODO: Implement
pass

# ==================== YOUR CODE HERE ====================
"""

# Here we define the CodeBlockType instance for the TODO_STUDENT_CODE block
STUDENT_CODE = CodeBlockType(
    name="Student Code Block",  # The name of the codeblock (only used for identification)
    start_trigger_str="STUDENT_CODE_START",  # The start trigger string: this is used to identify the start of the codeblock
    end_trigger_str="STUDENT_CODE_END",  # The end trigger string: this is used to identify the end of the codeblock
    replacement_str=student_code_replacement_str,
)


# =====
# KEY_ONLY block: This codeblock is used to hide sections of code that we don't
# want students to see without replacing.
KEY_ONLY = CodeBlockType(
    name="Key Only",
    start_trigger_str="KEY_ONLY_START",
    end_trigger_str="KEY_ONLY_END",
    replacement_str="",  # Here the replacement string is empty, so the block is only removed not replaced
)


# =====
# Feel free to implement additional codeblocks as needed here!


# ===================== DO NOT MODIFY THE CODE BELOW =====================
# This code collects all codeblocks defined in this file for easy access
CODEBLOCK_TYPES = []

for item in list(globals().values()):
    if isinstance(item, CodeBlockType):
        CODEBLOCK_TYPES.append(item)
