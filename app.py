import streamlit as st
import folium
import numpy as np
import rasterio
from folium import raster_layers
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Dashboard Pemetaan Fase Tumbuh Jagung 🌽")

st.markdown("Peta hasil klasifikasi fase tumbuh jagung di Kabupaten Karo.")

with st.sidebar:
    st.header("Pengaturan")
    opacity = st.slider("Opacity layer", 0.0, 1.0, 0.6)

# DATA TIDAK BISA DIMUAT SAAT INI (PERLU DIUPLOAD SECARA MANUAL)
st.warning("⚠️ Upload raster klasifikasi `.tif` ke folder `data/` agar peta bisa ditampilkan.")

# Buat peta kosong dulu
m = folium.Map(location=[3.2, 98.4], zoom_start=10)
st_data = st_folium(m, width=1000, height=600)
