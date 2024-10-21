import pandas as pd
from typing import TextIO

def load_csv_from_file(file: str | TextIO) -> pd.DataFrame:
    return pd.read_csv(file)