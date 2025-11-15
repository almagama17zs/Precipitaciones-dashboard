# -----------------------------
# SUMMARY PAGE – National overview
# -----------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_precip_data

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Resumen - Precipitaciones 2021", layout="wide")

# -----------------------------
# LOAD CUSTOM CSS (FORCE BLUE SIDEBAR + BLACK TEXT)
# -----------------------------
st.markdown("""
<style>
/* Barra lateral completa */
[data-testid="stSidebar"] {
    background-color: #cce6ff !important;
    color: #000 !important; /* Letras negras */
    padding-top: 10px !important;
}

/* Contenido de la barra lateral */
[data-testid="stSidebarContent"] {
    padding-top: 10px !important;
    color: #000 !important;
}

/* Sidebar headings */
[data-testid="stSidebarContent"] h2,
[data-testid="stSidebarContent"] h3,
[data-testid="stSidebarContent"] h4 {
    margin-top: 0 !important;
    padding-top: 0 !important;
    color: #000 !important;
}

/* Opcional: selectbox spacing */
[data-testid="stSidebar"] .stSelectbox {
    margin-top: 5px !important;
    margin-bottom: 5px !important;
}

/* Multi-page menu hack: azul + texto negro */
.css-18e3th9, .css-1d391kg {
    background-color: #cce6ff !important;
    color: #000 !important;
}

/* Forzar color negro en links del menú lateral */
.css-18e3th9 a, .css-1d391kg a {
    color: #000 !important;
    text-decoration: none;
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
        f'<div style="text-align:center; margin-bottom:15px;">'
        f'<img src="data:image/png;base64,{logo_b64}" style="width:70%;"/>'
        f'</div>',
        unsafe_allow_html=True
    )

# -----------------------------
# LOAD DATA
# -----------------------------
# English: We load the main dataset using the shared utility function.
df = load_precip_data()

# Standardize column names
if "region" in df.columns:
    df = df.rename(columns={"region": "Provincia"})

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Convert numeric columns
cols = MESES + ["anual"]
for c in cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# -----------------------------
# TITLE & INTRO
# -----------------------------
st.title("🌍 Resumen nacional — Precipitaciones 2021")
st.markdown("Visión general de las precipitaciones registradas en España durante 2021. Este panel reúne los indicadores clave y los gráficos principales.")

st.markdown("---")

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
# English: Compute the most important national metrics.
media_anual = df["anual"].mean()
max_prov = df.loc[df["anual"].idxmax()]
min_prov = df.loc[df["anual"].idxmin()]
total_lluvia = df["anual"].sum()

# -----------------------------
# KPI DISPLAY
# -----------------------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("📦 Media anual (mm)", f"{media_anual:.1f}")
k2.metric("🌧️ Provincia más lluviosa", f"{max_prov['Provincia']} — {max_prov['anual']:.1f} mm")
k3.metric("🌦️ Provincia más seca", f"{min_prov['Provincia']} — {min_prov['anual']:.1f} mm")
k4.metric("💧 Total nacional (mm)", f"{total_lluvia:,.0f}")

st.markdown("---")

# -----------------------------
# BAR CHART: Ranking anual nacional
# -----------------------------
st.subheader("🏆 Ranking anual de precipitación (todas las provincias)")

# English: Create sorted DataFrame for ranking.
rank_df = df.sort_values(by="anual", ascending=False)

fig_rank = px.bar(
    rank_df,
    x="Provincia",
    y="anual",
    title="Ranking anual de precipitación",
    labels={"anual": "Precipitación (mm)", "Provincia": "Provincia"},
)
fig_rank.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_rank, use_container_width=True)

st.markdown("---")

# -----------------------------
# HEATMAP: Precipitación mensual por provincia
# -----------------------------
st.subheader("🌡️ Heatmap — Precipitación mensual por provincia")

# English: Build a melt dataframe to create a heatmap-like chart.
df_melt = df.melt(
    id_vars=["Provincia"],
    value_vars=MESES,
    var_name="Mes",
    value_name="Valor"
)

df_melt["Mes"] = pd.Categorical(df_melt["Mes"], categories=MESES, ordered=True)

fig_heat = px.imshow(
    df[MESES],
    labels=dict(color="mm"),
    x=MESES,
    y=df["Provincia"],
    aspect="auto",
    title="Mapa de calor mensual (mm)"
)

st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# -----------------------------
# DISTRIBUTION: Distribución anual
# -----------------------------
st.subheader("📊 Distribución de la precipitación anual")

fig_hist = px.histogram(
    df,
    x="anual",
    nbins=20,
    title="Distribución de precipitación anual",
    labels={"anual": "Precipitación anual (mm)"}
)
st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# -----------------------------
# FOOTER
# -----------------------------
st.write("Explora más en las otras páginas del panel: mapa, provincias, comparaciones y tendencias.")
