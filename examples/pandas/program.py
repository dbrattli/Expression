import numpy as np
import pandas as pd

# Set seed
np.random.seed(520)

# Create a dataframe
df = pd.DataFrame(
    {
        "name": ["Ted"] * 3 + ["Lisa"] * 3 + ["Sam"] * 3,
        "subject": ["math", "physics", "history"] * 3,
        "score": np.random.randint(60, 100, 9),
    }
)


def get_subject_rank(input_df: pd.DataFrame):
    # Avoid overwrite the original dataframe
    input_df = input_df.copy()
    input_df["subject_rank"] = input_df.groupby(["subject"])["score"].rank(
        ascending=False
    )
    return input_df


# pipe method
df.pipe(get_subject_rank)
