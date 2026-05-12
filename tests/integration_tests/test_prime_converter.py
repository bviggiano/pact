"""Integration tests for PrimeConverter."""
from __future__ import annotations

import os

import pytest

from pact.convert.utils.prime_converter import (
    BLACK_LIST_FILE_NAME,
    DEFAULT_BLACK_LIST,
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
        assert converter.black_list == list(DEFAULT_BLACK_LIST)
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
        assert converter.black_list == list(DEFAULT_BLACK_LIST)
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
        """Missing black_list.pact doesn't raise error; defaults remain."""
        converter = PrimeConverter()
        converter.load_black_list(str(tmp_path))  # Should not raise
        assert converter.black_list == list(DEFAULT_BLACK_LIST)

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

    def test_default_black_list_filters_without_pact_file(self, converter):
        """Default ignore patterns apply even with no black_list.pact loaded."""
        # converter fixture didn't load a black_list.pact; defaults still apply
        assert converter.conversion_filter("/path/.DS_Store") is False
        assert converter.conversion_filter("/path/__pycache__/x.pyc") is False
        assert converter.conversion_filter("/path/.ipynb_checkpoints/nb.ipynb") is False

    def test_default_black_list_merges_with_user_patterns(self, converter):
        """User patterns extend, don't replace, the defaults."""
        converter.black_list = list(DEFAULT_BLACK_LIST) + ["custom_secret"]
        # Defaults still filter
        assert converter.conversion_filter("/path/.DS_Store") is False
        assert converter.conversion_filter("/path/.ipynb_checkpoints") is False
        # User pattern also filters
        assert converter.conversion_filter("/path/custom_secret.txt") is False
        # Unrelated file still passes
        assert converter.conversion_filter("/path/main.py") is True

    def test_filters_virtual_environments(self, converter):
        """Common Python virtual environment directory names are filtered."""
        assert converter.conversion_filter("/proj/.venv") is False
        assert converter.conversion_filter("/proj/venv") is False
        assert converter.conversion_filter("/proj/env") is False
        assert converter.conversion_filter("/proj/ENV") is False
        assert converter.conversion_filter("/proj/venv/lib/site-packages/x.py") is False
        # Substring collisions are NOT filtered
        assert converter.conversion_filter("/proj/prevention.py") is True
        assert converter.conversion_filter("/proj/environment.yml") is True

    def test_filters_build_artifacts(self, converter):
        """Build / packaging artifacts are filtered."""
        assert converter.conversion_filter("/proj/build") is False
        assert converter.conversion_filter("/proj/dist") is False
        assert converter.conversion_filter("/proj/wheels") is False
        assert converter.conversion_filter("/proj/eggs") is False
        assert converter.conversion_filter("/proj/.eggs") is False
        assert converter.conversion_filter("/proj/pact.egg-info") is False
        assert converter.conversion_filter("/proj/pact.egg-info/PKG-INFO") is False
        assert converter.conversion_filter("/proj/pact.egg") is False
        assert converter.conversion_filter("/proj/MANIFEST") is False

    def test_filters_compiled_python(self, converter):
        """Compiled Python and native-extension files are filtered."""
        assert converter.conversion_filter("/proj/module.pyc") is False
        assert converter.conversion_filter("/proj/module.pyo") is False
        assert converter.conversion_filter("/proj/module.pyd") is False
        assert converter.conversion_filter("/proj/Hello$py.class") is False
        assert converter.conversion_filter("/proj/_ext.so") is False

    def test_filters_ide_metadata(self, converter):
        """IDE / editor metadata is filtered."""
        assert converter.conversion_filter("/proj/.idea") is False
        assert converter.conversion_filter("/proj/.idea/workspace.xml") is False
        assert converter.conversion_filter("/proj/.vscode") is False
        assert converter.conversion_filter("/proj/.vscode/settings.json") is False
        assert converter.conversion_filter("/proj/main.py.swp") is False

    def test_filters_linter_and_typecheck_caches(self, converter):
        """mypy/pytype/ruff cache directories and dmypy state are filtered."""
        assert converter.conversion_filter("/proj/.mypy_cache") is False
        assert converter.conversion_filter("/proj/.mypy_cache/3.10/x") is False
        assert converter.conversion_filter("/proj/.pytype") is False
        assert converter.conversion_filter("/proj/.ruff_cache") is False
        assert converter.conversion_filter("/proj/.dmypy.json") is False
        assert converter.conversion_filter("/proj/dmypy.json") is False

    def test_filters_test_and_coverage_artifacts(self, converter):
        """Test runner and coverage artifacts are filtered."""
        assert converter.conversion_filter("/proj/.pytest_cache") is False
        assert converter.conversion_filter("/proj/.tox") is False
        assert converter.conversion_filter("/proj/.nox") is False
        assert converter.conversion_filter("/proj/.coverage") is False
        assert converter.conversion_filter("/proj/.coverage.host.1234") is False
        assert converter.conversion_filter("/proj/coverage.xml") is False
        assert converter.conversion_filter("/proj/htmlcov") is False
        assert converter.conversion_filter("/proj/htmlcov/index.html") is False
        assert converter.conversion_filter("/proj/.hypothesis") is False

    def test_filters_pip_artifacts(self, converter):
        """pip log/scratch files are filtered."""
        assert converter.conversion_filter("/proj/pip-log.txt") is False
        assert converter.conversion_filter("/proj/pip-delete-this-directory.txt") is False

    def test_filters_os_noise(self, converter):
        """Windows OS metadata files are filtered."""
        assert converter.conversion_filter("/proj/Thumbs.db") is False
        assert converter.conversion_filter("/proj/desktop.ini") is False

    def test_filters_nested_ipynb_checkpoints(self, converter):
        """Nested .ipynb_checkpoints directories are filtered."""
        assert (
            converter.conversion_filter("/proj/subdir/.ipynb_checkpoints/nb-checkpoint.ipynb")
            is False
        )


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

    def test_default_ignores_without_black_list_file(self, tmp_path):
        """.DS_Store, __pycache__, and .ipynb_checkpoints are excluded with no black_list.pact."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        (assignment_dir / "main.py").write_text("code")
        (assignment_dir / ".DS_Store").write_bytes(b"\x00\x00")

        checkpoints = assignment_dir / ".ipynb_checkpoints"
        checkpoints.mkdir()
        (checkpoints / "main-checkpoint.ipynb").write_text("{}")

        pycache = assignment_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "main.cpython-39.pyc").write_bytes(b"bytecode")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        output_dir = assignment_dir / GENERATED_LOCATION_NAME / assignment_dir.name
        assert (output_dir / "main.py").exists()
        assert not (output_dir / ".DS_Store").exists()
        assert not (output_dir / ".ipynb_checkpoints").exists()
        assert not (output_dir / "__pycache__").exists()

    def test_default_ignores_with_custom_black_list(self, tmp_path):
        """Custom black_list.pact extends defaults rather than replacing them."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        (assignment_dir / "main.py").write_text("code")
        (assignment_dir / "secret.txt").write_text("secret")
        (assignment_dir / ".DS_Store").write_bytes(b"\x00\x00")

        checkpoints = assignment_dir / ".ipynb_checkpoints"
        checkpoints.mkdir()
        (checkpoints / "nb-checkpoint.ipynb").write_text("{}")

        # Custom black list mentions only secret.txt
        (assignment_dir / BLACK_LIST_FILE_NAME).write_text("secret.txt\n")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        output_dir = assignment_dir / GENERATED_LOCATION_NAME / assignment_dir.name
        assert (output_dir / "main.py").exists()
        # Custom pattern filters
        assert not (output_dir / "secret.txt").exists()
        # Defaults still filter
        assert not (output_dir / ".DS_Store").exists()
        assert not (output_dir / ".ipynb_checkpoints").exists()

    def test_expanded_default_ignores_without_black_list_file(self, tmp_path):
        """Comprehensive Python/IDE/venv/OS artifacts are excluded without black_list.pact."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        # Files that should survive
        (assignment_dir / "main.py").write_text("code")
        (assignment_dir / "environment.yml").write_text("name: test")

        # Compiled / bytecode
        (assignment_dir / "module.pyc").write_bytes(b"x")
        (assignment_dir / "module.pyo").write_bytes(b"x")
        (assignment_dir / "_ext.so").write_bytes(b"x")

        # Virtual environments. macOS' default filesystem is case-insensitive,
        # so we can't create both "env" and "ENV" side by side; the ENV regex
        # is covered by the unit-level test_filters_virtual_environments.
        for vname in (".venv", "venv", "env"):
            d = assignment_dir / vname
            d.mkdir()
            (d / "ignored.py").write_text("x")

        # Build / packaging artifacts
        for bname in ("build", "dist", "wheels", "eggs", ".eggs", "pact.egg-info"):
            d = assignment_dir / bname
            d.mkdir()
            (d / "ignored.py").write_text("x")
        (assignment_dir / "MANIFEST").write_text("x")
        (assignment_dir / "pact.egg").write_text("x")

        # IDE / editor
        for iname in (".idea", ".vscode"):
            d = assignment_dir / iname
            d.mkdir()
            (d / "ignored.txt").write_text("x")
        (assignment_dir / "main.py.swp").write_bytes(b"x")

        # Linter / typecheck caches
        for cname in (".mypy_cache", ".pytype", ".ruff_cache"):
            (assignment_dir / cname).mkdir()
        (assignment_dir / ".dmypy.json").write_text("{}")
        (assignment_dir / "dmypy.json").write_text("{}")

        # Test / coverage
        for tname in (".pytest_cache", ".tox", ".nox", "htmlcov", ".hypothesis"):
            (assignment_dir / tname).mkdir()
        (assignment_dir / ".coverage").write_text("")
        (assignment_dir / ".coverage.host.123").write_text("")
        (assignment_dir / "coverage.xml").write_text("<coverage/>")

        # pip
        (assignment_dir / "pip-log.txt").write_text("")
        (assignment_dir / "pip-delete-this-directory.txt").write_text("")

        # OS noise
        (assignment_dir / ".DS_Store").write_bytes(b"\x00")
        (assignment_dir / "Thumbs.db").write_bytes(b"\x00")
        (assignment_dir / "desktop.ini").write_text("")

        # Nested ipynb_checkpoints
        nested = assignment_dir / "src" / ".ipynb_checkpoints"
        nested.mkdir(parents=True)
        (nested / "nb-checkpoint.ipynb").write_text("{}")
        (assignment_dir / "src" / "module.py").write_text("code")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        output_dir = assignment_dir / GENERATED_LOCATION_NAME / assignment_dir.name

        # Things that should ship
        assert (output_dir / "main.py").exists()
        assert (output_dir / "environment.yml").exists()
        assert (output_dir / "src" / "module.py").exists()

        # Nothing else should
        present = {p.name for p in output_dir.iterdir()}
        survivors = {"main.py", "environment.yml", "src", "create_submission_zip.py"}
        unexpected = present - survivors
        assert not unexpected, f"Unexpected files in student version: {unexpected}"

        # Nested checkpoint dir excluded even though src/ is kept
        assert not (output_dir / "src" / ".ipynb_checkpoints").exists()

    def test_existing_redundant_black_list_still_works(self, tmp_path):
        """A black_list.pact that redundantly lists default patterns still works."""
        assignment_dir = tmp_path / "assignment"
        assignment_dir.mkdir()

        (assignment_dir / "main.py").write_text("code")
        (assignment_dir / ".DS_Store").write_bytes(b"\x00\x00")

        # Redundantly list a default pattern alongside a custom one
        (assignment_dir / BLACK_LIST_FILE_NAME).write_text(
            r"\.DS_Store$" + "\nnotes.md\n"
        )
        (assignment_dir / "notes.md").write_text("instructor notes")

        converter = PrimeConverter()
        converter.convert(str(assignment_dir))

        output_dir = assignment_dir / GENERATED_LOCATION_NAME / assignment_dir.name
        assert (output_dir / "main.py").exists()
        assert not (output_dir / ".DS_Store").exists()
        assert not (output_dir / "notes.md").exists()

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
