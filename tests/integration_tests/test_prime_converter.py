"""Integration tests for PrimeConverter."""
from __future__ import annotations

import os

import pytest

from pact.convert.utils.prime_converter import (
    BLACK_LIST_FILE_NAME,
    GENERATED_LOCATION_NAME,
    OPTIONS_FILE_NAME,
    SUB_LIST_FILE_NAME,
    PrimeConverter,
)


class TestPrimeConverterInit:
    """Tests for PrimeConverter initialization."""

    def test_init(self):
        """PrimeConverter initializes with correct defaults."""
        converter = PrimeConverter()
        assert converter.file_converter is not None
        assert converter.master_generation_location is None
        assert converter.black_list == []
        assert converter.sub_list == []
        assert converter.options == []

    def test_reset(self):
        """Reset clears all state."""
        converter = PrimeConverter()
        converter.master_generation_location = "/some/path"
        converter.black_list = ["pattern"]
        converter.sub_list = ["file.py"]
        converter.options = ["option"]

        converter.reset()

        assert converter.master_generation_location is None
        assert converter.black_list == []
        assert converter.sub_list == []
        assert converter.options == []


class TestPrimeConverterLoadConfig:
    """Tests for loading configuration files."""

    def test_load_black_list(self, tmp_path):
        """Black list is loaded from file."""
        # Create black_list.pact
        black_list_file = tmp_path / BLACK_LIST_FILE_NAME
        black_list_file.write_text("*.pyc\n__pycache__\nsecret.txt\n")

        converter = PrimeConverter()
        converter.load_black_list(str(tmp_path))

        assert "*.pyc" in converter.black_list
        assert "__pycache__" in converter.black_list
        assert "secret.txt" in converter.black_list

    def test_load_black_list_missing_file(self, tmp_path):
        """Missing black_list.pact doesn't raise error."""
        converter = PrimeConverter()
        converter.load_black_list(str(tmp_path))  # Should not raise
        assert converter.black_list == []

    def test_load_sub_list(self, tmp_path):
        """Sub list is loaded from file."""
        # Create sub_list.pact
        sub_list_file = tmp_path / SUB_LIST_FILE_NAME
        sub_list_file.write_text("main.py\nhelpers.py\n")

        converter = PrimeConverter()
        converter.load_sub_list(str(tmp_path))

        assert "main.py" in converter.sub_list
        assert "helpers.py" in converter.sub_list

    def test_load_sub_list_missing_file(self, tmp_path):
        """Missing sub_list.pact doesn't raise error."""
        converter = PrimeConverter()
        converter.load_sub_list(str(tmp_path))  # Should not raise
        assert converter.sub_list == []

    def test_load_options(self, tmp_path):
        """Options are loaded from file."""
        # Create options.pact
        options_file = tmp_path / OPTIONS_FILE_NAME
        options_file.write_text("no_submission_file\n")

        converter = PrimeConverter()
        converter.load_options(str(tmp_path))

        assert "no_submission_file" in converter.options

    def test_load_options_missing_file(self, tmp_path):
        """Missing options.pact doesn't raise error."""
        converter = PrimeConverter()
        converter.load_options(str(tmp_path))  # Should not raise
        assert converter.options == []


class TestConversionFilter:
    """Tests for conversion_filter method."""

    @pytest.fixture
    def converter(self, tmp_path):
        """Create a converter with generation location set."""
        converter = PrimeConverter()
        converter.master_generation_location = str(tmp_path / GENERATED_LOCATION_NAME)
        return converter

    def test_filters_generated_location(self, converter):
        """Generated location is filtered out."""
        assert converter.conversion_filter(converter.master_generation_location) is False

    def test_filters_pycache(self, converter):
        """__pycache__ directories are filtered."""
        assert converter.conversion_filter("/path/to/__pycache__") is False
        assert converter.conversion_filter("/path/__pycache__/file.py") is False

    def test_filters_pyc_files(self, converter):
        """*.pyc files are filtered."""
        assert converter.conversion_filter("/path/to/module.pyc") is False

    def test_filters_ds_store(self, converter):
        """.DS_Store files are filtered."""
        assert converter.conversion_filter("/path/.DS_Store") is False
        assert converter.conversion_filter("/path/to/.DS_Store") is False

    def test_filters_pact_files(self, converter):
        """PACT special files are filtered."""
        assert converter.conversion_filter(f"/path/{BLACK_LIST_FILE_NAME}") is False
        assert converter.conversion_filter(f"/path/{SUB_LIST_FILE_NAME}") is False
        assert converter.conversion_filter(f"/path/{OPTIONS_FILE_NAME}") is False

    def test_filters_black_list_simple(self, converter):
        """Simple black list patterns filter files."""
        converter.black_list = ["secret.txt"]
        assert converter.conversion_filter("/path/secret.txt") is False
        assert converter.conversion_filter("/path/to/secret.txt") is False

    def test_filters_black_list_regex(self, converter):
        """Regex black list patterns filter files."""
        converter.black_list = [r".*\.secret$", r"hidden_.*"]
        assert converter.conversion_filter("/path/file.secret") is False
        assert converter.conversion_filter("/path/hidden_data") is False
        assert converter.conversion_filter("/path/data.txt") is True

    def test_allows_regular_files(self, converter):
        """Regular files pass the filter."""
        assert converter.conversion_filter("/path/to/main.py") is True
        assert converter.conversion_filter("/path/to/README.md") is True
        assert converter.conversion_filter("/path/to/data.json") is True


class TestPrimeConverterConvert:
    """Integration tests for the convert method."""

    @pytest.fixture
    def simple_assignment(self, tmp_path):
        """Create a simple assignment directory structure."""
        assignment_dir = tmp_path / "test_assignment"
        assignment_dir.mkdir()

        # Create a simple Python file with codeblock
        (assignment_dir / "main.py").write_text(
            """def hello():
    # STUDENT_CODE_START
    return "Hello, World!"
    # STUDENT_CODE_END
"""
        )

        # Create an unchanged file
        (assignment_dir / "utils.py").write_text(
            """def helper():
    return 42
"""
        )

        return assignment_dir

    def test_converts_single_file(self, tmp_path):
        """Single file can be converted."""
        # Create a simple file
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """# STUDENT_CODE_START
x = 1
# STUDENT_CODE_END
"""
        )

        converter = PrimeConverter()
        converter.convert(str(test_file))

        # Check output exists
        output_dir = tmp_path / GENERATED_LOCATION_NAME
        assert output_dir.exists()

        # File should be converted
        converted_file = output_dir / "test.py"
        assert converted_file.exists()

        content = converted_file.read_text()
        assert "STUDENT_CODE_START" not in content
        assert "STUDENT_CODE_END" not in content

    def test_converts_directory_recursively(self, simple_assignment):
        """Directory with files is converted recursively."""
        converter = PrimeConverter()
        converter.convert(str(simple_assignment))

        # Check output directory structure
        output_dir = simple_assignment / GENERATED_LOCATION_NAME / simple_assignment.name
        assert output_dir.exists()

        # Both files should exist
        assert (output_dir / "main.py").exists()
        assert (output_dir / "utils.py").exists()

        # Check main.py was converted
        content = (output_dir / "main.py").read_text()
        assert "STUDENT_CODE_START" not in content

        # Check utils.py is unchanged
        utils_content = (output_dir / "utils.py").read_text()
        assert "return 42" in utils_content

    def test_creates_student_version_folder(self, simple_assignment):
        """STUDENT_VERSION folder is created."""
        converter = PrimeConverter()
        converter.convert(str(simple_assignment))

        student_version = simple_assignment / GENERATED_LOCATION_NAME
        assert student_version.exists()
        assert student_version.is_dir()

    def test_cleans_existing_student_version(self, simple_assignment):
        """Existing STUDENT_VERSION folder is cleaned before conversion."""
        # Create existing STUDENT_VERSION with old content
        old_version = simple_assignment / GENERATED_LOCATION_NAME
        old_version.mkdir()
        old_file = old_version / "old_file.txt"
        old_file.write_text("old content")

        converter = PrimeConverter()
        converter.convert(str(simple_assignment))

        # Old file should be gone
        assert not old_file.exists()

    def test_respects_black_list(self, tmp_path):
        """Black list patterns are respected."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        # Create files
        (assignment_dir / "main.py").write_text("code")
        (assignment_dir / "secret.txt").write_text("secret data")

        # Create black list
        (assignment_dir / BLACK_LIST_FILE_NAME).write_text("secret.txt\n")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        output_dir = assignment_dir / GENERATED_LOCATION_NAME / assignment_dir.name
        assert (output_dir / "main.py").exists()
        assert not (output_dir / "secret.txt").exists()

    def test_skips_pycache(self, tmp_path):
        """__pycache__ directories are skipped."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        # Create files
        (assignment_dir / "main.py").write_text("code")

        # Create __pycache__
        pycache = assignment_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "main.cpython-39.pyc").write_bytes(b"bytecode")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        output_dir = assignment_dir / GENERATED_LOCATION_NAME / assignment_dir.name
        assert (output_dir / "main.py").exists()
        assert not (output_dir / "__pycache__").exists()

    def test_creates_zip_for_directory(self, simple_assignment):
        """Zip file is created for directory conversion."""
        converter = PrimeConverter()
        converter.convert(str(simple_assignment))

        zip_file = simple_assignment / GENERATED_LOCATION_NAME / f"{simple_assignment.name}.zip"
        assert zip_file.exists()

    def test_creates_submission_file(self, simple_assignment):
        """Submission file is created by default."""
        converter = PrimeConverter()
        converter.convert(str(simple_assignment))

        output_dir = simple_assignment / GENERATED_LOCATION_NAME / simple_assignment.name
        submission_file = output_dir / "create_submission_zip.py"
        assert submission_file.exists()

    def test_no_submission_file_option(self, tmp_path):
        """no_submission_file option prevents submission file creation."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        (assignment_dir / "main.py").write_text("code")
        (assignment_dir / OPTIONS_FILE_NAME).write_text("no_submission_file\n")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        output_dir = assignment_dir / GENERATED_LOCATION_NAME / assignment_dir.name
        submission_file = output_dir / "create_submission_zip.py"
        assert not submission_file.exists()

    def test_loads_sub_list(self, tmp_path):
        """Sub list is loaded and used."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        (assignment_dir / "main.py").write_text("code")
        (assignment_dir / SUB_LIST_FILE_NAME).write_text("main.py\n")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        assert "main.py" in converter.sub_list

    def test_nested_directories(self, tmp_path):
        """Nested directory structure is preserved."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        # Create nested structure
        subdir = assignment_dir / "src"
        subdir.mkdir()
        (subdir / "module.py").write_text("code")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        output_dir = assignment_dir / GENERATED_LOCATION_NAME / assignment_dir.name
        assert (output_dir / "src" / "module.py").exists()


class TestPrepareGenerationLocation:
    """Tests for _prepare_generation_location method."""

    def test_file_generation_location(self, tmp_path):
        """Generation location for file is in same directory."""
        test_file = tmp_path / "test.py"
        test_file.write_text("code")

        converter = PrimeConverter()
        location = converter._prepare_generation_location(str(test_file))

        expected = tmp_path / GENERATED_LOCATION_NAME
        assert location == str(expected)
        assert expected.exists()

    def test_directory_generation_location(self, tmp_path):
        """Generation location for directory is inside directory."""
        test_dir = tmp_path / "assignment"
        test_dir.mkdir()

        converter = PrimeConverter()
        location = converter._prepare_generation_location(str(test_dir))

        expected = test_dir / GENERATED_LOCATION_NAME
        assert location == str(expected)
        assert expected.exists()

    def test_nonexistent_path_raises(self, tmp_path):
        """Non-existent path raises ValueError."""
        converter = PrimeConverter()

        with pytest.raises(ValueError) as exc_info:
            converter._prepare_generation_location(str(tmp_path / "nonexistent"))

        assert "does not exist" in str(exc_info.value)
