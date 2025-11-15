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

# Standardize province column name
df = df.rename(columns={"region": "Provincia"})

# List of months in correct order
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# -----------------------------
# SIDEBAR — FILTERS
# -----------------------------
st.sidebar.header("Filters")

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
st.subheader("📊 General Indicators")

col1, col2, col3, col4 = st.columns(4)

# Calculate KPI metrics
media_nacional = df["anual"].mean()
max_prov = df.loc[df["anual"].idxmax()]
min_prov = df.loc[df["anual"].idxmin()]

# Display KPIs
col1.metric("💧 National annual mean", f"{media_nacional:.1f} mm")
col2.metric("🌧️ Maximum annual", f"{max_prov['anual']} mm", max_prov["Provincia"])
col3.metric("🌦️ Minimum annual", f"{min_prov['anual']} mm", min_prov["Provincia"])
col4.metric("📍 Provinces analyzed", len(df))

st.markdown("---")

# -----------------------------
# MONTHLY PRECIPITATION PLOT
# -----------------------------
st.subheader("📈 Monthly precipitation evolution")

# Transform data from wide to long format
df_melt = data_filtrada.melt(
    id_vars=["Provincia"],
    value_vars=MESES,
    var_name="Mes",
    value_name="Precipitación"
)

# Create line plot
fig_line = px.line(
    df_melt,
    x="Mes",
    y="Precipitación",
    color="Provincia" if provincia_seleccion == "Todas" else None,
    markers=True,
    title="Monthly precipitation"
)

st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# ANNUAL RANKING PLOT
# -----------------------------
st.subheader("🏆 Annual precipitation ranking by province")

fig_bar = px.bar(
    df.sort_values("anual", ascending=False),
    x="Provincia",
    y="anual",
    title="Annual ranking (mm)",
)

st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("🧾 Data table")

# Display the filtered table with formatting
st.dataframe(
    data_filtrada.style.format("{:.1f}"),
    use_container_width=True
)
