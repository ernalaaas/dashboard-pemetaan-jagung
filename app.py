import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import rasterio
from folium.raster_layers import ImageOverlay
from rasterio.plot import reshape_as_image
from rasterio.enums import Resampling
from matplotlib import cm
import matplotlib.pyplot as plt
import os
import requests

st.set_page_config(layout="wide")
st.title("Dashboard Pemetaan Fase Tumbuh Jagung 🌽")
st.markdown("Peta interaktif hasil klasifikasi fase tumbuh jagung di Kabupaten Karo.")

# === Sidebar ===
with st.sidebar:
    st.header("Pengaturan Layer")
    opacity = st.slider("Transparansi Layer", 0.0, 1.0, 0.6)
    uploaded_file = st.file_uploader("Upload file raster (.tif)", type=["tif", "tiff"])

# === File default dari Google Drive ===
output_path = "data/hasil_klasifikasi.tif"
gdrive_url = "https://drive.google.com/uc?id=19gAUxtX8kmCrdQypFF46UqiEWXtLLyEG"

if not os.path.exists(output_path):
    with st.spinner("📥 Mengunduh file raster dari Google Drive..."):
        r = requests.get(gdrive_url)
        os.makedirs("data", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(r.content)

# === Fungsi untuk membaca dan mengatur warna dari raster ===
def load_raster_colormap(raster_array):
    colormap = cm.get_cmap('tab10', np.max(raster_array))
    colored = colormap(raster_array / np.max(raster_array))
    return (colored[:, :, :3] * 255).astype(np.uint8)

# === Proses dan tampilkan peta ===
try:
    if uploaded_file is not None:
        st.success("✅ File klasifikasi berhasil diunggah dan digunakan.")
        src = rasterio.open(uploaded_file)
    else:
        src = rasterio.open(output_path)

    data = src.read(1, resampling=Resampling.nearest)
    bounds = src.bounds
    extent = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

    # Ubah data menjadi citra RGB dengan colormap
    image_rgb = load_raster_colormap(data)

    # Buat peta dan tampilkan layer citra
    m = folium.Map(location=[3.2, 98.4], zoom_start=11, tiles="CartoDB positron")

    # Tambahkan basemap Google Satellite
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    # Layer klasifikasi
    ImageOverlay(
        image=image_rgb,
        bounds=extent,
        opacity=opacity,
        name="Hasil Klasifikasi",
        interactive=True,
        cross_origin=False,
        zindex=1
    ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)

except Exception as e:
    st.error(f"❌ Gagal memuat raster: {e}")
