# Página de Mapa: Coropletas de precipitación por provincia española
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import unicodedata
from utils.load_data import load_precip_data

# -----------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------
st.set_page_config(page_title="Mapa - Precipitaciones 2021", layout="wide")
st.title("🗺️ Mapa — Precipitación por provincia (2021)")
st.sidebar.header("Opciones de mapa")

# -----------------------------
# CARGAR DATOS
# -----------------------------
df = load_precip_data()
if "region" in df.columns:
    df = df.rename(columns={"region": "Provincia"})

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

mes = st.sidebar.selectbox("Mes / Anual", options=["anual"] + MESES, index=0)

# -----------------------------
# FUNCIÓN DE NORMALIZACIÓN
# -----------------------------
def normalize(s):
    """Normaliza texto a minúsculas y sin acentos para comparación."""
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("provincia de ", "")
    s = "".join(ch for ch in s if ch.isalnum() or ch.isspace())
    s = " ".join(s.split())
    return s

# -----------------------------
# CARGAR GEOJSON
# -----------------------------
GEOJSON_URL = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-provinces.geojson"
try:
    geojson = requests.get(GEOJSON_URL, timeout=20).json()
except Exception:
    st.error("No se pudo cargar el GeoJSON remoto. Verifica conexión o usa un archivo local.")
    st.stop()

# Normalizamos nombres en GeoJSON
for f in geojson["features"]:
    f["properties"]["name_norm"] = normalize(f["properties"].get("name"))

# -----------------------------
# MAPEO MANUAL CSV -> GEOJSON
# -----------------------------
PROV_MAPPING = {
    "Alicante": "Alicante",
    "Alava": "Álava",
    "Araba": "Álava",
    "Bizkaia": "Vizcaya",
    "Gipuzkoa": "Guipúzcoa",
    "Castellon": "Castellón",
    "Cordoba": "Córdoba",
    "Granada": "Granada",
    "Huelva": "Huelva",
    "Jaen": "Jaén",
    "Leon": "León",
    "Lleida": "Lérida",
    "Madrid": "Madrid",
    "Malaga": "Málaga",
    "Murcia": "Murcia",
    "Navarra": "Navarra",
    "Ourense": "Orense",
    "Palencia": "Palencia",
    "Pontevedra": "Pontevedra",
    "Sevilla": "Sevilla",
    "Valencia": "Valencia",
    "Zaragoza": "Zaragoza",
    "Santa Cruz de Tenerife": "Santa Cruz de Tenerife",
    "Las Palmas": "Las Palmas",
    "Toledo": "Toledo",
    "Segovia": "Segovia",
    "Valladolid": "Valladolid",
    "Burgos": "Burgos",
    "Cantabria": "Cantabria",
    "La Rioja": "La Rioja",
    "Asturias": "Asturias",
    "Guadalajara": "Guadalajara",
    "Albacete": "Albacete",
    "Ciudad Real": "Ciudad Real",
    "Soria": "Soria",
    "Teruel": "Teruel",
    "Huesca": "Huesca"
}

# -----------------------------
# PREPARAR DATOS PARA EL MAPA
# -----------------------------
df_map = df.groupby("Provincia", as_index=False).agg({mes: "mean"})
df_map["geo_name"] = df_map["Provincia"].map(PROV_MAPPING)
plot_df = df_map.dropna(subset=["geo_name"]).copy()
plot_df["geo_norm"] = plot_df["geo_name"].apply(normalize)

# -----------------------------
# GRAFICO COROPLETA
# -----------------------------
fig = px.choropleth(
    plot_df,
    geojson=geojson,
    locations="geo_norm",
    featureidkey="properties.name_norm",  # ahora coincide con la normalización
    color=mes,
    hover_name="Provincia",
    hover_data={mes: True},
    labels={mes: "Precipitación (mm)"},
    title=f"Mapa de precipitación — {mes.capitalize()}"
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TABLA DE DATOS
# -----------------------------
st.markdown("---")
st.subheader("Datos de precipitación por provincia")
st.dataframe(plot_df[["Provincia", mes]].sort_values(mes, ascending=False).reset_index(drop=True))
