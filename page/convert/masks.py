"""
masks.py

This module contains instances of the MaskType class, which is utilized to partially
mask sections of text/code within the assignment files using predefined trigger strings.

You can create custom mask instances by following the examples below.
"""

from page.convert.utils.mask_infra import (
    MaskType,
)


# ================ A few Mask Types are implemented below ================
# =====
# Python Value Assignment Mask: This mask is used to mask the values assigned
# to variables in python code. Notice that the replacement string contains
# "= None". This is to ensure that the code is syntactically correct
# when converted.

# Here we define the MaskType instance for the TODO_VALUE_ASSIGNMENT mask
PY_VALUE_ASSIGNMENT = MaskType(
    name="Python Value Assignment Mask",  # The name of the mask (only used for identification)
    trigger_str="MASK_ASSIGNMENT",  # The trigger string: this is used to identify the line that should be masked
    start_char="=",  # The character in the original line where the mask should start
    mask_str="= None # TODO: Implement",  # The string that will replace the characters in the mask on the first line
)


# =====
# Feel free to implement additional codeblocks as needed here!


# ===================== DO NOT MODIFY THE CODE BELOW =====================
# This code collects all codeblocks defined in this file for easy access
MASKTYPES = []

for item in list(globals().values()):
    if isinstance(item, MaskType):
        MASKTYPES.append(item)
