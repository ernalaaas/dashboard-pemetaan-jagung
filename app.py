import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import rasterio
from folium.raster_layers import ImageOverlay
from rasterio.enums import Resampling
import matplotlib.cm as cm
import os
import requests

# Konfigurasi halaman
st.set_page_config(layout="wide")
st.title("🌽 Dashboard Pemetaan Fase Tumbuh Jagung")
st.markdown("Basemap: Google Satellite | Overlay: Hasil klasifikasi fase tumbuh jagung")

# === Sidebar
with st.sidebar:
    st.header("Pengaturan")
    opacity = st.slider("Transparansi layer klasifikasi", 0.0, 1.0, 0.6)
    uploaded_file = st.file_uploader("Upload file raster (.tif)", type=["tif", "tiff"])

# === Path file default dari Google Drive
file_id = "19gAUxtX8kmCrdQypFF46UqiEWXtLLyEG"
default_path = "data/hasil_klasifikasi.tif"
os.makedirs("data", exist_ok=True)

# === Download file jika belum ada
if not os.path.exists(default_path):
    st.info("📥 Mengunduh file klasifikasi dari Google Drive...")
    url = f"https://drive.google.com/uc?id={file_id}"
    r = requests.get(url)
    with open(default_path, "wb") as f:
        f.write(r.content)

# === Fungsi konversi array raster ke RGB image
def array_to_rgb(array):
    max_val = np.max(array)
    if max_val == 0:
        array = np.ones_like(array)
        max_val = 1
    cmap = cm.get_cmap("tab10", int(max_val + 1))
    rgba = cmap(array / max_val)
    return (rgba[:, :, :3] * 255).astype(np.uint8)


# === Baca file raster dan tampilkan di peta
try:
    st.write("✅ Maksimum nilai raster:", np.max(data))
    st.write("✅ Ukuran raster:", data.shape)

    if uploaded_file is not None:
        src = rasterio.open(uploaded_file)
        st.success("✅ File raster berhasil diunggah.")
    else:
        src = rasterio.open(default_path)

    data = src.read(1, resampling=Resampling.nearest)
    bounds = src.bounds
    extent = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
    rgb_image = array_to_rgb(data)

    # === Buat peta
    center = [(bounds.top + bounds.bottom) / 2, (bounds.left + bounds.right) / 2]
    m = folium.Map(location=center, zoom_start=11)

    # Basemap: Google Satellite
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite",
        overlay=False,
        control=True
    ).add_to(m)

    # Overlay raster klasifikasi
    ImageOverlay(
        image=rgb_image,
        bounds=extent,
        opacity=opacity,
        name="Klasifikasi Jagung"
    ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)

except Exception as e:
    st.error(f"❌ Gagal menampilkan peta: {e}")
