# Map page: Choropleth of precipitation by Spanish province (month or annual)
import streamlit as st
import pandas as pd
import requests
import json
import plotly.express as px
import unicodedata
from utils.load_data import load_precip_data
from difflib import get_close_matches

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(page_title="Map - Precipitation 2021", layout="wide")

st.title("🗺️ Map — Precipitation by Province (2021)")
st.markdown(
    "Choropleth map of Spanish provinces colored by precipitation. "
    "The map loads a public GeoJSON (commonly used source). If you prefer an official dataset "
    "(IGN / datos.gob.es), replace the GEOJSON_URL with your local file or official endpoint."
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_precip_data()
# Ensure the province column is named consistently
if "region" in df.columns:
    df = df.rename(columns={"region": "Provincia"})

# -----------------------------
# HELPERS
# -----------------------------
def normalize(s):
    """Normalize text to lowercase ASCII for fuzzy matching."""
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("provincia de ", "")
    # keep it safe: remove punctuation and double spaces
    s = "".join(ch for ch in s if ch.isalnum() or ch.isspace())
    s = " ".join(s.split())
    return s

# Public GeoJSON URL (widely used in examples)
GEOJSON_URL = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-provinces.geojson"

# -----------------------------
# SIDEBAR OPTIONS
# -----------------------------
st.sidebar.header("Map options")
month = st.sidebar.selectbox(
    "Month / Annual",
    options=[
        "anual",
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ],
    index=0
)

st.info("Loading provinces GeoJSON from a public repository — this requires internet access when running the app.")

# -----------------------------
# LOAD GEOJSON
# -----------------------------
try:
    res = requests.get(GEOJSON_URL, timeout=20)
    geojson = res.json()
    st.success("GeoJSON loaded from remote source.")
except Exception as e:
    st.error(
        "Could not load GeoJSON from remote source. If you are offline or prefer an official file, "
        "download a provinces GeoJSON (e.g. from IGN/Datos.gob.es) and point GEOJSON_URL to the local file."
    )
    st.stop()

# -----------------------------
# PREPARE NAME MATCHING
# -----------------------------
features = geojson.get("features", [])
# Try multiple properties that common geojsons use for the province name
geo_names = []
for f in features:
    props = f.get("properties", {})
    # try several common property names
    candidate = (
        props.get("name")
        or props.get("NAME")
        or props.get("NOMBRE")
        or props.get("prov_name")
        or props.get("nom")
        or None
    )
    geo_names.append(candidate)

# Build normalised mapping from normalized geo name -> original geo name
geo_norm = {}
for name in geo_names:
    if name is not None:
        geo_norm[normalize(name)] = name

# Normalize province names in the CSV
df["prov_norm"] = df["Provincia"].apply(normalize)

# Create mapping province_csv -> geojson name (try direct match then fuzzy)
mapping = {}
for prov, pn in zip(df["Provincia"], df["prov_norm"]):
    if pn in geo_norm:
        mapping[prov] = geo_norm[pn]
    else:
        # fuzzy match: cutoff can be tuned
        candidates = get_close_matches(pn, list(geo_norm.keys()), n=1, cutoff=0.7)
        if candidates:
            mapping[prov] = geo_norm[candidates[0]]
        else:
            mapping[prov] = None

# Notify if there are unmatched provinces
unmatched = [p for p, g in mapping.items() if g is None]
if unmatched:
    st.warning(
        f"Could not confidently match {len(unmatched)} provinces between CSV and GeoJSON. "
        f"Examples: {unmatched[:6]}. Provide a local GeoJSON with matching names or adjust the mapping."
    )

# -----------------------------
# PREPARE DATAFRAME FOR CHOROPLETH
# -----------------------------
value_col = month
# aggregate by province in case there are multiple rows per province
df_map = df.groupby("Provincia", as_index=False).agg({value_col: "mean", "prov_norm": "first"})
df_map["geo_name"] = df_map["Provincia"].map(mapping)
# drop those with no geo match
plot_df = df_map.dropna(subset=["geo_name"]).copy()
plot_df["geo_norm"] = plot_df["geo_name"].apply(normalize)

# -----------------------------
# PLOT CHOROPLETH
# -----------------------------
fig = px.choropleth(
    plot_df,
    geojson=geojson,
    locations="geo_norm",           # keys we created (normalized geo names)
    featureidkey="properties.name", # property used by the GeoJSON; may need change depending on the file
    color=value_col,
    hover_name="Provincia",
    hover_data={value_col: True},
    labels={value_col: "Precipitation (mm)"},
    title=f"Choropleth — {value_col}"
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# SHOW DATA
# -----------------------------
st.markdown("---")
st.subheader("Data used for the map")
st.dataframe(plot_df[["Provincia", value_col]].sort_values(value_col, ascending=False).reset_index(drop=True))
