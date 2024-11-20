import base64
import io
import pandas as pd
from typing import List, TextIO
import matplotlib.pyplot as plt
import missingno as msno
import plotly.graph_objects as go
import plotly.express as px

# gambiarra?
import matplotlib

matplotlib.use("Agg")


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


def remove_object_columns_from(
    dataframe: pd.DataFrame, label_column: str
) -> pd.DataFrame:
    object_columns: List = dataframe.select_dtypes(include="object").columns.to_list()
    object_columns.remove(label_column)
    return dataframe.drop(columns=object_columns)


def normalize_data_from(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized_dataframe = dataframe.copy()  # Faz uma cópia do DataFrame original
    numeric_columns = normalized_dataframe.select_dtypes(
        include=["float64", "int64"]
    ).columns
    
    normalized_dataframe[numeric_columns] = (
        normalized_dataframe[numeric_columns]
        - normalized_dataframe[numeric_columns].min()
    ) / (
        normalized_dataframe[numeric_columns].max()
        - normalized_dataframe[numeric_columns].min()
    )
    
    return normalized_dataframe

def plot_parallel_coordinates_from(dataframe: pd.DataFrame) -> go.Figure:
    # Identifica as colunas numéricas do DataFrame
    numeric_columns = dataframe.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # Define os rótulos com base nos valores da primeira coluna
    labels = {col: dataframe[col].iloc[1] for col in numeric_columns}
    # print(f"tamanho lista de rótulos: {len(labels)}")
    # Gera o gráfico de coordenadas paralelas
    fig = px.parallel_coordinates(
        dataframe,
        dimensions=numeric_columns,  # Colunas numéricas
        color=dataframe[numeric_columns[1]],  # Cor com base na primeira coluna numérica
        labels=labels  # Rótulos definidos pelos valores da primeira coluna
    )

    return fig