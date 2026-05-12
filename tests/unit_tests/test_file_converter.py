"""Unit tests for FileConverter."""
from __future__ import annotations

import json


class TestConvertIpynbCellSourceShapes:
    """FileConverter must handle both nbformat shapes of cell.source."""

    def _build_notebook(self, source):
        """Build a minimal notebook with one code cell whose source is `source`."""
        return {
            "cells": [
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": 1,
                    "outputs": [],
                    "source": source,
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }

    def test_string_source_triggers_are_replaced(self, tmp_path, file_converter):
        """A cell whose source is a single string still gets its triggers replaced."""
        # Single-string form (the broken case from issue #2)
        source_str = (
            "def f():\n"
            "    # STUDENT_CODE_START\n"
            "    secret = 42\n"
            "    return secret\n"
            "    # STUDENT_CODE_END\n"
        )
        nb_path = tmp_path / "notebook.ipynb"
        nb_path.write_text(json.dumps(self._build_notebook(source_str)))

        out_dir = tmp_path / "out"
        file_converter.convert_file(str(nb_path), str(out_dir))

        converted = json.loads((out_dir / "notebook.ipynb").read_text())
        cell_source = "".join(converted["cells"][0]["source"])

        # Triggers are gone; replacement text is present
        assert "STUDENT_CODE_START" not in cell_source
        assert "STUDENT_CODE_END" not in cell_source
        assert "secret = 42" not in cell_source
        assert "TODO: Implement" in cell_source

    def test_list_source_still_works(self, tmp_path, file_converter):
        """Existing list-of-lines callers are unaffected by the normalization."""
        source_list = [
            "def f():\n",
            "    # STUDENT_CODE_START\n",
            "    secret = 42\n",
            "    return secret\n",
            "    # STUDENT_CODE_END\n",
        ]
        nb_path = tmp_path / "notebook.ipynb"
        nb_path.write_text(json.dumps(self._build_notebook(source_list)))

        out_dir = tmp_path / "out"
        file_converter.convert_file(str(nb_path), str(out_dir))

        converted = json.loads((out_dir / "notebook.ipynb").read_text())
        cell_source = "".join(converted["cells"][0]["source"])

        assert "STUDENT_CODE_START" not in cell_source
        assert "secret = 42" not in cell_source
        assert "TODO: Implement" in cell_source

    def test_string_source_answer_key_cell_excluded(self, tmp_path, file_converter):
        """ANSWER_KEY_CELL exclusion works on string-form sources too."""
        nb = {
            "cells": [
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": 1,
                    "outputs": [],
                    "source": "# ANSWER_KEY_CELL\nsecret_answer = 99\n",
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": 2,
                    "outputs": [],
                    "source": "keep_me = 1\n",
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        nb_path = tmp_path / "notebook.ipynb"
        nb_path.write_text(json.dumps(nb))

        out_dir = tmp_path / "out"
        file_converter.convert_file(str(nb_path), str(out_dir))

        converted = json.loads((out_dir / "notebook.ipynb").read_text())
        all_source = "".join(
            "".join(cell["source"]) for cell in converted["cells"]
        )
        assert len(converted["cells"]) == 1
        assert "secret_answer" not in all_source
        assert "keep_me = 1" in all_source
