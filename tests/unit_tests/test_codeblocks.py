"""Unit tests for built-in codeblock instances in pact.convert.codeblocks."""
from __future__ import annotations

import json

from pact.convert.codeblocks import (
    CODEBLOCK_TYPES,
    IPYNB_ANSWER,
    KEY_ONLY,
    STUDENT_CODE,
)
from pact.convert.masks import MASKTYPES
from pact.convert.utils.file_converter import FileConverter


class TestBuiltinCodeblockRegistry:
    """The built-in codeblock instances are exported and registered."""

    def test_ipynb_answer_registered(self):
        assert IPYNB_ANSWER in CODEBLOCK_TYPES

    def test_all_builtins_registered(self):
        for block in (STUDENT_CODE, KEY_ONLY, IPYNB_ANSWER):
            assert block in CODEBLOCK_TYPES

    def test_ipynb_answer_triggers(self):
        assert IPYNB_ANSWER.start_trigger_str == "IPYNB_ANSWER_START"
        assert IPYNB_ANSWER.end_trigger_str == "IPYNB_ANSWER_END"
        assert "YOUR ANSWER HERE" in IPYNB_ANSWER.replacement_str


class TestIpynbAnswerConversion:
    """End-to-end: IPYNB_ANSWER wraps instructor text in a markdown cell."""

    def _converter(self):
        return FileConverter(
            codeblock_types=CODEBLOCK_TYPES, mask_types=MASKTYPES
        )

    def _notebook(self, source):
        return {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": source,
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }

    def test_ipynb_answer_replaces_instructor_text(self, tmp_path):
        source = (
            "**Q1.** Why is X important?\n"
            "\n"
            "IPYNB_ANSWER_START\n"
            "Because X is the foundation of Y and unlocks Z.\n"
            "IPYNB_ANSWER_END\n"
        )
        nb_path = tmp_path / "notebook.ipynb"
        nb_path.write_text(json.dumps(self._notebook(source)))

        out_dir = tmp_path / "out"
        self._converter().convert_file(str(nb_path), str(out_dir))

        converted = json.loads((out_dir / "notebook.ipynb").read_text())
        cell_source = "".join(converted["cells"][0]["source"])

        # The instructor text and trigger lines are gone
        assert "Because X is the foundation" not in cell_source
        assert "IPYNB_ANSWER_START" not in cell_source
        assert "IPYNB_ANSWER_END" not in cell_source
        # The placeholder is present
        assert "YOUR ANSWER HERE" in cell_source
        # The question prompt is preserved
        assert "Why is X important?" in cell_source
