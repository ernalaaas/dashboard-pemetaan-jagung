import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import rasterio
from folium.raster_layers import ImageOverlay
from rasterio.enums import Resampling
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import os
import requests

st.set_page_config(layout="wide")
st.title("Dashboard Pemetaan Fase Tumbuh Jagung 🌽")
st.markdown("Basemap: Google Satellite | Overlay: Hasil klasifikasi fase tumbuh jagung")

# === Sidebar ===
with st.sidebar:
    st.header("Pengaturan")
    opacity = st.slider("Transparansi layer klasifikasi", 0.0, 1.0, 0.6)
    uploaded_file = st.file_uploader("Upload file raster (.tif)", type=["tif", "tiff"])

# === Unduh file dari Google Drive jika belum tersedia ===
file_id = "19gAUxtX8kmCrdQypFF46UqiEWXtLLyEG"
default_path = "data/hasil_klasifikasi.tif"
os.makedirs("data", exist_ok=True)

if not os.path.exists(default_path):
    with st.spinner("📥 Mengunduh file raster dari Google Drive..."):
        url = f"https://drive.google.com/uc?id={file_id}"
        r = requests.get(url)
        with open(default_path, "wb") as f:
            f.write(r.content)

# === Fungsi: ubah array ke RGB dari colormap
def array_to_rgb(array):
    cmap = cm.get_cmap("tab10", int(np.max(array)))
    rgba = cmap(array / np.max(array))
    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
    return rgb

# === Baca raster dari upload atau default ===
try:
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
    m = folium.Map(location=[(bounds.top + bounds.bottom)/2, (bounds.left + bounds.right)/2],
                   zoom_start=11)

    # === Tambahkan basemap Google Satellite
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    # === Overlay klasifikasi
    ImageOverlay(
        image=rgb_image,
        bounds=extent,
        opacity=opacity,
        name="Hasil Klasifikasi"
    ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)

except Exception as e:
    st.error(f"❌ Gagal menampilkan peta: {e}")
