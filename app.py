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
st.markdown("Peta hasil klasifikasi fase tumbuh jagung di Kabupaten Karo.")

# === Sidebar ===
with st.sidebar:
    st.header("Pengaturan")
    opacity = st.slider("Opacity layer", 0.0, 1.0, 0.6)

# === Unduh dari Google Drive jika belum ada lokal ===
# Ganti file_id ini dengan ID dari link Drive kamu
#2024-07
file_id = "19gAUxtX8kmCrdQypFF46UqiEWXtLLyEG"  # <== GANTI dengan ID milikmu
output_path = "data/hasil_klasifikasi.tif"

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(output_path):
    st.info("⏳ Mengunduh raster klasifikasi dari Google Drive...")
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)

# === Tampilkan raster jika file tersedia ===
if os.path.exists(output_path):
    with rasterio.open(output_path) as src:
        image = src.read(1)
        bounds = src.bounds
        transform = src.transform

    # Warna klasifikasi
    kelas_warna = {
        1: "#66c2a5",  # Vegetatif Awal
        2: "#fc8d62",  # Vegetatif Akhir
        3: "#8da0cb",  # Reproduktif Awal
        4: "#e78ac3",  # Reproduktif Akhir
        5: "#a6d854"   # Bukan lahan jagung
    }

    # Konversi klasifikasi ke RGB
    def klasifikasi_to_rgb(image, colormap):
        rgb_img = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
        for val, hex_color in colormap.items():
            mask = image == val
            rgba = tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (150,)
            rgb_img[mask] = rgba
        return rgb_img

    rgb_image = klasifikasi_to_rgb(image, kelas_warna)

    # Simpan sementara ke PNG
    temp_img = "temp_overlay.png"
    plt.imsave(temp_img, rgb_image)

    # Buat peta
    center = [(bounds.top + bounds.bottom) / 2, (bounds.left + bounds.right) / 2]
    m = folium.Map(location=center, zoom_start=11)
    image_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

    raster_layers.ImageOverlay(
        image=temp_img,
        bounds=image_bounds,
        opacity=opacity,
        name="Peta Klasifikasi"
    ).add_to(m)

    # Legenda manual
    legend_html = """
    <div style="position: fixed; 
                bottom: 20px; left: 20px; width: 220px; height: 150px; 
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

    st_data = st_folium(m, width=1000, height=600)
else:
    st.warning("❌ Gagal menampilkan peta. Pastikan file `.tif` berhasil diunduh atau ID Drive benar.")
