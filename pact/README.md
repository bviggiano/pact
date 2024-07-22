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