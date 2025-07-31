import streamlit as st
import folium
import numpy as np
import rasterio
from folium import raster_layers
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import os
import gdown

# === Konfigurasi halaman ===
st.set_page_config(layout="wide")
st.title("Dashboard Pemetaan Fase Tumbuh Jagung 🌽")
st.markdown("**Basemap:** Google Satellite | **Overlay:** Hasil klasifikasi fase tumbuh jagung")

# === Sidebar ===
with st.sidebar:
    st.header("Pengaturan")
    opacity = st.slider("Transparansi layer klasifikasi", 0.0, 1.0, 0.6)
    uploaded_file = st.file_uploader("Upload file .tif hasil klasifikasi", type=["tif"])

# === Unduh raster dari Google Drive jika belum ada ===
file_id = "19gAUxtX8kmCrdQypFF46UqiEWXtLLyEG"  # Ganti dengan ID kamu
default_path = "data/hasil_klasifikasi.tif"

if not os.path.exists("data"):
    os.makedirs("data")

if uploaded_file:
    with open(default_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ File berhasil diunggah dan digunakan.")
elif not os.path.exists(default_path):
    st.info("⏳ Mengunduh file dari Google Drive...")
    gdown.download(f"https://drive.google.com/uc?id={file_id}", default_path, quiet=False)
    st.success("✅ Unduhan selesai.")
else:
    st.info("📂 Menggunakan file lokal yang sudah ada.")

# === Fungsi bantu: konversi klasifikasi ke RGBA ===
def klasifikasi_to_rgb(image, colormap):
    rgb_img = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
    for val, hex_color in colormap.items():
        mask = image == val
        rgba = tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (150,)
        rgb_img[mask] = rgba
    return rgb_img

# === Proses file raster dan tampilkan di peta ===
if os.path.exists(default_path):
    with rasterio.open(default_path) as src:
        image = src.read(1)
        bounds = src.bounds

    kelas_warna = {
        1: "#66c2a5",  # Vegetatif Awal
        2: "#fc8d62",  # Vegetatif Akhir
        3: "#8da0cb",  # Reproduktif Awal
        4: "#e78ac3",  # Reproduktif Akhir
        5: "#a6d854"   # Bukan lahan jagung
    }

    rgb_image = klasifikasi_to_rgb(image, kelas_warna)
    temp_img = "temp_overlay.png"
    plt.imsave(temp_img, rgb_image)

    # Lokasi tengah peta
    center = [(bounds.top + bounds.bottom) / 2, (bounds.left + bounds.right) / 2]
    m = folium.Map(location=center, zoom_start=12)

    # Basemap Google Satellite
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite",
        overlay=False,
        control=True
    ).add_to(m)

    # Overlay raster klasifikasi
    image_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
    raster_layers.ImageOverlay(
        image=temp_img,
        bounds=image_bounds,
        opacity=opacity,
        name="Klasifikasi Fase Tumbuh"
    ).add_to(m)

    # Legenda
    legend_html = """
    <div style="position: fixed; 
                bottom: 20px; left: 20px; width: 240px; height: 160px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid gray; padding:10px;">
    <b>Legenda Kelas:</b><br>
    <i style="background:#66c2a5;width:12px;height:12px;display:inline-block;"></i> Vegetatif Awal<br>
    <i style="background:#fc8d62;width:12px;height:12px;display:inline-block;"></i> Vegetatif Akhir<br>
    <i style="background:#8da0cb;width:12px;height:12px;display:inline-block;"></i> Reproduktif Awal<br>
    <i style="background:#e78ac3;width:12px;height:12px;display:inline-block;"></i> Reproduktif Akhir<br>
    <i style="background:#a6d854;width:12px;height:12px;display:inline-block;"></i> Bukan Lahan Jagung<br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)
else:
    st.error("❌ File raster belum ditemukan.")
