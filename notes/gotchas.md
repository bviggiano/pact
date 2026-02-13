# PACT Gotchas and Notes

This file captures gotchas, edge cases, and learnings discovered while working on PACT.

## Replacement String Format

**Gotcha**: `CodeBlockType.replacement_str` must start with `\n` if it contains multiple lines.

The `get_replacement_str()` method assumes the replacement string starts with a newline and strips it:
```python
if self.replacement_str[0] == "\n":
    replacement_str = self.replacement_str[1:]
```

If your replacement string doesn't start with `\n`, you'll get an `UnboundLocalError`.

**Correct**:
```python
replacement_str="\n# TODO: Implement\npass\n"
```

**Incorrect**:
```python
replacement_str="# TODO: Implement\npass\n"  # Will cause error
```

## Mask Deactivation

**Gotcha**: Masks stay active until a blank line is encountered.

This is intentional - it allows multi-line expressions to be masked:
```python
result = long_function(  # MASK_ASSIGNMENT
    arg1,
    arg2,
)
# Mask still active on lines above!

# Blank line here deactivates the mask
```

If you need consecutive masked lines, ensure there's a blank line between them.

## Codeblock Nesting

**Gotcha**: Codeblocks cannot be nested, even of different types.

This will fail:
```python
# STUDENT_CODE_START
# KEY_ONLY_START  # Error!
...
# KEY_ONLY_END
# STUDENT_CODE_END
```

## Filter Behavior

**Gotcha**: `black_list.pact` uses regex matching, not glob patterns.

To exclude a folder named `hidden/`, use:
```
hidden/
```

To exclude all `.secret` files:
```
.*\.secret$
```

## ipynb Handling

**Gotcha**: The `ANSWER_KEY_CELL` marker excludes the entire cell, not just that line.

Place it anywhere in a cell (code or markdown) to exclude the whole cell from student version.

## File Encoding

**Gotcha**: Binary files (images, etc.) are detected by catching `UnicodeDecodeError`.

If you add a new binary file type, it will be handled automatically. Image files (`.png`, `.jpg`, `.jpeg`, `.gif`, `.tiff`) are explicitly copied without processing.

## Test Fixtures

The `tests/conftest.py` file contains shared fixtures. Key ones:
- `tmp_path` - pytest built-in for temporary directories
- `mock_assignment_dir` - creates a sample assignment structure
- `file_converter` - pre-configured FileConverter
- `prime_converter` - fresh PrimeConverter instance

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/unit_tests/test_codeblock_infra.py -v

# With coverage
python -m pytest tests/ --cov=pact --cov-report=term-missing

# Stop on first failure
python -m pytest tests/ -x
```
