import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------
# FUNCTION: Load precipitation dataset
# ---------------------------------------------------
# English: Load CSV for a specific year. Uses Streamlit cache for performance.
@st.cache_data(show_spinner=True)
def load_precip_data(year: int = 2021) -> pd.DataFrame:
    """
    English:
    Loads the precipitation dataset for the selected year.
    Supports files named using the pattern:
        PREC_<year>_Provincias.csv

    Example:
        PREC_2021_Provincias.csv

    Returns:
        pandas.DataFrame: Cleaned dataset.
    """

    # Build dynamic filename according to your actual file naming
    file_path = os.path.join("data", f"PREC_{year}_Provincias.csv")

    # Check file existence
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"No se encontró el archivo: {file_path}. "
            f"Verifica que está dentro de /data."
        )

    # Load CSV
    df = pd.read_csv(file_path, encoding="utf-8")

    # English: Clean column names for consistency
    df.columns = df.columns.str.lower().str.strip()

    # English: Detect and standardize the province column
    possible_names = ["provincia", "region", "prov", "prov_name", "nombre"]
    for col in df.columns:
        if col in possible_names:
            df = df.rename(columns={col: "Provincia"})
            break

    # English: Capitalize province names
    if "Provincia" in df.columns:
        df["Provincia"] = df["Provincia"].str.title()

    return df
