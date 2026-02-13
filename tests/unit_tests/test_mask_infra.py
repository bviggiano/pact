"""Unit tests for MaskManager and MaskType."""
from __future__ import annotations

import pytest

from pact.convert.utils.mask_infra import (
    InvalidMaskError,
    MaskManager,
    MaskType,
)


class TestMaskType:
    """Tests for MaskType class."""

    def test_init(self):
        """MaskType initializes with correct attributes."""
        mask = MaskType(
            name="Assignment Mask",
            trigger_str="MASK_IT",
            start_char="=",
            mask_str="= None",
        )
        assert mask.name == "Assignment Mask"
        assert mask.trigger_str == "MASK_IT"
        assert mask.start_char == "="
        assert mask.mask_str == "= None"


class TestMaskManager:
    """Tests for MaskManager class."""

    @pytest.fixture
    def manager(self):
        """Create a MaskManager with test mask types."""
        manager = MaskManager()
        manager.add_mask_type(
            MaskType(
                name="Assignment",
                trigger_str="MASK_ASSIGN",
                start_char="=",
                mask_str="= None # TODO",
            )
        )
        manager.add_mask_type(
            MaskType(
                name="Return",
                trigger_str="MASK_RETURN",
                start_char="return",
                mask_str="return None # TODO",
            )
        )
        return manager

    def test_initial_state_inactive(self, manager):
        """Manager starts with no active mask."""
        assert manager.is_mask_active() is False
        assert manager.active_mask_type is None

    def test_add_mask_type(self):
        """Mask types can be added to manager."""
        manager = MaskManager()
        assert len(manager.mask_types) == 0

        mask = MaskType("Test", "TRIGGER", "=", "= None")
        manager.add_mask_type(mask)

        assert len(manager.mask_types) == 1
        assert manager.mask_types[0] is mask

    def test_activate_on_trigger(self, manager):
        """Mask activates when trigger string is found."""
        manager.update_state("x = 5 # MASK_ASSIGN")
        assert manager.is_mask_active() is True
        assert manager.active_mask_type.name == "Assignment"

    def test_deactivate_on_whitespace(self, manager):
        """Mask deactivates on whitespace-only line."""
        manager.update_state("x = 5 # MASK_ASSIGN")
        assert manager.is_mask_active() is True

        manager.update_state("")
        assert manager.is_mask_active() is False

    def test_deactivate_on_spaces_only(self, manager):
        """Mask deactivates on spaces-only line."""
        manager.update_state("x = 5 # MASK_ASSIGN")
        assert manager.is_mask_active() is True

        manager.update_state("    ")
        assert manager.is_mask_active() is False

    def test_deactivate_on_newline(self, manager):
        """Mask deactivates on newline-only line."""
        manager.update_state("x = 5 # MASK_ASSIGN")
        assert manager.is_mask_active() is True

        manager.update_state("\n")
        assert manager.is_mask_active() is False

    def test_stays_active_on_content(self, manager):
        """Mask stays active when line has content (even without trigger)."""
        manager.update_state("x = 5 # MASK_ASSIGN")
        assert manager.is_mask_active() is True

        manager.update_state("    continued = True")
        assert manager.is_mask_active() is True

    def test_double_activation_raises_error(self, manager):
        """Activating a mask while another is active raises error."""
        manager.update_state("x = 5 # MASK_ASSIGN")

        with pytest.raises(InvalidMaskError) as exc_info:
            manager.update_state("y = 6 # MASK_RETURN")

        assert "still active" in str(exc_info.value)

    def test_get_masked_str_replaces_after_start_char(self, manager):
        """Masked string replaces content from start char onward."""
        manager.update_state("x = 5 # MASK_ASSIGN")
        result = manager.get_masked_str("x = 5 # MASK_ASSIGN")

        assert result == "x = None # TODO\n\n"

    def test_get_masked_str_preserves_before_start_char(self, manager):
        """Masked string preserves content before start char."""
        manager.update_state("variable_name = value # MASK_ASSIGN")
        result = manager.get_masked_str("variable_name = value # MASK_ASSIGN")

        assert result.startswith("variable_name ")
        assert "= None # TODO" in result

    def test_get_masked_str_with_spaces(self, manager):
        """Masked string works with various spacing."""
        manager.update_state("self.data = compute() # MASK_ASSIGN")
        result = manager.get_masked_str("self.data = compute() # MASK_ASSIGN")

        assert "self.data " in result
        assert "= None # TODO" in result

    def test_missing_start_char_raises_error(self, manager):
        """Missing start char in masked line raises error."""
        manager.update_state("x = 5 # MASK_ASSIGN")

        with pytest.raises(InvalidMaskError) as exc_info:
            manager.get_masked_str("no equals sign here")

        assert "Start character" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_get_masked_str_when_inactive_raises(self, manager):
        """Get masked string when no mask active raises error."""
        with pytest.raises(ValueError) as exc_info:
            manager.get_masked_str("some line")

        assert "No mask type is currently active" in str(exc_info.value)

    def test_multiple_triggers_on_line_raises_error(self, manager):
        """Multiple mask triggers on same line raises error."""
        with pytest.raises(InvalidMaskError) as exc_info:
            manager.update_state("x = return # MASK_ASSIGN MASK_RETURN")

        assert "Multiple mask triggers" in str(exc_info.value)

    def test_check_for_trigger_returns_correct_type(self, manager):
        """Internal check correctly identifies mask type."""
        result = manager._check_for_trigger("# MASK_ASSIGN here")
        assert result.name == "Assignment"

        result = manager._check_for_trigger("# MASK_RETURN here")
        assert result.name == "Return"

    def test_check_for_trigger_no_trigger(self, manager):
        """Internal check returns None when no trigger found."""
        result = manager._check_for_trigger("regular line")
        assert result is None

    def test_complete_mask_cycle(self, manager):
        """Complete activate/mask/deactivate cycle works correctly."""
        # Start inactive
        assert manager.is_mask_active() is False

        # Activate
        manager.update_state("x = 5 # MASK_ASSIGN")
        assert manager.is_mask_active() is True

        # Get masked string
        result = manager.get_masked_str("x = 5 # MASK_ASSIGN")
        assert "= None # TODO" in result

        # Continue masking (stays active with content)
        manager.update_state("    + more")
        assert manager.is_mask_active() is True

        # Deactivate with blank line
        manager.update_state("")
        assert manager.is_mask_active() is False

        # Can start another mask
        manager.update_state("return value # MASK_RETURN")
        assert manager.is_mask_active() is True
        assert manager.active_mask_type.name == "Return"

    def test_no_trigger_no_state_change(self, manager):
        """Line without trigger doesn't change inactive state."""
        manager.update_state("regular code line")
        assert manager.is_mask_active() is False

    def test_return_mask_type(self, manager):
        """Return mask type works correctly."""
        manager.update_state("return calculate() # MASK_RETURN")
        result = manager.get_masked_str("return calculate() # MASK_RETURN")

        # start_char is "return", so everything from "return" onward is replaced
        assert "return None # TODO" in result


class TestInvalidMaskError:
    """Tests for InvalidMaskError exception."""

    def test_init_with_message(self):
        """Exception stores message correctly."""
        err = InvalidMaskError("Test error message")
        assert err.message == "Test error message"
        assert err.error_code == 1

    def test_init_with_error_code(self):
        """Exception stores custom error code."""
        err = InvalidMaskError("Test", error_code=42)
        assert err.error_code == 42

    def test_str_includes_message_and_code(self):
        """String representation includes message and code."""
        err = InvalidMaskError("Test error", error_code=5)
        s = str(err)
        assert "Test error" in s
        assert "5" in s
