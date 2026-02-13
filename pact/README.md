# How to use `pact`

<p align="center">
  <img src="https://img.shields.io/badge/Keywords-Codeblocks_&_Masks-blue?style=for-the-badge" alt="Keywords">
  <img src="https://img.shields.io/badge/Files-.py_•_.ipynb-orange?style=for-the-badge" alt="Supported Files">
  <img src="https://img.shields.io/badge/Output-Student_Ready-green?style=for-the-badge" alt="Output">
</p>

In this README, we will explain the basics of how to use `pact` and this template repository.

---

## Summary

`pact` works by converting fully solved programming assignments into versions that
are ready to distribute to students. This customizable behavior is achieved
through the use of keywords and comments in the solution version of the assignments
that `pact` can recognize and act upon.

---

## 📝 How to create an assignment using `pact`

<table>
<tr>
<td width="60">

**Step**

</td>
<td>

**Action**

</td>
</tr>
<tr>
<td align="center">

🗂️

</td>
<td>

**Create a new assignment directory** in the `assignments` folder. This directory will contain the solution version.

</td>
</tr>
<tr>
<td align="center">

✍️

</td>
<td>

**Add the solution code** — fully solved and working.

</td>
</tr>
<tr>
<td align="center">

🔑

</td>
<td>

**Add `pact` keywords** to define the regions that should be masked in the student version (see below).

</td>
</tr>
<tr>
<td align="center">

⚙️

</td>
<td>

**Generate the student versions** by running:

```bash
python pact/convert_all.py
```

</td>
</tr>
</table>

> [!TIP]
> A GitHub workflow is included that automatically runs `convert_all.py` when you push to `main` and creates a release with zip files of all student versions.

---

## 🤔 How do I use `pact` keywords?

Let's look at the different types of `pact` keywords and how they customize the conversion process.

<br>

### <img src="https://img.shields.io/badge/Code_Blocks-<>-blue?style=flat-square" alt="Code Blocks">

Code blocks are used to **completely mask (and optionally replace)** entire portions of solution code.

<table>
<tr>
<th>🔐 Solution Version</th>
<th>📄 Student Version</th>
</tr>
<tr>
<td>

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

</td>
<td>

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

</td>
</tr>
</table>

To use a codeblock, wrap the code you want to mask with the start and end keyword strings.
See all available code block types in [`./convert/codeblocks.py`](./convert/codeblocks.py)

> [!IMPORTANT]
> **Rules for Code Blocks:**
> - Start and end keywords must be on **separate lines**
> - Everything between triggers is masked, **including the trigger lines themselves**
> - Code blocks **cannot be nested**

<br>

### <img src="https://img.shields.io/badge/Line_Masks-={}-orange?style=flat-square" alt="Line Masks">

Line masks allow you to **partially mask lines**, providing more structure to students.

<table>
<tr>
<th>🔐 Solution Version</th>
<th>📄 Student Version</th>
</tr>
<tr>
<td>

```python
self.transformer = nn.ModuleDict( # MASK_ASSIGNMENT
            dict(
                wte=nn.Embedding(config.vocab_size, config.n_embd),
                wpe=nn.Embedding(config.block_size, config.n_embd),
                drop=nn.Dropout(config.embd_pdrop),
                h=nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
                ln_f=nn.LayerNorm(config.n_embd),
            )
        )

self.lm_head = nn.Linear(...) # MASK_ASSIGNMENT
```

</td>
<td>

```python
self.transformer = None # TODO: Implement

self.lm_head = None # TODO: Implement
```

</td>
</tr>
</table>

To use a line mask, add the keyword string to the end of the line you want to mask.
See all available line mask types in [`./convert/masks.py`](./convert/masks.py)

> [!IMPORTANT]
> **Rules for Line Masks:**
> - Masks start from a predefined character (e.g., `=`) and replace everything after it
> - Masking **continues across multiple lines** until an empty line is found
> - Ensure a **blank line** between separate masked sections

<br>

### <img src="https://img.shields.io/badge/Jupyter_Notebooks-📒-yellow?style=flat-square" alt="Notebooks">

For Jupyter notebooks (`.ipynb` files), you can exclude entire cells from the student version.

Simply add `ANSWER_KEY_CELL` anywhere within a cell to exclude it completely.

---

## 📁 Special Files

Place these files in your assignment's root directory to customize conversion behavior:

| File | Purpose |
|:-----|:--------|
| <img src="https://img.shields.io/badge/black__list.pact-Exclude_files-red?style=flat-square" alt="blacklist"> | List files/folders to **exclude** from student version |
| <img src="https://img.shields.io/badge/sub__list.pact-Submission_files-green?style=flat-square" alt="sublist"> | List files that should be in student **submissions** |
| <img src="https://img.shields.io/badge/options.pact-Options-purple?style=flat-square" alt="options"> | Conversion options (e.g., `no_submission_file`) |

<details>
<summary><strong>📋 Example: black_list.pact</strong></summary>

```
answer_output.txt
hidden_tests/
```

These files/folders will be excluded from the student version.

</details>

<details>
<summary><strong>📋 Example: sub_list.pact</strong></summary>

```
model.py
answer_output.txt
```

A `create_submission_zip.py` script will be generated that packages these files.

</details>

<details>
<summary><strong>📋 Example: options.pact</strong></summary>

```
no_submission_file
```

This skips generation of the `create_submission_zip.py` helper script.

</details>

---

## 🎨 Creating Custom Codeblocks and Masks

`pact` is designed to be extensible. Create your own types to fit your specific needs.

<br>

### Custom Codeblock

Edit [`./convert/codeblocks.py`](./convert/codeblocks.py):

```python
from pact.convert.utils.codeblock_infra import CodeBlockType

BONUS_CODE = CodeBlockType(
    name="Bonus Code Block",
    start_trigger_str="BONUS_START",
    end_trigger_str="BONUS_END",
    replacement_str="""
# ========== BONUS CHALLENGE ==========
# This is an optional bonus exercise.
pass
# =====================================
""",
)
```

| Parameter | Description |
|:----------|:------------|
| `name` | Descriptive name (used in error messages) |
| `start_trigger_str` | String that marks the beginning of the block |
| `end_trigger_str` | String that marks the end of the block |
| `replacement_str` | Text that replaces the entire block (use `""` to remove entirely) |

<br>

### Custom Mask

Edit [`./convert/masks.py`](./convert/masks.py):

```python
from pact.convert.utils.mask_infra import MaskType

MASK_RETURN_VALUE = MaskType(
    name="Return Value Mask",
    trigger_str="MASK_RETURN",
    start_char="return",
    mask_str="return None  # TODO: Return the correct value",
)
```

| Parameter | Description |
|:----------|:------------|
| `name` | Descriptive name (used in error messages) |
| `trigger_str` | String that triggers the mask (place in a comment) |
| `start_char` | Character/string where masking begins |
| `mask_str` | Text that replaces the masked portion |

---

## 🐍 Programmatic API

Use `pact` directly in your Python scripts:

```python
from pact.convert.utils.prime_converter import PrimeConverter

# Convert an entire assignment directory
converter = PrimeConverter()
converter.convert("path/to/assignment_folder")
```

<details>
<summary><strong>🔧 Advanced: Using FileConverter directly</strong></summary>

```python
from pact.convert.utils.file_converter import FileConverter
from pact.convert.codeblocks import CODEBLOCK_TYPES
from pact.convert.masks import MASKTYPES

converter = FileConverter(
    codeblock_types=CODEBLOCK_TYPES,
    mask_types=MASKTYPES,
)

converter.convert_file(
    source_file_path="path/to/solution.py",
    destination_folder_path="path/to/output/",
)
```

</details>

---

## 🔧 Troubleshooting

### <img src="https://img.shields.io/badge/InvalidCodeBlockError-red?style=flat-square" alt="Error">

This error occurs when codeblocks are not properly defined.

| Cause | Example |
|:------|:--------|
| **Unclosed block** | Missing `# STUDENT_CODE_END` |
| **Mismatched triggers** | Using `KEY_ONLY_END` to close `STUDENT_CODE_START` |
| **Nested blocks** | Placing one codeblock inside another |
| **Multiple triggers** | Two triggers on the same line |

<br>

### <img src="https://img.shields.io/badge/InvalidMaskError-red?style=flat-square" alt="Error">

This error occurs when masks are not properly defined.

| Cause | Solution |
|:------|:---------|
| **Missing start character** | Ensure the line with the mask trigger contains the `start_char` (e.g., `=`) |
| **Nested masks** | Add a **blank line** between masked sections |

```python
# ❌ Wrong - no blank line between masks
x = value  # MASK_ASSIGNMENT
y = other  # MASK_ASSIGNMENT

# ✅ Correct - blank line deactivates previous mask
x = value  # MASK_ASSIGNMENT

y = other  # MASK_ASSIGNMENT
```

---

## 💡 Tips

> **Use comments for triggers** — Place trigger strings inside comments so they don't affect code execution in the solution version.

> **Test your solution first** — Make sure your solution code runs correctly before adding `pact` triggers.

> **Check indentation** — Replacement strings for codeblocks will be indented to match the start trigger line.

> **Blank lines matter for masks** — Masks continue until a blank line is encountered. Use this to mask multi-line expressions.
