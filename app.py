import streamlit as st
import plotly.express as px
import pandas as pd
from utils.load_data import load_precip_data

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Precipitaciones España 2021",
    page_icon="🌧️",
    layout="wide"
)

# -----------------------------
# HEADER
# -----------------------------
st.title("🌧️ Dashboard de Precipitaciones en España — 2021")
st.markdown("Visualización interactiva de la precipitación mensual y anual por provincias.")

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_precip_data()

# Ensure the province column exists (already standardized in load_data.py)
if "Provincia" not in df.columns:
    st.error("No se encontró la columna 'Provincia' en los datos.")
    st.stop()

# List of months in correct order
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# -----------------------------
# SIDEBAR — FILTERS
# -----------------------------
st.sidebar.header("Filtros")

provincia_seleccion = st.sidebar.selectbox(
    "Provincia:",
    options=["Todas"] + sorted(df["Provincia"].unique())
)

# Apply province filter
if provincia_seleccion != "Todas":
    data_filtrada = df[df["Provincia"] == provincia_seleccion]
else:
    data_filtrada = df.copy()

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("📊 Indicadores generales")

col1, col2, col3, col4 = st.columns(4)

# Calculate KPI metrics
media_nacional = df["anual"].mean()
max_prov = df.loc[df["anual"].idxmax()]
min_prov = df.loc[df["anual"].idxmin()]

# Display KPIs in Spanish
col1.metric("💧 Media anual nacional", f"{media_nacional:.1f} mm")
col2.metric("🌧️ Provincia más lluviosa", f"{max_prov['anual']:.1f} mm", max_prov["Provincia"])
col3.metric("🌦️ Provincia menos lluviosa", f"{min_prov['anual']:.1f} mm", min_prov["Provincia"])
col4.metric("📍 Provincias analizadas", len(df))

st.markdown("---")

# -----------------------------
# MONTHLY PRECIPITATION PLOT
# -----------------------------
st.subheader("📈 Evolución mensual de precipitación")

df_melt = data_filtrada.melt(
    id_vars=["Provincia"],
    value_vars=MESES,
    var_name="Mes",
    value_name="Precipitación"
)

fig_line = px.line(
    df_melt,
    x="Mes",
    y="Precipitación",
    color="Provincia" if provincia_seleccion == "Todas" else None,
    markers=True,
    title="Precipitación mensual"
)

st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# ANNUAL RANKING PLOT
# -----------------------------
st.subheader("🏆 Ranking anual de precipitación por provincia")

fig_bar = px.bar(
    df.sort_values("anual", ascending=False),
    x="Provincia",
    y="anual",
    title="Ranking anual (mm)",
)

st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("🧾 Tabla de datos")

# Format only numeric columns to avoid ValueError
numeric_cols = data_filtrada.select_dtypes(include='number').columns
df_display = data_filtrada.copy()
df_display[numeric_cols] = df_display[numeric_cols].round(1)

st.dataframe(df_display, use_container_width=True)
