import base64
import io
import pandas as pd
from typing import List, TextIO
import matplotlib.pyplot as plt
import missingno as msno

# gambiarra?
import matplotlib
matplotlib.use('Agg') 

def generate_missing_data_matrix_from(dataframe: pd.DataFrame) -> str:
    fig = plt.figure()
    # Generating the matrix
    msno.matrix(dataframe, ax=fig.add_subplot(111), sparkline=False)
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    plt.close(fig)
    # encoding the image on base64
    encoded_image: str = base64.b64encode(img_buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_image}"

def remove_nan_rows_from(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.dropna()

def remove_object_columns_from(dataframe: pd.DataFrame, label_column: str) -> pd.DataFrame:
    object_columns: List = dataframe.select_dtypes(include="object").columns.to_list()
    object_columns.remove(label_column)
    return dataframe.drop(columns=object_columns)