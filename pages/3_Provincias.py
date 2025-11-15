# Página de Provincias: KPIs detallados y comparativa
import streamlit as st
import pandas as pd
import plotly.express as px
import os 
import base64
from utils.load_data import load_precip_data
from utils.sidebar_style import apply_sidebar_style
# Mini-map imports
import folium
from streamlit_folium import st_folium

apply_sidebar_style()
# -----------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------
st.set_page_config(page_title="Provincias - Precipitaciones 2021", layout="wide")

# -----------------------------
# CARGAR DATOS
# -----------------------------
df = load_precip_data()

# Normalizar columna de provincia
if "region" in df.columns:
    df = df.rename(columns={"region": "Provincia"})

# Columnas de meses
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Asegurar tipos numéricos
numeric_cols = [c for c in MESES + ["anual"] if c in df.columns]
for c in numeric_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Filtros")
provincia = st.sidebar.selectbox("Selecciona provincia:", options=sorted(df["Provincia"].unique()))
top_n = st.sidebar.slider("Número de provincias en ranking (Top)", 5, 50, 10, 1)
mes_ranking = st.sidebar.selectbox("Mes para ranking:", ["anual"] + MESES, index=0)

# -----------------------------
# DATOS DE LA PROVINCIA SELECCIONADA
# -----------------------------
prov_df = df[df["Provincia"] == provincia].reset_index(drop=True)
if prov_df.empty:
    st.error("Provincia no encontrada.")
    st.stop()

# -----------------------------
# KPIs
# -----------------------------
anual_prov = float(prov_df["anual"].iloc[0])

meses_presentes = [m for m in MESES if pd.notna(prov_df[m].iloc[0])]
if meses_presentes:
    valores = prov_df[meses_presentes].iloc[0]
    mes_max = valores.idxmax()
    val_max = float(valores.max())
    mes_min = valores.idxmin()
    val_min = float(valores.min())
else:
    mes_max = mes_min = None
    val_max = val_min = None

media_nacional_anual = float(df["anual"].mean())
posicion_ranking = int(
    df["anual"].rank(method="min", ascending=False).loc[df["Provincia"] == provincia].iloc[0]
)

# -----------------------------
# MOSTRAR KPIs
# -----------------------------
st.title(f"📍 Análisis — {provincia}")
st.markdown("KPIs y visualizaciones detalladas de la provincia seleccionada.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("💧 Total anual (mm)", f"{anual_prov:.1f}")
k2.metric("🌧️ Mes más lluvioso", f"{mes_max.title()} — {val_max:.1f} mm" if mes_max else "N/A")
k3.metric("🌦️ Mes menos lluvioso", f"{mes_min.title()} — {val_min:.1f} mm" if mes_min else "N/A")
k4.metric("🏷 Ranking anual", f"{posicion_ranking} / {len(df)}")

st.markdown("---")

# -----------------------------
# MINI MAPA
# -----------------------------
st.subheader("🗺️ Ubicación de la provincia")
center_lat = prov_df["lat"].iloc[0] if "lat" in prov_df.columns else 40.0
center_lon = prov_df["lon"].iloc[0] if "lon" in prov_df.columns else -3.7

m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="CartoDB positron")
folium.Marker(
    location=[center_lat, center_lon],
    popup=provincia,
    tooltip=provincia,
    icon=folium.Icon(color="blue")
).add_to(m)
st_folium(m, width=500, height=350)

st.markdown("---")

# -----------------------------
# GRÁFICOS DE LÍNEA — Provincia vs Media Nacional
# -----------------------------
st.subheader("📈 Precipitación mensual — Provincia vs Media nacional")
serie_prov = prov_df[MESES].T.reset_index()
serie_prov.columns = ["Mes", "Valor"]
serie_prov["Tipo"] = provincia

media_mensual = df[MESES].mean().reset_index()
media_mensual.columns = ["Mes", "Valor"]
media_mensual["Tipo"] = "Media nacional"

plot_df = pd.concat([serie_prov, media_mensual])
plot_df["Mes"] = pd.Categorical(plot_df["Mes"], categories=MESES, ordered=True)

fig_line = px.line(
    plot_df,
    x="Mes",
    y="Valor",
    color="Tipo",
    markers=True,
    title=f"Comparativa mensual — {provincia} vs Media nacional"
)
fig_line.update_layout(legend_title_text="Serie")
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# -----------------------------
# BARRAS — Precipitación mensual provincia
# -----------------------------
st.subheader("📊 Precipitación por mes — Provincia seleccionada")
fig_bar = px.bar(
    serie_prov,
    x="Mes",
    y="Valor",
    title=f"Precipitación mensual en {provincia}",
    labels={"Valor": "Precipitación (mm)"}
)
fig_bar.update_xaxes(categoryorder="array", categoryarray=MESES)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# -----------------------------
# RANKING TOP N
# -----------------------------
st.subheader(f"🏆 Ranking — Top {top_n} por '{mes_ranking}'")
if mes_ranking not in df.columns:
    st.warning("La columna seleccionada no existe.")
else:
    rank_df = df[["Provincia", mes_ranking]].dropna().sort_values(by=mes_ranking, ascending=False)
    rank_top = rank_df.head(top_n)

    fig_rank = px.bar(
        rank_top[::-1],
        x=mes_ranking,
        y="Provincia",
        orientation="h",
        title=f"Top {top_n} — {mes_ranking}"
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    if provincia in rank_df["Provincia"].values:
        pos = rank_df.index[rank_df["Provincia"] == provincia][0] + 1
        st.write(f"{provincia} está en la posición **{pos}** del ranking para '{mes_ranking}'.")

st.markdown("---")

# -----------------------------
# TABLA — Provincia vs Media Nacional
# -----------------------------
st.subheader("🧾 Datos detallados y comparativa")

fila_prov = prov_df[["Provincia"] + MESES + ["anual"]].copy()
fila_prov["Tipo"] = provincia

fila_media = pd.DataFrame(
    [["Media nacional"] + list(df[MESES].mean().round(1)) + [media_nacional_anual]],
    columns=["Provincia"] + MESES + ["anual"]
)
fila_media["Tipo"] = "Media nacional"

tabla = pd.concat([fila_prov, fila_media]).set_index("Tipo")

# ✅ FORMATEAR SOLO COLUMNAS NUMÉRICAS
numericas = tabla.select_dtypes(include="number").columns
st.dataframe(tabla.style.format({col: "{:.1f}" for col in numericas}))

st.markdown("---")
st.write("Sugerencias: cambia provincia, ajusta el Top o elige otro mes para explorar variaciones.")
