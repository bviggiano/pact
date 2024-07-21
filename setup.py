from setuptools import setup, find_packages

setup(
    name="pact",
    version="0.1.0",
    package_dir={"": "pact"},
    packages=find_packages(where="pact"),
    install_requires=["zipp"],
)
