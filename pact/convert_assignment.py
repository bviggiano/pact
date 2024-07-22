"""
convert_assignment.py

Creates student versions of assignment files by converting solution versions of
the files.
"""

import argparse
from pact.convert.utils.prime_converter import PrimeConverter

if __name__ == "__main__":

    # Create an argument parser
    parser = argparse.ArgumentParser(
        description="Convert solution versions of assignment files into student versions."
    )

    # Add arguments
    parser.add_argument(
        "source_file_or_folder",
        type=str,
        help="The path to the solution version of the assignment file to convert.",
    )

    # Load the arguments
    args = parser.parse_args()

    # Create prime converter
    prime_converter = PrimeConverter()

    # Convert the source file/folder
    prime_converter.convert(source_file_or_folder=args.source_file_or_folder)
