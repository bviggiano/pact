from setuptools import setup, find_packages

setup(
    name="pact",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "zipp",
        "pytest",
        "nbclient",
        "nbformat",
        "ipykernel",
    ],
    entry_points={
        "console_scripts": [
            "pact-validate-notebooks=pact.validate_notebooks:main",
        ],
    },
)
