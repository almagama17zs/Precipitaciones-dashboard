import streamlit as st
import plotly.express as px
import pandas as pd
from utils.load_data import load_precip_data
import os
import base64

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Precipitaciones España 2021",
    page_icon="🌧️",
    layout="wide"
)

# -----------------------------
# LOAD CUSTOM CSS (FORCE BLUE SIDEBAR)
# -----------------------------
css_path = "assets/style.css"
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.warning("No se encontró el CSS en assets/style.css")

# Hack para barra lateral multi-page (clase interna de Streamlit)
st.markdown("""
<style>
/* Sidebar general */
div[data-testid="stSidebar"] {
    background-color: #cce6ff !important;
    padding: 0 !important;
}

/* Reduce top spacing */
div[data-testid="stSidebarContent"] {
    padding-top: 5px !important;
    margin-top: 0 !important;
}

/* Logo styling */
div[data-testid="stSidebar"] img {
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-top: 5px !important;
    margin-bottom: 10px !important;
    width: 70% !important;
}

/* Sidebar headings spacing */
div[data-testid="stSidebarContent"] h2,
div[data-testid="stSidebarContent"] h3,
div[data-testid="stSidebarContent"] h4 {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Optional: selectbox spacing */
div[data-testid="stSidebar"] .stSelectbox {
    margin-top: 5px !important;
    margin-bottom: 5px !important;
}

/* Force blue background for multi-page menu (hack) */
.css-18e3th9 { 
    background-color: #cce6ff !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR LOGO (arriba) usando base64
# -----------------------------
logo_path = "assets/logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_bytes = f.read()
        logo_b64 = base64.b64encode(logo_bytes).decode()
    st.sidebar.markdown(
        f'<div style="text-align:center; margin-bottom:10px;">'
        f'<img src="data:image/png;base64,{logo_b64}" style="width:70%;"/>'
        f'</div>',
        unsafe_allow_html=True
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
if "Provincia" not in df.columns:
    st.error("No se encontró la columna 'Provincia' en los datos.")
    st.stop()

MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]

# -----------------------------
# SIDEBAR — FILTERS
# -----------------------------
st.sidebar.header("Filtros")
provincia_seleccion = st.sidebar.selectbox(
    "Provincia:",
    options=["Todas"] + sorted(df["Provincia"].unique())
)
data_filtrada = df if provincia_seleccion == "Todas" else df[df["Provincia"] == provincia_seleccion]

# -----------------------------
# KPIs
# -----------------------------
st.subheader("📊 Indicadores generales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💧 Media anual nacional", f"{df['anual'].mean():.1f} mm")
max_prov = df.loc[df['anual'].idxmax()]
min_prov = df.loc[df['anual'].idxmin()]
col2.metric("🌧️ Provincia más lluviosa", f"{max_prov['anual']:.1f} mm", max_prov["Provincia"])
col3.metric("🌦️ Provincia menos lluviosa", f"{min_prov['anual']:.1f} mm", min_prov["Provincia"])
col4.metric("📍 Provincias analizadas", len(df))

st.markdown("---")

# -----------------------------
# MONTHLY PRECIPITATION PLOT
# -----------------------------
st.subheader("📈 Evolución mensual de precipitación")
df_melt = data_filtrada.melt(id_vars=["Provincia"], value_vars=MESES, var_name="Mes", value_name="Precipitación")
fig_line = px.line(df_melt, x="Mes", y="Precipitación",
                   color="Provincia" if provincia_seleccion == "Todas" else None,
                   markers=True, title="Precipitación mensual")
st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# ANNUAL RANKING PLOT
# -----------------------------
st.subheader("🏆 Ranking anual de precipitación por provincia")
fig_bar = px.bar(df.sort_values("anual", ascending=False), x="Provincia", y="anual", title="Ranking anual (mm)")
st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("🧾 Tabla de datos")
numeric_cols = data_filtrada.select_dtypes(include='number').columns
df_display = data_filtrada.copy()
df_display[numeric_cols] = df_display[numeric_cols].round(1)
st.dataframe(df_display, use_container_width=True)
