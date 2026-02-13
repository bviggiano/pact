"""Integration tests for zip functions."""
from __future__ import annotations

import os
import zipfile

import pytest

from pact.zip.zip_assignment import zip_assignment_dir
from pact.zip.zip_submission import create_submission_file


class TestZipAssignmentDir:
    """Tests for zip_assignment_dir function."""

    @pytest.fixture
    def sample_dir(self, tmp_path):
        """Create a sample directory with files."""
        dir_path = tmp_path / "sample_assignment"
        dir_path.mkdir()

        # Create some files
        (dir_path / "main.py").write_text("print('hello')")
        (dir_path / "README.md").write_text("# Sample Assignment")

        # Create nested directory
        subdir = dir_path / "utils"
        subdir.mkdir()
        (subdir / "helpers.py").write_text("def helper(): pass")

        return dir_path

    def test_creates_zip_in_parent(self, sample_dir):
        """Zip file is created in parent directory by default."""
        zip_assignment_dir(str(sample_dir))

        zip_path = sample_dir.parent / f"{sample_dir.name}.zip"
        assert zip_path.exists()

    def test_creates_zip_in_custom_output(self, sample_dir, tmp_path):
        """Zip file is created in custom output directory."""
        output_dir = tmp_path / "output"

        zip_assignment_dir(str(sample_dir), output_dir=str(output_dir))

        zip_path = output_dir / f"{sample_dir.name}.zip"
        assert zip_path.exists()

    def test_creates_output_dir_if_needed(self, sample_dir, tmp_path):
        """Output directory is created if it doesn't exist."""
        output_dir = tmp_path / "new_output_dir"
        assert not output_dir.exists()

        zip_assignment_dir(str(sample_dir), output_dir=str(output_dir))

        assert output_dir.exists()
        assert (output_dir / f"{sample_dir.name}.zip").exists()

    def test_raises_for_non_directory(self, tmp_path):
        """ValueError is raised for non-directory path."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        with pytest.raises(ValueError) as exc_info:
            zip_assignment_dir(str(file_path))

        assert "not a directory" in str(exc_info.value)

    def test_raises_for_nonexistent_path(self, tmp_path):
        """ValueError is raised for non-existent path."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(ValueError) as exc_info:
            zip_assignment_dir(str(nonexistent))

        assert "not a directory" in str(exc_info.value)

    def test_includes_all_files(self, sample_dir):
        """All files are included in the zip."""
        zip_assignment_dir(str(sample_dir))

        zip_path = sample_dir.parent / f"{sample_dir.name}.zip"

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()

        assert "main.py" in names
        assert "README.md" in names
        assert "utils/helpers.py" in names

    def test_preserves_structure(self, sample_dir):
        """Directory structure is preserved in zip."""
        zip_assignment_dir(str(sample_dir))

        zip_path = sample_dir.parent / f"{sample_dir.name}.zip"

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()

        # Check relative paths are correct
        assert any("utils/" in name for name in names)

    def test_zip_contents_readable(self, sample_dir):
        """Files in zip are readable and have correct content."""
        zip_assignment_dir(str(sample_dir))

        zip_path = sample_dir.parent / f"{sample_dir.name}.zip"

        with zipfile.ZipFile(zip_path, "r") as zf:
            content = zf.read("main.py").decode("utf-8")

        assert "print('hello')" in content


class TestCreateSubmissionFile:
    """Tests for create_submission_file function."""

    def test_creates_file_without_sub_list(self, tmp_path):
        """Submission file is created without sub_list."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        create_submission_file(str(output_dir))

        submission_file = output_dir / "create_submission_zip.py"
        assert submission_file.exists()

    def test_creates_file_with_sub_list(self, tmp_path):
        """Submission file is created with sub_list."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        sub_list = ["main.py", "helpers.py"]
        create_submission_file(str(output_dir), sub_list=sub_list)

        submission_file = output_dir / "create_submission_zip.py"
        assert submission_file.exists()

        content = submission_file.read_text()
        assert "main.py" in content
        assert "helpers.py" in content

    def test_injects_patterns_correctly(self, tmp_path):
        """Patterns are injected into template correctly."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        sub_list = ["src/*.py", "data/*.json"]
        create_submission_file(str(output_dir), sub_list=sub_list)

        submission_file = output_dir / "create_submission_zip.py"
        content = submission_file.read_text()

        # Check patterns are in the file as a list
        assert "PATTERNS_TO_INCLUDE" in content
        assert "src/*.py" in content
        assert "data/*.json" in content

    def test_file_is_python_syntax(self, tmp_path):
        """Generated file has valid Python syntax."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        create_submission_file(str(output_dir), sub_list=["file.py"])

        submission_file = output_dir / "create_submission_zip.py"
        content = submission_file.read_text()

        # Should compile without syntax error
        compile(content, str(submission_file), "exec")

    def test_empty_sub_list_keeps_default(self, tmp_path):
        """Empty sub_list or None keeps default template patterns."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        create_submission_file(str(output_dir), sub_list=None)

        submission_file = output_dir / "create_submission_zip.py"
        content = submission_file.read_text()

        # Default should have PATTERNS_TO_INCLUDE = []
        assert "PATTERNS_TO_INCLUDE = []" in content

    def test_overwrites_existing_file(self, tmp_path):
        """Existing submission file is overwritten."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        submission_file = output_dir / "create_submission_zip.py"
        submission_file.write_text("old content")

        create_submission_file(str(output_dir), sub_list=["new.py"])

        new_content = submission_file.read_text()
        assert "old content" not in new_content
        assert "new.py" in new_content
