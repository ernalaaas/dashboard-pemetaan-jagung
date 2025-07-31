import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import os

# === Konfigurasi halaman
st.set_page_config(layout="wide")
st.title("🌽 Dashboard Pemetaan Fase Tumbuh Jagung")
st.markdown("Pilih bulan klasifikasi untuk ditampilkan sebagai overlay pada peta satelit.")

# === Sidebar
with st.sidebar:
    st.header("Pengaturan")

    bulan_opsi = ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
    bulan_pilihan = st.selectbox("Pilih bulan klasifikasi:", bulan_opsi)
    opacity = st.slider("Transparansi overlay", 0.0, 1.0, 0.6)

# === Path dan bounds
image_path = f"data/{bulan_pilihan}.png"

# Gunakan bounds tetap (dari hasil konversi UTM ke latlon)
image_bounds = [
    [2.867686, 97.870742],  # south, west
    [3.331565, 98.629036]   # north, east
]

# === Cek file dan tampilkan peta
if not os.path.exists(image_path):
    st.error(f"❌ Gambar PNG untuk bulan {bulan_pilihan} tidak ditemukan di: {image_path}")
else:
    # Pusatkan peta di tengah bounds
    center_lat = (image_bounds[0][0] + image_bounds[1][0]) / 2
    center_lon = (image_bounds[0][1] + image_bounds[1][1]) / 2

    # Buat peta
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Basemap: Google Satellite
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite"
    ).add_to(m)

    # Overlay sesuai bulan
    ImageOverlay(
        image=image_path,
        bounds=image_bounds,
        opacity=opacity,
        name=f"Klasifikasi {bulan_pilihan}"
    ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)
