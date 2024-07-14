# Python Assignment Generation Environment (PAGE) 📄


PAGE is a simple Github based tool designed to help streamline the process of creating, versioning, and distributing python based programming assignments.

<center>
<img src="page.webp" width="200" height="200">
</center>


## Key Features ✨
- **Configurable Masking**: Easily convert programming assignment solutions into student-friendly "skelton" files by masking solution code and replacing with placeholders.

- **Testing and Grading integration**: 
Write unit tests for assignments that can be utilized with Gradescope or your own custom testing framework to automatically grade student submissions.

- **Version Control**: Automatically manage version control for course assignments, allowing for easy tracking of changes and updates to various assignment files.

## How it works! 🛠️
PAGE works by converting fully solved programming assignments into versions that are ready to distribute to students. This customizable behavior is achieved through the use of keywords and comments in the solution version of the assignments that PAGE can recognize and act upon.


## Getting Started 🚀
This PAGE repository is designed to be utilized as a starting template for a repository containing the assignments for your course. Since this repository will contain the solution versions of the assignments, it is recommended to keep it private to prevent students from accessing the solution code.

The easist way to get started with PAGE is to create a `private` fork of this repository. However, creating a private fork is a paid feature on Github that not all users may have access to. If you do not have access to a paid Github account, you can still use this repository as a starting template for your own private repository by following the steps below:
1. Clone this repository to your local machine.
2. Remove the `.git` folder from the cloned repository. (This will remove the git history from the local version of the repository).
3. Create a new private repository containing the contents of the cloned repository.


Finally, after you have your private repository set up, set up the page conda environment by running the following command from the root of the repository:
```bash
conda env create -f environment.yml
```

You can begin developing your assignments to the repository! Check out the [./page/README.md](./page/README.md) file for more information on how to use PAGE to create assignments.


## Contributing 🤝
Contributions to PAGE are welcome! Whether it's adding new features, fixing bugs, or improving documentation, all contributions are appreciated. 😁