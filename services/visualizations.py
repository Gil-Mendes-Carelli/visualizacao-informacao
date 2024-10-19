import streamlit as st
import pandas as pd

def display_data(data: pd.DataFrame) -> None:
    """Exibe os dados em formato de tabela."""
    st.write("Dados Carregados:")
    st.dataframe(data)

def display_bar_chart(data: pd.DataFrame) -> None:
    """Exibe um gráfico de barras da primeira coluna dos dados."""
    st.subheader("Visualizações")
    st.bar_chart(data.iloc[:, 0])  # Alterar conforme necessário para outras visualizações