import pandas as pd
import streamlit as st


@st.cache_data
def load_data(path="data/clean/dataset.csv"):
    """Lê o dataset já tratado (exportado ao final do notebook de EDA)."""
    df = pd.read_csv(path)
    # Duração em minutos, mais legível para o público do Dashboard 2
    df["duration_min"] = df["duration_ms"] / 60000
    return df
