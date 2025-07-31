import streamlit as st
import folium
import numpy as np
import rasterio
from folium import raster_layers
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import os
import gdown

st.set_page_config(layout="wide")
st.title("Dashboard Pemetaan Fase Tumbuh Jagung 🌽")
st.markdown("Basemap: Google Satellite | Overlay: Hasil klasifikasi fase tumbuh jagung")

# === Sidebar ===
with st.sidebar:
    st.header("Pengaturan")
    opacity = st.slider("Transparansi layer klasifikasi", 0.0, 1.0, 0.6)

# === Download raster dari Google Drive jika belum ada ===
file_id = "19gAUxtX8kmCrdQypFF46UqiEWXtLLyEG"  # GANTI sesuai file kamu
output_path = "data/hasil_klasifikasi.tif"

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(output_path):
    st.info("⏳ Mengunduh file klasifikasi dari Google Drive...")
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)

# === Proses dan tampilkan peta jika tif ada ===
if os.path.exists(output_path):
    with rasterio.open(output_path) as src:
        image = src.read(1)
        bounds = src.bounds

    # Warna klasifikasi
    kelas_warna = {
        1: "#66c2a5",  # Vegetatif Awal
        2: "#fc8d62",  # Vegetatif Akhir
        3: "#8da0cb",  # Reproduktif Awal
        4: "#e78ac3",  # Reproduktif Akhir
        5: "#a6d854"   # Bukan lahan jagung
    }

    def klasifikasi_to_rgb(image, colormap):
        rgb_img = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
        for val, hex_color in colormap.items():
            mask = image == val
            rgba = tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (150,)
            rgb_img[mask] = rgba
        return rgb_img

    rgb_image = klasifikasi_to_rgb(image, kelas_warna)

    temp_img = "temp_overlay.png"
    plt.imsave(temp_img, rgb_image)

    # === Buat peta dengan basemap Google Satellite ===
    center = [(bounds.top + bounds.bottom) / 2, (bounds.left + bounds.right) / 2]
    m = folium.Map(location=center, zoom_start=12)

    # Tambah Google Satellite Layer
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
