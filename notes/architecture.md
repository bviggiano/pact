# PACT Architecture

## Overview

PACT uses a layered architecture for converting solution code to student versions:

```
┌─────────────────────────────────────────────────────┐
│                    CLI Layer                         │
│         convert_all.py / convert_assignment.py       │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  PrimeConverter                      │
│  - Handles directories recursively                   │
│  - Loads config files (black_list, sub_list, etc)   │
│  - Creates STUDENT_VERSION output                    │
│  - Generates zip and submission script               │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  FileConverter                       │
│  - Converts individual files                         │
│  - Handles text files, ipynb, images                │
│  - Coordinates CodeBlockManager and MaskManager      │
└─────────────────────────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
┌─────────────────────┐   ┌─────────────────────┐
│  CodeBlockManager   │   │    MaskManager      │
│  - Tracks state     │   │  - Tracks state     │
│  - Start/end logic  │   │  - Trigger logic    │
│  - Replacement      │   │  - Partial masking  │
└─────────────────────┘   └─────────────────────┘
              │                       │
              ▼                       ▼
┌─────────────────────┐   ┌─────────────────────┐
│   CodeBlockType     │   │     MaskType        │
│  (data class)       │   │   (data class)      │
└─────────────────────┘   └─────────────────────┘
```

## State Machine: CodeBlockManager

```
                    ┌──────────────────┐
     ┌──────────────│    INACTIVE      │◄─────────────┐
     │              │ active_block=None│              │
     │              └────────┬─────────┘              │
     │                       │                        │
     │              START trigger found               │
     │                       │                        │
     │                       ▼                        │
     │              ┌──────────────────┐              │
     │              │     ACTIVE       │       END trigger found
     │              │ active_block=type│──────────────┘
     │              └──────────────────┘
     │
     │ END trigger without START → InvalidCodeBlockError
     │ Nested START → InvalidCodeBlockError
     │ Wrong END type → InvalidCodeBlockError
     │ EOF while ACTIVE → InvalidCodeBlockError
```

## State Machine: MaskManager

```
                    ┌──────────────────┐
     ┌──────────────│    INACTIVE      │◄─────────────┐
     │              │ active_mask=None │              │
     │              └────────┬─────────┘              │
     │                       │                        │
     │             MASK trigger found                 │
     │                       │                        │
     │                       ▼                        │
     │              ┌──────────────────┐              │
     │              │     ACTIVE       │    Blank line encountered
     │              │ active_mask=type │──────────────┘
     │              └──────────────────┘
     │
     │ Nested MASK trigger → InvalidMaskError
     │ Missing start_char → InvalidMaskError
```

## File Processing Flow

```
FileConverter.convert_file(source, dest)
    │
    ├─► Is .ipynb?
    │       │
    │       └─► Parse JSON
    │           Remove cells with ANSWER_KEY_CELL
    │           Process cell sources through _convert_source_text
    │           Clear outputs/execution_count
    │           Write JSON
    │
    ├─► Is image? (.png, .jpg, .jpeg, .gif, .tiff)
    │       │
    │       └─► Binary copy (no processing)
    │
    └─► Is text file?
            │
            └─► Read lines
                For each line:
                    1. Update CodeBlockManager state
                    2. Update MaskManager state
                    3. If codeblock active: skip line (replacement added on deactivate)
                    4. If mask active: apply mask to line
                    5. Otherwise: keep line as-is
                Check end_of_file (no open blocks)
                Write result
```

## Extension Points

1. **New codeblock types**: Add to `pact/convert/codeblocks.py`
2. **New mask types**: Add to `pact/convert/masks.py`
3. **New file types**: Modify `FileConverter._convert_file()` method
4. **New options**: Add handling in `PrimeConverter.convert()`
