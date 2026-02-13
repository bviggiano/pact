"""Unit tests for utility functions in codeblock_infra and mask_infra."""
from __future__ import annotations

import pytest

from pact.convert.utils.codeblock_infra import get_line_indentation
from pact.convert.utils.mask_infra import line_is_only_whitespace


class TestGetLineIndentation:
    """Tests for get_line_indentation function."""

    def test_no_indentation(self):
        """Line with no leading whitespace returns empty string."""
        assert get_line_indentation("hello world") == ""

    def test_spaces_indentation(self):
        """Line with leading spaces returns those spaces."""
        assert get_line_indentation("    hello world") == "    "

    def test_tabs_indentation(self):
        """Line with leading tabs returns those tabs."""
        assert get_line_indentation("\thello world") == "\t"

    def test_mixed_indentation(self):
        """Line with mixed tabs and spaces returns all leading whitespace."""
        assert get_line_indentation("\t  hello world") == "\t  "

    def test_spaces_then_tabs(self):
        """Line with spaces then tabs returns all leading whitespace."""
        assert get_line_indentation("  \thello") == "  \t"

    def test_empty_line(self):
        """Empty string returns empty string."""
        assert get_line_indentation("") == ""

    def test_all_whitespace_spaces(self):
        """Line that is only spaces returns the entire line."""
        line = "    "
        assert get_line_indentation(line) == line

    def test_all_whitespace_tabs(self):
        """Line that is only tabs returns the entire line."""
        line = "\t\t"
        assert get_line_indentation(line) == line

    def test_all_whitespace_mixed(self):
        """Line that is only mixed whitespace returns the entire line."""
        line = "\t  \t "
        assert get_line_indentation(line) == line

    def test_newline_only(self):
        """Line that is only newline returns empty string (newline is not indentation)."""
        assert get_line_indentation("\n") == ""

    def test_indentation_with_newline(self):
        """Indentation is captured even if line ends with newline."""
        assert get_line_indentation("    code\n") == "    "


class TestLineIsOnlyWhitespace:
    """Tests for line_is_only_whitespace function."""

    def test_empty_string(self):
        """Empty string is considered whitespace only."""
        assert line_is_only_whitespace("") is True

    def test_spaces_only(self):
        """String of only spaces is whitespace only."""
        assert line_is_only_whitespace("    ") is True

    def test_tabs_only(self):
        """String of only tabs is whitespace only."""
        assert line_is_only_whitespace("\t\t") is True

    def test_newline_only(self):
        """String of only newlines is whitespace only."""
        assert line_is_only_whitespace("\n") is True

    def test_mixed_whitespace(self):
        """String of mixed whitespace characters is whitespace only."""
        assert line_is_only_whitespace(" \t \n ") is True

    def test_has_content(self):
        """String with non-whitespace content returns False."""
        assert line_is_only_whitespace("hello") is False

    def test_whitespace_with_content(self):
        """String with whitespace and content returns False."""
        assert line_is_only_whitespace("  hello  ") is False

    def test_content_with_leading_whitespace(self):
        """String with leading whitespace and content returns False."""
        assert line_is_only_whitespace("    code") is False

    def test_content_with_trailing_whitespace(self):
        """String with content and trailing whitespace returns False."""
        assert line_is_only_whitespace("code    ") is False
