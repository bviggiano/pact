"""Shared pytest fixtures for PACT tests."""
from __future__ import annotations

import os
import sys

import pytest

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from pact.convert.utils.codeblock_infra import CodeBlockManager, CodeBlockType
from pact.convert.utils.file_converter import FileConverter
from pact.convert.utils.mask_infra import MaskManager, MaskType
from pact.convert.utils.prime_converter import (
    BLACK_LIST_FILE_NAME,
    OPTIONS_FILE_NAME,
    SUB_LIST_FILE_NAME,
    PrimeConverter,
)


# ============================================================================
# Codeblock Fixtures
# ============================================================================


@pytest.fixture
def student_code_block():
    """A codeblock type for student code sections."""
    return CodeBlockType(
        name="Student Code Block",
        start_trigger_str="STUDENT_CODE_START",
        end_trigger_str="STUDENT_CODE_END",
        replacement_str="\n# TODO: Implement\npass\n",
    )


@pytest.fixture
def key_only_block():
    """A codeblock type that removes content entirely (for answer keys)."""
    return CodeBlockType(
        name="Key Only",
        start_trigger_str="KEY_ONLY_START",
        end_trigger_str="KEY_ONLY_END",
        replacement_str="",
    )


@pytest.fixture
def codeblock_types(student_code_block, key_only_block):
    """List of all test codeblock types."""
    return [student_code_block, key_only_block]


@pytest.fixture
def codeblock_manager(codeblock_types):
    """A CodeBlockManager with test codeblock types registered."""
    manager = CodeBlockManager()
    for block_type in codeblock_types:
        manager.add_codeblock_type(block_type)
    return manager


# ============================================================================
# Mask Fixtures
# ============================================================================


@pytest.fixture
def assignment_mask():
    """A mask type for Python assignment statements."""
    return MaskType(
        name="Python Value Assignment Mask",
        trigger_str="MASK_ASSIGNMENT",
        start_char="=",
        mask_str="= None # TODO: Implement",
    )


@pytest.fixture
def mask_types(assignment_mask):
    """List of all test mask types."""
    return [assignment_mask]


@pytest.fixture
def mask_manager(mask_types):
    """A MaskManager with test mask types registered."""
    manager = MaskManager()
    for mask_type in mask_types:
        manager.add_mask_type(mask_type)
    return manager


# ============================================================================
# Converter Fixtures
# ============================================================================


@pytest.fixture
def file_converter(codeblock_types, mask_types):
    """A FileConverter with test codeblock and mask types."""
    return FileConverter(codeblock_types=codeblock_types, mask_types=mask_types)


@pytest.fixture
def prime_converter():
    """A fresh PrimeConverter instance."""
    return PrimeConverter()


# ============================================================================
# Mock Assignment Fixtures
# ============================================================================


@pytest.fixture
def mock_assignment_dir(tmp_path):
    """Create a mock assignment directory structure."""
    assignment_dir = tmp_path / "test_assignment"
    assignment_dir.mkdir()

    # Create main Python file with codeblock
    main_py = assignment_dir / "main.py"
    main_py.write_text(
        '''"""Main module for assignment."""


def solution_function():
    """A function students need to implement."""
    # STUDENT_CODE_START
    result = 42
    return result
    # STUDENT_CODE_END


def helper_function():
    """A helper function provided to students."""
    return "helper"
'''
    )

    # Create a file with masks
    masked_py = assignment_dir / "masked.py"
    masked_py.write_text(
        '''"""Module with masked assignments."""


def create_model():
    """Create the model."""
    model = build_complex_model(  # MASK_ASSIGNMENT
        layers=[64, 32, 16],
        activation="relu",
    )

    return model
'''
    )

    # Create an unchanged file
    utils_py = assignment_dir / "utils.py"
    utils_py.write_text(
        '''"""Utility functions provided to students."""


def utility():
    return "utility"
'''
    )

    # Create README
    readme = assignment_dir / "README.md"
    readme.write_text("# Test Assignment\n\nInstructions here.")

    return assignment_dir


@pytest.fixture
def mock_assignment_with_config(mock_assignment_dir):
    """Mock assignment with PACT configuration files."""
    # Create black_list.pact
    black_list = mock_assignment_dir / BLACK_LIST_FILE_NAME
    black_list.write_text("secret.txt\nhidden/\n")

    # Create sub_list.pact
    sub_list = mock_assignment_dir / SUB_LIST_FILE_NAME
    sub_list.write_text("main.py\nmasked.py\n")

    # Create a secret file that should be excluded
    secret = mock_assignment_dir / "secret.txt"
    secret.write_text("This is secret and should not be included")

    # Create hidden directory
    hidden_dir = mock_assignment_dir / "hidden"
    hidden_dir.mkdir()
    (hidden_dir / "answer_key.py").write_text("answers here")

    return mock_assignment_dir


@pytest.fixture
def mock_assignment_no_submission(mock_assignment_dir):
    """Mock assignment with no_submission_file option."""
    options = mock_assignment_dir / OPTIONS_FILE_NAME
    options.write_text("no_submission_file\n")
    return mock_assignment_dir


# ============================================================================
# File Content Fixtures
# ============================================================================


@pytest.fixture
def simple_codeblock_content():
    """Simple Python file content with a codeblock."""
    return '''def func():
    # STUDENT_CODE_START
    secret_implementation()
    # STUDENT_CODE_END
    return result
'''


@pytest.fixture
def simple_mask_content():
    """Simple Python file content with a mask."""
    return '''def func():
    value = compute_secret()  # MASK_ASSIGNMENT

    return value
'''


@pytest.fixture
def invalid_unclosed_codeblock_content():
    """Python file with unclosed codeblock."""
    return '''def func():
    # STUDENT_CODE_START
    code here
    # Missing END
'''


@pytest.fixture
def invalid_nested_codeblock_content():
    """Python file with nested codeblocks."""
    return '''def func():
    # STUDENT_CODE_START
    # KEY_ONLY_START
    nested
    # KEY_ONLY_END
    # STUDENT_CODE_END
'''
