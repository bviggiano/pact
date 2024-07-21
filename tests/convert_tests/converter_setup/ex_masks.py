"""
ex_masks.py

This module contains definitions of MaskType instances used in convert tests.
"""

from pact.convert.utils.mask_infra import (
    MaskType,
)

PY_VALUE_ASSIGNMENT = MaskType(
    name="Python Value Assignment Mask",
    trigger_str="MASK_ASSIGNMENT",
    start_char="=",
    mask_str="= None # TODO: Implement",
)

MASKTYPES = []

for item in list(globals().values()):
    if isinstance(item, MaskType):
        MASKTYPES.append(item)
