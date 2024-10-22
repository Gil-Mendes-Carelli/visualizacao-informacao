import streamlit as st
from services.data_loader import load_csv_from_file
from services.visualizations import display_data, display_bar_chart
import pandas as pd
from io import BytesIO


class Dashboard:
    def __init__(self) -> None:
        self.data: pd.DataFrame = None

    def load_data(self) -> None:
        uploaded_file : BytesIO = st.file_uploader("Escolha um arquivo CSV", type="csv")
        if uploaded_file is not None:
            self.data = load_csv_from_file(uploaded_file)
            display_data(self.data)  # Exibe os dados carregados

    def display_visualizations(self) -> None:
        if self.data is not None:
            display_bar_chart(self.data)  # Exibe as visualizações