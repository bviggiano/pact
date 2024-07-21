"""
ex_codeblocks.py

This file defines codeblocks that are used in the tests.
"""

from pact.convert.utils.codeblock_infra import (
    CodeBlockType,
)

student_code_replacement_str = """
# ==================== YOUR CODE HERE ====================

# TODO: Implement
pass

# ==================== YOUR CODE HERE ====================
"""

STUDENT_CODE = CodeBlockType(
    name="Student Code Block",
    start_trigger_str="STUDENT_CODE_START",
    end_trigger_str="STUDENT_CODE_END",
    replacement_str=student_code_replacement_str,
)

KEY_ONLY = CodeBlockType(
    name="Key Only",
    start_trigger_str="KEY_ONLY_START",
    end_trigger_str="KEY_ONLY_END",
    replacement_str="",
)

CODEBLOCK_TYPES = []

for item in list(globals().values()):
    if isinstance(item, CodeBlockType):
        CODEBLOCK_TYPES.append(item)
