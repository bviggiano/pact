"""
vectorized.py
"""

import pandas as pd


def check_speed_vectorized(poke_df: pd.DataFrame, speed_min: int = 100) -> pd.DataFrame:
    """
    Creates a new column in the DataFrame called "is_fast" containing a boolean value
    for each Pokemon. The value should be True if the Pokemon's speed is above the
    variable `speed_min` and False otherwise.

    IMPLEMENTATION INSTRUCTIONS:
        - Use vectorized operations to create the new column.
        - Do not use any for loops.

    Args:
        poke_df (pd.DataFrame): A pandas DataFrame containing the Pokemon data.
        speed_min (int): The minimum speed threshold for a Pokemon to be considered fast.

    Returns:
        pd.DataFrame: The pandas DataFrame containing the Pokemon data with an additional
                      column called "is_fast" that contains a boolean value for each Pokemon
    """

    # STUDENT_CODE_START

    # Add new column
    poke_df["is_fast"] = poke_df["Speed"] > speed_min

    # STUDENT_CODE_END

    return poke_df


def filter_by_type(poke_df: pd.DataFrame, poke_type: str) -> pd.DataFrame:
    """
    Filters the DataFrame to only include Pokemon that are of the specified type.

    IMPLEMENTATION INSTRUCTIONS:
        - Use vectorized operations to filter the DataFrame.
        - Do not use any for loops.
        - IMPORTANT: Do not modify the original DataFrame.

    Args:
        poke_df (pd.DataFrame): A pandas DataFrame containing the Pokemon data.
        poke_type (str): The type of Pokemon to filter by.

    Returns:
        pd.DataFrame: The filtered pandas DataFrame containing only Pokemon of the specified type.
    """

    # STUDENT_CODE_START

    # Overwrite this variable in your implementation
    filtered_df = None

    # Filter the DataFrame
    filtered_df = poke_df[
        (poke_df["Type 1"] == poke_type) | (poke_df["Type 2"] == poke_type)
    ]

    # STUDENT_CODE_END

    return filtered_df


def check_mega_evo(poke_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a column in the DataFrame called "is_mega" containing a boolean value
    for each Pokemon. The value should be True if the Pokemon's name contains "Mega"
    and False otherwise.

    IMPLEMENTATION INSTRUCTIONS:
        - Use vectorized operations to create the new column.
        - Do not use any for loops.
        - HINT: You may find the documentation for the Series.str.contains() method helpful.

    Args:
        poke_df (pd.DataFrame): A pandas DataFrame containing the Pokemon data.

    Returns:
        pd.DataFrame: The pandas DataFrame containing the Pokemon data with an additional
                      column called "is_mega" that contains a boolean value for each Pokémon.
    """

    # STUDENT_CODE_START

    # Add new column
    poke_df["is_mega"] = poke_df["Name"].str.contains("Mega")

    # STUDENT_CODE_END

    return poke_df
