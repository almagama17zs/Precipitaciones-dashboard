# Page: Choropleth of precipitation by Spanish province (fixed)
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import unicodedata
from utils.load_data import load_precip_data

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(page_title="Map - Precipitation 2021", layout="wide")
st.title("🗺️ Map — Precipitation by Province (2021)")
st.sidebar.header("Map options")

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_precip_data()
if "region" in df.columns:
    df = df.rename(columns={"region": "Provincia"})

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

mes = st.sidebar.selectbox("Month / Annual", options=["anual"] + MESES, index=0)

# -----------------------------
# NORMALIZATION FUNCTION
# -----------------------------
def normalize(s):
    """Normalize text to lowercase ASCII for matching."""
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
# LOAD GEOJSON
# -----------------------------
GEOJSON_URL = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-provinces.geojson"
try:
    geojson = requests.get(GEOJSON_URL, timeout=20).json()
except Exception:
    st.error("Could not load remote GeoJSON. Check connection or use a local file.")
    st.stop()

# Normalize names in GeoJSON
geo_names_set = set()
for f in geojson["features"]:
    f["properties"]["name_norm"] = normalize(f["properties"].get("name"))
    geo_names_set.add(f["properties"]["name_norm"])

# -----------------------------
# MANUAL CSV -> GEOJSON MAPPING
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
# PREPARE DATA FOR MAP
# -----------------------------
df_map = df.groupby("Provincia", as_index=False).agg({mes: "mean"})
df_map["geo_name"] = df_map["Provincia"].map(PROV_MAPPING)
df_map["geo_norm"] = df_map["geo_name"].apply(normalize)

# Ensure color column is numeric and fill NaN
df_map[mes] = pd.to_numeric(df_map[mes], errors="coerce").fillna(0)

# Filter only provinces present in GeoJSON
plot_df = df_map[df_map["geo_norm"].isin(geo_names_set)].copy()
if plot_df.empty:
    st.error("No matching provinces found between CSV and GeoJSON.")
    st.stop()

# -----------------------------
# CHOROPLETH MAPBOX
# -----------------------------
fig = px.choropleth_mapbox(
    plot_df,
    geojson=geojson,
    locations="geo_norm",
    featureidkey="properties.name_norm",
    color=mes,
    hover_name="Provincia",
    hover_data={mes: True},
    labels={mes: "Precipitación (mm)"},
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    center={"lat": 40, "lon": -4},
    zoom=5,
    opacity=0.7,
    title=f"Mapa de precipitación — {mes.capitalize()}"
)

fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.markdown("---")
st.subheader("Datos de precipitación por provincia")
st.dataframe(
    plot_df[["Provincia", "anual"] + MESES].sort_values(mes, ascending=False).reset_index(drop=True)
)
