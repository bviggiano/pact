"""Unit tests for NotebookValidator."""
from __future__ import annotations

import json
import os

import pytest

from pact.convert.utils.prime_converter import GENERATED_LOCATION_NAME
from pact.validate.utils.notebook_validator import NotebookValidator


def _write_notebook(path, code_cells: list[str]) -> None:
    """Write a minimal valid notebook with the given code cell sources."""
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": src,
            }
            for src in code_cells
        ],
        "metadata": {
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3",
                "language": "python",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    with open(path, "w") as f:
        json.dump(nb, f)


@pytest.fixture
def passing_notebook(tmp_path):
    path = tmp_path / "passing.ipynb"
    _write_notebook(str(path), ["x = 1 + 1\n", "assert x == 2\n"])
    return str(path)


@pytest.fixture
def failing_notebook(tmp_path):
    path = tmp_path / "failing.ipynb"
    _write_notebook(str(path), ["raise RuntimeError('intentional failure')\n"])
    return str(path)


class TestNotebookValidatorSingleFile:
    def test_passing_notebook_reports_ok(self, passing_notebook):
        report = NotebookValidator().validate(passing_notebook)
        assert report.ok is True
        assert len(report.results) == 1
        assert report.results[0].ok is True
        assert report.results[0].error is None

    def test_failing_notebook_reports_failure(self, failing_notebook):
        report = NotebookValidator().validate(failing_notebook)
        assert report.ok is False
        assert len(report.failures) == 1
        assert "RuntimeError" in report.failures[0].error
        assert "intentional failure" in report.failures[0].error

    def test_nonexistent_path_raises(self, tmp_path):
        with pytest.raises(ValueError, match="does not exist"):
            NotebookValidator().validate(str(tmp_path / "missing.ipynb"))

    def test_non_ipynb_file_raises(self, tmp_path):
        f = tmp_path / "not_a_notebook.py"
        f.write_text("x = 1")
        with pytest.raises(ValueError, match="Not a notebook"):
            NotebookValidator().validate(str(f))


class TestNotebookValidatorDirectory:
    def test_validates_directory_recursively(self, tmp_path, passing_notebook):
        # Add a second passing notebook in a subdir
        subdir = tmp_path / "sub"
        subdir.mkdir()
        nested = subdir / "nested.ipynb"
        _write_notebook(str(nested), ["x = 0\n"])

        report = NotebookValidator().validate(str(tmp_path))
        assert report.ok is True
        assert len(report.results) == 2

    def test_directory_with_failure_fails_overall(
        self, tmp_path, passing_notebook, failing_notebook
    ):
        report = NotebookValidator().validate(str(tmp_path))
        assert report.ok is False
        assert len(report.results) == 2
        assert len(report.failures) == 1
        assert report.failures[0].path.endswith("failing.ipynb")

    def test_skips_student_version_by_default(self, tmp_path):
        # Solution notebook at top level
        _write_notebook(str(tmp_path / "solution.ipynb"), ["x = 1\n"])
        # Broken notebook inside STUDENT_VERSION/ (should be skipped)
        student_dir = tmp_path / GENERATED_LOCATION_NAME / "assn"
        student_dir.mkdir(parents=True)
        _write_notebook(
            str(student_dir / "broken.ipynb"),
            ["raise RuntimeError('this should be skipped')\n"],
        )

        report = NotebookValidator().validate(str(tmp_path))
        assert report.ok is True
        assert len(report.results) == 1
        assert os.path.basename(report.results[0].path) == "solution.ipynb"

    def test_include_student_versions_opts_in(self, tmp_path):
        _write_notebook(str(tmp_path / "solution.ipynb"), ["x = 1\n"])
        student_dir = tmp_path / GENERATED_LOCATION_NAME / "assn"
        student_dir.mkdir(parents=True)
        _write_notebook(
            str(student_dir / "broken.ipynb"),
            ["raise RuntimeError('boom')\n"],
        )

        validator = NotebookValidator(include_student_versions=True)
        report = validator.validate(str(tmp_path))
        assert report.ok is False
        assert len(report.results) == 2

    def test_skips_ipynb_checkpoints(self, tmp_path, passing_notebook):
        checkpoints = tmp_path / ".ipynb_checkpoints"
        checkpoints.mkdir()
        _write_notebook(
            str(checkpoints / "passing-checkpoint.ipynb"),
            ["raise RuntimeError('should be skipped')\n"],
        )

        report = NotebookValidator().validate(str(tmp_path))
        assert report.ok is True
        assert len(report.results) == 1

    def test_empty_directory_returns_empty_report(self, tmp_path):
        report = NotebookValidator().validate(str(tmp_path))
        assert report.ok is True
        assert report.results == []


class TestValidateNotebooksCli:
    def test_cli_exits_zero_on_pass(self, passing_notebook):
        from pact.validate_notebooks import main

        assert main([passing_notebook]) == 0

    def test_cli_exits_nonzero_on_failure(self, failing_notebook):
        from pact.validate_notebooks import main

        assert main([failing_notebook]) == 1
