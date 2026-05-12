"""
validate_notebooks.py

Executes every Jupyter notebook under a target path and fails (exit code 1)
if any notebook raises during execution.
"""

from __future__ import annotations

import argparse
import logging
import sys

from pact.validate.utils.notebook_validator import (
    DEFAULT_CELL_TIMEOUT_SEC,
    NotebookValidator,
)

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Execute every notebook under the given path and fail if any "
            "raises. Skips STUDENT_VERSION/ output by default."
        )
    )
    parser.add_argument(
        "path",
        type=str,
        help="A .ipynb file or directory to scan recursively.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_CELL_TIMEOUT_SEC,
        help=f"Per-cell timeout in seconds (default: {DEFAULT_CELL_TIMEOUT_SEC}).",
    )
    parser.add_argument(
        "--kernel",
        type=str,
        default="python3",
        help="Jupyter kernel name (default: python3).",
    )
    parser.add_argument(
        "--include-student-versions",
        action="store_true",
        help="Also validate notebooks inside STUDENT_VERSION/ directories.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    validator = NotebookValidator(
        cell_timeout_sec=args.timeout,
        kernel_name=args.kernel,
        include_student_versions=args.include_student_versions,
    )
    report = validator.validate(args.path)

    if not report.results:
        print(f"No notebooks found under: {args.path}")
        return 0

    print(f"\nValidated {len(report.results)} notebook(s):")
    for r in report.results:
        marker = "OK  " if r.ok else "FAIL"
        print(f"  [{marker}] {r.path}")

    if report.failures:
        print(f"\n{len(report.failures)} notebook(s) failed:")
        for r in report.failures:
            print(f"\n--- {r.path} ---")
            print(r.error)
        return 1

    print("\nAll notebooks executed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
