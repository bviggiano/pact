"""
notebook_validator.py

Executes Jupyter notebooks end-to-end to verify they run without errors.
Used to catch broken solution notebooks before student versions are generated.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

from pact.convert.utils.prime_converter import GENERATED_LOCATION_NAME

logger = logging.getLogger(__name__)

DEFAULT_CELL_TIMEOUT_SEC = 300


@dataclass
class NotebookResult:
    """The result of executing a single notebook."""

    path: str
    ok: bool
    error: Optional[str] = None


@dataclass
class ValidationReport:
    """Aggregated results across one or more notebooks."""

    results: List[NotebookResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(r.ok for r in self.results)

    @property
    def failures(self) -> List[NotebookResult]:
        return [r for r in self.results if not r.ok]


class NotebookValidator:
    """
    Validates that notebooks execute end-to-end without errors.
    """

    def __init__(
        self,
        cell_timeout_sec: int = DEFAULT_CELL_TIMEOUT_SEC,
        kernel_name: str = "python3",
        include_student_versions: bool = False,
    ):
        """
        Args:
            cell_timeout_sec: Per-cell execution timeout.
            kernel_name: Jupyter kernel to launch.
            include_student_versions: If True, also validate notebooks inside
                STUDENT_VERSION/ directories. Defaults to False because those
                notebooks intentionally contain unimplemented TODOs.
        """
        self.cell_timeout_sec = cell_timeout_sec
        self.kernel_name = kernel_name
        self.include_student_versions = include_student_versions

    def validate(self, path: str) -> ValidationReport:
        """
        Validate every notebook found at `path` (a single .ipynb file or a
        directory to walk recursively).
        """
        notebooks = self._collect_notebooks(path)
        report = ValidationReport()
        for nb_path in notebooks:
            report.results.append(self._run_notebook(nb_path))
        return report

    def _collect_notebooks(self, path: str) -> List[str]:
        if not os.path.exists(path):
            raise ValueError(f"Path does not exist: {path}")

        if os.path.isfile(path):
            if not path.endswith(".ipynb"):
                raise ValueError(f"Not a notebook file: {path}")
            return [path]

        notebooks = []
        for root, dirs, files in os.walk(path):
            if not self.include_student_versions:
                # Don't descend into generated student-version trees
                dirs[:] = [d for d in dirs if d != GENERATED_LOCATION_NAME]
            # Skip checkpoints regardless
            dirs[:] = [d for d in dirs if d != ".ipynb_checkpoints"]
            for name in files:
                if name.endswith(".ipynb"):
                    notebooks.append(os.path.join(root, name))
        notebooks.sort()
        return notebooks

    def _run_notebook(self, nb_path: str) -> NotebookResult:
        logger.info("Validating notebook: %s", nb_path)
        try:
            nb = nbformat.read(nb_path, as_version=4)
            client = NotebookClient(
                nb,
                timeout=self.cell_timeout_sec,
                kernel_name=self.kernel_name,
                resources={"metadata": {"path": os.path.dirname(nb_path) or "."}},
            )
            client.execute()
        except CellExecutionError as exc:
            return NotebookResult(path=nb_path, ok=False, error=str(exc))
        except Exception as exc:
            return NotebookResult(
                path=nb_path, ok=False, error=f"{type(exc).__name__}: {exc}"
            )
        return NotebookResult(path=nb_path, ok=True)
