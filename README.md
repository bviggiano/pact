# Programming Assignment Creation Tool (PACT) 📄


PACT is a simple Github based tool designed to help streamline the process of creating, versioning, and distributing programming assignments.

<center>
    <img src="pact.webp" width="200" height="200">
</center>

## How it works! 🛠️
PACT works by converting fully solved programming assignments into versions that are ready to distribute to students. This customizable behavior is achieved through the use of keywords and comments in the solution version of the assignments that PACT can recognize and act upon.

Here's an example! Let's say we want students to implement the forward function
of an attention block. We indicate the region of code that the students should
complete by surrounding it with customizable trigger keywords:
    
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

PACT will then use these keywords to generate a student version of the assignment file that masks the
code between the `STUDENT_CODE_START` and `STUDENT_CODE_END` keywords. The masked code will be replaced with a customizable comment indicating that the student should complete the code in that region.

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

PACT also supports the ability to partially mask lines, allowing us to provide a
bit more structure to the student version of the assignment. For example, we can
mask only the portion of the line after the assignment operator:

```python
def add(a, b):
    """
    Adds two numbers and returns the result.
    """

    c = a + b # MASK_ASSIGNMENT

    return x
```

In the student facing version of the assignment, the masked line can be replaced
with a customizable string:

```python
def add(a, b):
    """
    Adds two numbers and returns the result.
    """

    c = None # TODO: Implement

    return c
```


## Getting Started 🚀
This PACT repository is designed to be utilized as a starting template for a repository containing the assignments for your course. Since this repository will contain the solution versions of the assignments, it is recommended to keep it private to prevent students from accessing the solution code.

The easiest way to get started with PACT is to use this repository as a template.
1. Navigate to [github.com/bviggiano/pact](https://github.com/bviggiano/pact)
2. Click on the "Use this template" button, located above the file list and next to the "Code" button.
3. Select "Create a new repository"
4. On the repository creation page, choose a repository name (e.g., `CS101`) and set the visibility to `private`.


Finally, after you have your private repository set up, set up the pact conda environment by running the following commands from the root of the repository:
```bash
conda env create -f environment.yml
conda activate pact_env
pip install -e .
```

You can begin developing your assignments to the repository! Check out the [./pact/README.md](./pact/README.md) file for more information on how to use PACT to create assignments.


## Contributing 🤝
Contributions to PACT are welcome! Whether it's adding new features, fixing bugs, or improving documentation, all contributions are appreciated. 😁

## License 📝
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<center>
Happy Coding! 🚀
</center>

