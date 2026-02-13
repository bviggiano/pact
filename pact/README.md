# How to use PACT

In this README, we will explain the basics of how to use PACT and this template repository.

## Summary
PACT works by converting fully solved programming assignments into versions that
are ready to distribute to students. This customizable behavior is achieved 
through the use of keywords and comments in the solution version of the assignments
that PACT can recognize and act upon.

## How to create an assignment using PACT 📝

1. **Create a new assignment directory**: Create a new directory in the `assignments` folder of this repository. This directory will contain the solution version of the assignment.

2. **Add the solution code**: Add the solution code for the assignment to the directory you created in step 1. This code should be fully solved.

3. **Add PACT keywords**: Add PACT keywords to the solution code to define the regions that should be masked in the student version of the assignment. PACT keywords are used to define code blocks, line masks, and other types of masking (Read more on this below).

4. **Generate the student versions**: To create the student versions of the assignments in the `assignments` directory, run the following command from the root of the repository:

    ```bash
    python pact/convert_all.py
    ```

    This command will generate a new directory within each assignment containing the student ready version.

In addition, we have included a GitHub workflow that will automatically run the `convert_all.py` script whenever you push to the `main` branch of the repository and will generate zip files containing the student versions of the assignments as a release.


## How do I use PACT keywords? 🤔

Let's take a look at the different types of PACT keywords and how they can be used to customize the behavior of the conversion process.

### Code Blocks `<>`

The most basic type of keyword trigger is a code block! Code blocks are used to
completely mask (and optionally replace) entire portions of solution code. Let's
look at an example:
    
```python
def forward(self, x):
    """
    Forward pass of the attention block.
    """

    # STUDENT_CODE_START
    x = x + self.attn(self.ln_1(x))
    x = x + self.mlpf(self.ln_2(x))
    # STUDENT_CODE_END

    return x
```

In this example, the `STUDENT_CODE_START` and `STUDENT_CODE_END` keywords are used
to define a block of code that should be masked in the student version of the assignment.
The masked code will be replaced with a customizable comment indicating that the student 
should complete the code in that region.

```python
def forward(self, x):
    """
    Forward pass of the attention block.
    """

    # ==== YOUR CODE HERE ====

    # TODO: Implement
    pass

    # === YOUR CODE HERE ===

    return x
```

To use a codeblock, simply wrap the code you want to mask in the solution version
of the assignment with the start and stop keyword strings of the code block type
of your choosing. To see all available code block types and define your own custom
code blocks, check out: [`./convert/codeblocks.py`](./convert/codeblocks.py)

#### Important Considerations for Code Blocks
- To correctly use code blocks, the start and end keywords must be placed on separate lines.
- Code blocks are defined to mask everything between the start and end keywords, **including the lines containing the keywords themselves.**
- Code blocks can NOT be nested within each other.


### Line Masking `= {}`

PACT also supports the ability to partially mask lines, allowing us to provide a
bit more structure to the student version of the assignment. For example, lets say
we have the following function and we only want to mask the part of the line after
the assignment operator:

```python

self.transformer = nn.ModuleDict( # MASK_ASSINGMENT
            dict(
                wte=nn.Embedding(config.vocab_size, config.n_embd),
                wpe=nn.Embedding(config.block_size, config.n_embd),
                drop=nn.Dropout(config.embd_pdrop),
                h=nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
                ln_f=nn.LayerNorm(config.n_embd),
            )
        )

self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False) # MASK_ASSIGNMENT

```

In this example, the `MASK_ASSIGNMENT` keyword is used to define a line mask that
will only mask the portion of the line after the assignment operator. The masked
code will be replaced with a customizable comment indicating that the student should
complete the code in that region.

```python

self.transformer = None # TODO: Implement

self.lm_head = None # TODO: Implement

```

To use a line mask, simply add the keyword string of the line mask type of your choosing
to the end of the line you want to mask in the solution version of the assignment. To
see all available line mask types and define your own custom line masks, check out:
[`./convert/masks.py`](./convert/masks.py)

#### Important Considerations for Line Masks
- Line masks are defined to mask everything after a predefined character. This character can be any character you choose, but it must be in any line you want to mask.
    - In the above example, we chose the assignment operator `=` as the character to define start of the line mask.
- Line masks will continue to mask all lines after the line the keyword was found on *until an empty line(line only containing whitespace) is found.*
    - In the above example, this allows us to mask the entire assignment statement for self.transformer even though it spans multiple lines.


### Masking `ipynb` files 📒
Jupyter notebooks (`.ipynb` files) are commonly used for creating programming assignments.
In addition to the normal functionality of PACT, we have added a special keyword that allows
you to mask entire cells in a Jupyter notebook. This is useful for hiding entire sections of
code or markdown that you want to keep hidden from students.

To exclude an entire cell from the student version of the `ipynb` file, simply add the following
keyword anywhere within the cell: `ANSWER_KEY_CELL`.


### Special Files 📁

In addition to the keywords described above, PACT also recognizes a few
special files that can be used to customize the behavior of the conversion process.

1. `black_list.pact`: By placing a file named `black_list.pact` in the root of your assignment directory, you can specify a list of files/folders that you don't want to be included in the student version of the assignment. This is useful for excluding files that contain data or other information that should not be distributed to students.

Each line in the `black_list.pact` file should contain the path to a file or folder that you want to exclude from the student version of the assignment. For example, let's say we had the following in our `black_list.pact` file:

    answer_output.txt
    hidden_tests/

In this case, a hypothetical `answer_output.txt` file and the `hidden_tests` folder would be excluded from the student version of the assignment.


2. `sub_list.pact`: By placing a file named `sub_list.pact` in the root of your assignment directory, you can specify a list of files that should be included in student's submissions. The conversion process automatically generates a file called `create_submission_zip.py` that will create a zip file containing all the files listed in `sub_list.pact`. This is useful for including files that students need to submit along with their assignment.

Each line in the `sub_list.pact` file should contain the path to a file that you want to include in the student version of the assignment. For example, let's say we had the following in our `sub_list.pact` file:

    model.py
    answer_output.txt

In this case, a hypothetical `model.py` file and `answer_output.txt` file would be included in the student version of the assignment. If no `sub_list.pact` file is found, the `create_submission_zip.py` script will create a zip file containing all the files in the student version of the assignment (with the original directory structure preserved).


3. `options.pact`: By placing a file named `options.pact` in the root of your assignment directory, you can specify options that modify the conversion behavior.

Available options:
- `no_submission_file`: Skip generation of the `create_submission_zip.py` file. Useful when you don't want students to have a submission helper script.

Example `options.pact`:
```
no_submission_file
```


## Creating Custom Codeblocks and Masks

PACT is designed to be extensible. You can create your own custom codeblock types and mask types to fit your specific needs.

### Creating a Custom Codeblock

To add a new codeblock type, edit [`./convert/codeblocks.py`](./convert/codeblocks.py):

```python
from pact.convert.utils.codeblock_infra import CodeBlockType

# Define your custom codeblock
BONUS_CODE = CodeBlockType(
    name="Bonus Code Block",
    start_trigger_str="BONUS_START",
    end_trigger_str="BONUS_END",
    replacement_str="""
# ========== BONUS CHALLENGE ==========
# This is an optional bonus exercise.
# Remove this comment and add your implementation.
pass
# =====================================
""",
)
```

**Parameters:**
- `name`: A descriptive name for the codeblock (used in error messages)
- `start_trigger_str`: The string that marks the beginning of the block
- `end_trigger_str`: The string that marks the end of the block
- `replacement_str`: The text that replaces the entire block (including trigger lines). Use an empty string `""` to remove the block entirely.

### Creating a Custom Mask

To add a new mask type, edit [`./convert/masks.py`](./convert/masks.py):

```python
from pact.convert.utils.mask_infra import MaskType

# Define your custom mask
MASK_RETURN_VALUE = MaskType(
    name="Return Value Mask",
    trigger_str="MASK_RETURN",
    start_char="return",
    mask_str="return None  # TODO: Return the correct value",
)
```

**Parameters:**
- `name`: A descriptive name for the mask (used in error messages)
- `trigger_str`: The string that triggers the mask (place in a comment on the line)
- `start_char`: The character/string where masking begins (everything from this point to end of line is replaced)
- `mask_str`: The text that replaces the masked portion


## Programmatic API

You can use PACT programmatically in your Python scripts:

```python
from pact.convert.utils.prime_converter import PrimeConverter

# Create a converter
converter = PrimeConverter()

# Convert a single file
converter.convert("path/to/solution_file.py")

# Convert an entire assignment directory
converter.convert("path/to/assignment_folder")
```

For more control, you can use the `FileConverter` directly:

```python
from pact.convert.utils.file_converter import FileConverter
from pact.convert.codeblocks import CODEBLOCK_TYPES
from pact.convert.masks import MASKTYPES

# Create a file converter with default codeblocks and masks
converter = FileConverter(
    codeblock_types=CODEBLOCK_TYPES,
    mask_types=MASKTYPES,
)

# Convert a single file to a destination folder
converter.convert_file(
    source_file_path="path/to/solution.py",
    destination_folder_path="path/to/output/",
)
```


## Troubleshooting

### Common Errors

#### `InvalidCodeBlockError`

This error occurs when codeblocks are not properly defined.

**Common causes:**
- **Unclosed codeblock**: You have a start trigger without a matching end trigger.
  ```python
  # STUDENT_CODE_START
  code here
  # Missing STUDENT_CODE_END!
  ```
- **Mismatched triggers**: The end trigger doesn't match the start trigger type.
  ```python
  # STUDENT_CODE_START
  code here
  # KEY_ONLY_END  # Wrong! Should be STUDENT_CODE_END
  ```
- **Nested codeblocks**: You cannot nest one codeblock inside another.
  ```python
  # STUDENT_CODE_START
  # KEY_ONLY_START  # Error! Cannot nest blocks
  code
  # KEY_ONLY_END
  # STUDENT_CODE_END
  ```
- **Multiple triggers on one line**: Each line can only contain one trigger.
  ```python
  # STUDENT_CODE_START KEY_ONLY_START  # Error!
  ```

#### `InvalidMaskError`

This error occurs when masks are not properly defined.

**Common causes:**
- **Missing start character**: The first line with a mask trigger must contain the `start_char`.
  ```python
  some_code()  # MASK_ASSIGNMENT  # Error! No '=' on this line
  ```
- **Nested masks**: You cannot have multiple mask triggers active simultaneously.
  ```python
  x = value  # MASK_ASSIGNMENT
  y = other  # MASK_ASSIGNMENT  # Error! Previous mask still active (no blank line)
  ```

**Solution:** Ensure there's a blank line between masked sections:
```python
x = value  # MASK_ASSIGNMENT

y = other  # MASK_ASSIGNMENT  # OK! Blank line deactivated previous mask
```

### Tips

1. **Use comments for triggers**: Place trigger strings inside comments so they don't affect code execution in the solution version.

2. **Test your solution first**: Make sure your solution code runs correctly before adding PACT triggers.

3. **Check indentation**: The replacement string for codeblocks will be indented to match the start trigger line's indentation.

4. **Blank lines matter for masks**: Masks continue until a blank line is encountered. Use this to mask multi-line expressions.