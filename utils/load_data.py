import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------
# FUNCTION: Load precipitation dataset
# ---------------------------------------------------
@st.cache_data(show_spinner=True)
def load_precip_data(year: int = 2021) -> pd.DataFrame:
    """
    Load the precipitation dataset for the selected year.
    Returns a cleaned DataFrame with standardized 'Provincia' column.
    """

    file_path = os.path.join("data", f"PREC_{year}_Provincias.csv")

    # Check if file exists
    if not os.path.exists(file_path):
        st.error(f"No se encontró el archivo: {file_path}. Asegúrate de subirlo a la carpeta 'data'.")
        st.stop()

    # Load CSV
    df = pd.read_csv(file_path, sep=';', encoding="utf-8")

    # Check if DataFrame is empty
    if df.empty:
        st.error(f"El archivo {file_path} está vacío.")
        st.stop()

    # Clean column names
    df.columns = df.columns.str.lower().str.strip()

    # Detect and standardize province column
    possible_names = ["provincia", "region", "prov", "prov_name", "nombre"]
    found = False
    for col in df.columns:
        if col in possible_names:
            df = df.rename(columns={col: "Provincia"})
            found = True
            break

    if not found:
        st.error(f"No se encontró ninguna columna de provincia en {file_path}. Columnas disponibles: {list(df.columns)}")
        st.stop()

    # Capitalize province names
    df["Provincia"] = df["Provincia"].str.title()

    return df
