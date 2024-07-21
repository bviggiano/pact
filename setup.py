from setuptools import setup, find_packages

setup(
    name="page",
    version="0.1.0",
    package_dir={"": "page"},
    packages=find_packages(where="page"),
    install_requires=["zipp"],
)
