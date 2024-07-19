"""
naive.py
"""

import pandas as pd


def check_speed_loop(poke_df: pd.DataFrame, speed_min: int = 100) -> pd.DataFrame:
    """
    Creates a new column in the DataFrame called "is_fast" containing a boolean value
    for each Pokemon. The value should be True if the Pokemon's speed is above the
    variable `speed_min` and False otherwise.

    IMPLEMENTATION INSTRUCTIONS:
        - Use a for loop to iterate over the rows of the DataFrame and set the value of
          the new column for each Pokemon.
        - Do not use the DataFrame.apply() method.
        - Do not use any vectorized operations.

    Args:
        poke_df (pd.DataFrame): A pandas DataFrame containing the Pokemon data.
        speed_min (int): The minimum speed threshold for a Pokemon to be considered fast.

    Returns:
        pd.DataFrame: The pandas DataFrame containing the Pokemon data with an additional
                      column called "is_fast" that contains a boolean value for each Pokemon.
    """

    # STUDENT_CODE_START

    # Copy the DataFrame to avoid modifying the original
    poke_df = poke_df.copy()

    # Create a new column with default value of False
    poke_df["is_fast"] = False

    # Iterate over the rows of the DataFrame
    for idx, row in poke_df.iterrows():
        # Set the value of the new column for each Pokemon
        if row["Speed"] > speed_min:
            poke_df.at[idx, "is_fast"] = True

    # STUDENT_CODE_END

    return poke_df
