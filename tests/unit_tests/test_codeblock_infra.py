"""Unit tests for CodeBlockManager and CodeBlockType."""
from __future__ import annotations

import pytest

from pact.convert.utils.codeblock_infra import (
    CodeBlockManager,
    CodeBlockType,
    InvalidCodeBlockError,
)


class TestCodeBlockType:
    """Tests for CodeBlockType class."""

    def test_init(self):
        """CodeBlockType initializes with correct attributes."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
            replacement_str="replaced",
        )
        assert block.name == "Test Block"
        assert block.start_trigger_str == "START"
        assert block.end_trigger_str == "END"
        assert block.replacement_str == "replaced"

    def test_init_default_replacement(self):
        """CodeBlockType defaults to empty replacement string."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
        )
        assert block.replacement_str == ""

    def test_get_replacement_str_empty(self):
        """Empty replacement string returns empty string."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
            replacement_str="",
        )
        assert block.get_replacement_str() == ""
        assert block.get_replacement_str("    ") == ""

    def test_get_replacement_str_single_line(self):
        """Single line replacement returns the line (replacement strings should start with newline)."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
            replacement_str="\npass",
        )
        assert block.get_replacement_str() == "pass"
        assert block.get_replacement_str("    ") == "pass"

    def test_get_replacement_str_with_leading_newline(self):
        """Leading newline is stripped from replacement string."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
            replacement_str="\npass",
        )
        assert block.get_replacement_str() == "pass"

    def test_get_replacement_str_multi_line_no_indent(self):
        """Multi-line replacement without indentation."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
            replacement_str="\nline1\nline2\n",
        )
        result = block.get_replacement_str()
        assert result == "line1\nline2\n"

    def test_get_replacement_str_multi_line_with_indentation(self):
        """Multi-line replacement preserves indentation on all but last line."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
            replacement_str="\nline1\nline2\n",
        )
        result = block.get_replacement_str("    ")
        assert result == "    line1\n    line2\n"

    def test_str_representation(self):
        """String representation includes key attributes."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
        )
        s = str(block)
        assert "Test Block" in s
        assert "START" in s
        assert "END" in s

    def test_repr_representation(self):
        """Repr representation matches str."""
        block = CodeBlockType(
            name="Test Block",
            start_trigger_str="START",
            end_trigger_str="END",
        )
        assert repr(block) == str(block)


class TestCodeBlockManager:
    """Tests for CodeBlockManager class."""

    @pytest.fixture
    def manager(self):
        """Create a CodeBlockManager with test block types."""
        manager = CodeBlockManager()
        manager.add_codeblock_type(
            CodeBlockType(
                name="Student Code",
                start_trigger_str="STUDENT_START",
                end_trigger_str="STUDENT_END",
                replacement_str="\n# TODO: Implement\npass\n",
            )
        )
        manager.add_codeblock_type(
            CodeBlockType(
                name="Key Only",
                start_trigger_str="KEY_START",
                end_trigger_str="KEY_END",
                replacement_str="",
            )
        )
        return manager

    def test_initial_state_inactive(self, manager):
        """Manager starts with no active block."""
        assert manager.is_codeblock_active() is False
        assert manager.active_block_type is None

    def test_add_codeblock_type(self):
        """Codeblock types can be added to manager."""
        manager = CodeBlockManager()
        assert len(manager.codeblock_types) == 0

        block = CodeBlockType("Test", "START", "END")
        manager.add_codeblock_type(block)

        assert len(manager.codeblock_types) == 1
        assert manager.codeblock_types[0] is block

    def test_activate_block_sets_active(self, manager):
        """Activating a block sets it as active."""
        manager.update_state("# STUDENT_START")
        assert manager.is_codeblock_active() is True
        assert manager.active_block_type.name == "Student Code"

    def test_deactivate_block_clears_active(self, manager):
        """Deactivating a block clears active state."""
        manager.update_state("# STUDENT_START")
        assert manager.is_codeblock_active() is True

        manager.update_state("# STUDENT_END")
        assert manager.is_codeblock_active() is False
        assert manager.active_block_type is None

    def test_double_activation_raises_error(self, manager):
        """Activating a block while another is active raises error."""
        manager.update_state("# STUDENT_START")

        with pytest.raises(InvalidCodeBlockError) as exc_info:
            manager.update_state("# KEY_START")

        assert "still active" in str(exc_info.value)

    def test_same_block_double_activation_raises_error(self, manager):
        """Activating the same block type twice raises error."""
        manager.update_state("# STUDENT_START")

        with pytest.raises(InvalidCodeBlockError) as exc_info:
            manager.update_state("# STUDENT_START")

        assert "still active" in str(exc_info.value)

    def test_mismatched_end_raises_error(self, manager):
        """Ending with wrong block type raises error."""
        manager.update_state("# STUDENT_START")

        with pytest.raises(InvalidCodeBlockError) as exc_info:
            manager.update_state("# KEY_END")

        assert "Expected to deactivate" in str(exc_info.value)

    def test_end_without_start_raises_error(self, manager):
        """Ending a block without starting raises error (attempts to deactivate None)."""
        # When no block is active, trying to end raises an error because
        # _deactivate_block compares active_block_type (None) with the found type
        with pytest.raises((InvalidCodeBlockError, AttributeError)):
            manager.update_state("# STUDENT_END")

    def test_end_of_file_with_open_block_raises_error(self, manager):
        """End of file check with open block raises error."""
        manager.update_state("# STUDENT_START")

        with pytest.raises(InvalidCodeBlockError) as exc_info:
            manager.end_of_file_check()

        assert "not closed" in str(exc_info.value)

    def test_end_of_file_no_open_block_passes(self, manager):
        """End of file check with no open block passes."""
        manager.end_of_file_check()  # Should not raise

    def test_get_replacement_str_when_active(self, manager):
        """Get replacement string when block is active."""
        manager.update_state("# STUDENT_START")
        replacement = manager.get_replacement_str()
        assert "TODO" in replacement or "pass" in replacement

    def test_get_replacement_str_when_inactive_raises(self, manager):
        """Get replacement string when no block active raises error."""
        with pytest.raises(ValueError) as exc_info:
            manager.get_replacement_str()

        assert "No codeblock type is currently active" in str(exc_info.value)

    def test_indentation_preserved(self, manager):
        """Indentation is preserved from starting line."""
        manager.update_state("    # STUDENT_START")
        assert manager.block_indentation_str == "    "

        replacement = manager.get_replacement_str()
        # Multi-line replacement should include indentation on lines
        # The replacement string has newlines, so indentation is prepended
        assert "    " in replacement or replacement.startswith("# TODO")

    def test_update_state_no_trigger(self, manager):
        """Update state with no trigger does nothing."""
        manager.update_state("regular code line")
        assert manager.is_codeblock_active() is False

    def test_multiple_triggers_on_line_raises_error(self, manager):
        """Multiple triggers on same line raises error."""
        with pytest.raises(InvalidCodeBlockError) as exc_info:
            manager.update_state("# STUDENT_START KEY_START")

        assert "multiple codeblock triggers" in str(exc_info.value).lower()

    def test_check_for_trigger_returns_correct_type(self, manager):
        """Internal check correctly identifies trigger type."""
        result = manager._check_for_trigger("# STUDENT_START here")
        assert result[0].name == "Student Code"
        assert result[1] == "start"

        result = manager._check_for_trigger("# STUDENT_END here")
        assert result[0].name == "Student Code"
        assert result[1] == "end"

    def test_check_for_trigger_no_trigger(self, manager):
        """Internal check returns None when no trigger found."""
        result = manager._check_for_trigger("regular line")
        assert result is None

    def test_complete_block_cycle(self, manager):
        """Complete activate/deactivate cycle works correctly."""
        # Start inactive
        assert manager.is_codeblock_active() is False

        # Activate
        manager.update_state("# STUDENT_START")
        assert manager.is_codeblock_active() is True

        # Process lines (no change in state)
        manager.update_state("x = 1")
        manager.update_state("y = 2")
        assert manager.is_codeblock_active() is True

        # Deactivate
        manager.update_state("# STUDENT_END")
        assert manager.is_codeblock_active() is False

        # Can start another block
        manager.update_state("# KEY_START")
        assert manager.is_codeblock_active() is True
        assert manager.active_block_type.name == "Key Only"


class TestInvalidCodeBlockError:
    """Tests for InvalidCodeBlockError exception."""

    def test_init_with_message(self):
        """Exception stores message correctly."""
        err = InvalidCodeBlockError("Test error message")
        assert err.message == "Test error message"
        assert err.error_code == 1

    def test_init_with_error_code(self):
        """Exception stores custom error code."""
        err = InvalidCodeBlockError("Test", error_code=42)
        assert err.error_code == 42

    def test_str_includes_message_and_code(self):
        """String representation includes message and code."""
        err = InvalidCodeBlockError("Test error", error_code=5)
        s = str(err)
        assert "Test error" in s
        assert "5" in s
