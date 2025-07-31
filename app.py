import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import os

# === Konfigurasi halaman
st.set_page_config(layout="wide")
st.title("🌽 Dashboard Pemetaan Fase Tumbuh Jagung")
st.markdown("Visualisasi klasifikasi dari gambar PNG overlay pada peta satelit.")

# === Sidebar
with st.sidebar:
    st.header("Pengaturan")
    opacity = st.slider("Transparansi overlay", 0.0, 1.0, 0.6)

# === Path gambar dan koordinat bounds (WGS84 / lat-lon)
image_path = "data/2024-07_1Stage_filtered.png"

# GANTI KOORDINAT INI SESUAI HASIL KONVERSI DARI RASTER
# Contoh di bawah diasumsikan sudah dikonversi dari UTM ke lat-lon
image_bounds = [[3.095, 98.375], [3.155, 98.515]]  # [[south, west], [north, east]]

# === Cek file
if not os.path.exists(image_path):
    st.error(f"❌ Gambar PNG tidak ditemukan di: {image_path}")
else:
    # Pusatkan peta di tengah bounds
    center_lat = (image_bounds[0][0] + image_bounds[1][0]) / 2
    center_lon = (image_bounds[0][1] + image_bounds[1][1]) / 2

    # Buat peta
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    # Basemap: Google Satellite
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite"
    ).add_to(m)

    # Overlay PNG klasifikasi
    ImageOverlay(
        image=image_path,
        bounds=image_bounds,
        opacity=opacity,
        name="Klasifikasi Jagung"
    ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)
