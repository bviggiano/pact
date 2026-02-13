# PACT - Claude Code Instructions

PACT (Programming Assignment Creation Tool) converts solution code into student-ready assignment versions by processing trigger keywords.

## Quick Reference

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=pact --cov-report=term-missing

# Convert all assignments
python pact/convert_all.py

# Convert single assignment
python pact/convert_assignment.py path/to/assignment
```

## Project Structure

```
pact/
├── pact/                           # Main package
│   ├── convert/
│   │   ├── codeblocks.py          # CodeBlockType definitions
│   │   ├── masks.py               # MaskType definitions
│   │   └── utils/
│   │       ├── codeblock_infra.py # CodeBlockManager, CodeBlockType classes
│   │       ├── mask_infra.py      # MaskManager, MaskType classes
│   │       ├── file_converter.py  # FileConverter (single file conversion)
│   │       └── prime_converter.py # PrimeConverter (directory conversion)
│   ├── zip/
│   │   ├── zip_assignment.py      # zip_assignment_dir()
│   │   └── zip_submission.py      # create_submission_file()
│   ├── convert_all.py             # CLI: convert all assignments
│   └── convert_assignment.py      # CLI: convert single assignment
├── tests/
│   ├── unit_tests/                # Unit tests for individual classes
│   ├── integration_tests/         # Integration tests for converters
│   └── convert_tests/             # Original conversion tests
└── assignments/                   # Example assignments
```

## Core Concepts

### Codeblocks
Replace entire sections of code between start/end triggers:
```python
# STUDENT_CODE_START
secret_implementation()
# STUDENT_CODE_END
```
Becomes a placeholder like `# TODO: Implement` in student version.

### Masks
Partially mask lines from a start character onward:
```python
result = compute_answer()  # MASK_ASSIGNMENT
```
Becomes `result = None # TODO: Implement` in student version.

### Special Files (in assignment root)
- `black_list.pact` - Regex patterns for files to exclude
- `sub_list.pact` - Files to include in student submission
- `options.pact` - Options like `no_submission_file`

## Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `CodeBlockType` | `codeblock_infra.py` | Defines a codeblock trigger pair |
| `CodeBlockManager` | `codeblock_infra.py` | Tracks active codeblock state during conversion |
| `MaskType` | `mask_infra.py` | Defines a mask trigger and replacement |
| `MaskManager` | `mask_infra.py` | Tracks active mask state during conversion |
| `FileConverter` | `file_converter.py` | Converts a single file |
| `PrimeConverter` | `prime_converter.py` | Converts directories, handles config files |

## Important Constants

```python
# prime_converter.py
GENERATED_LOCATION_NAME = "STUDENT_VERSION"  # Output folder name
BLACK_LIST_FILE_NAME = "black_list.pact"
SUB_LIST_FILE_NAME = "sub_list.pact"
OPTIONS_FILE_NAME = "options.pact"

# file_converter.py
IPYNB_CELL_EXCLUDE = "ANSWER_KEY_CELL"  # Excludes entire notebook cell
```

## Conversion Flow

1. `PrimeConverter.convert(path)` is called
2. Loads config files (`black_list.pact`, `sub_list.pact`, `options.pact`)
3. Creates `STUDENT_VERSION/` output directory
4. Recursively processes files through `FileConverter`
5. Creates submission script and zip file

## Adding New Codeblock/Mask Types

**Codeblock** (`pact/convert/codeblocks.py`):
```python
NEW_BLOCK = CodeBlockType(
    name="New Block",
    start_trigger_str="NEW_START",
    end_trigger_str="NEW_END",
    replacement_str="\n# Replacement text\n",  # Must start with \n
)
```

**Mask** (`pact/convert/masks.py`):
```python
NEW_MASK = MaskType(
    name="New Mask",
    trigger_str="MASK_NEW",
    start_char="=",  # Masking starts here
    mask_str="= None # TODO",
)
```

## Error Classes

- `InvalidCodeBlockError` - Unclosed blocks, nested blocks, mismatched triggers
- `InvalidMaskError` - Missing start char, nested masks

## Testing Conventions

- Unit tests in `tests/unit_tests/`
- Integration tests in `tests/integration_tests/`
- Use `tmp_path` fixture for file operations
- Test fixtures defined in `tests/conftest.py`

## Common Tasks

### Add a test for a new feature
1. Determine if unit test (single class) or integration test (multiple components)
2. Add to appropriate file in `tests/unit_tests/` or `tests/integration_tests/`
3. Use existing fixtures from `conftest.py` when possible

### Debug conversion issues
1. Check for `InvalidCodeBlockError` or `InvalidMaskError` in output
2. Verify trigger strings match exactly (case-sensitive)
3. Ensure codeblocks aren't nested
4. Ensure masks have blank line between uses

### Modify conversion behavior
1. For new block/mask types: edit `codeblocks.py` or `masks.py`
2. For file handling: edit `file_converter.py`
3. For directory/config handling: edit `prime_converter.py`
