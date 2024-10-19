import streamlit as st
from uinterface.dashboard import Dashboard

def main():
    st.title("Visualizador de Dados Multidimensionais")
    dashboard = Dashboard()
    dashboard.load_data()
    # dashboard.display_visualizations()

if __name__ == "__main__":
    main()