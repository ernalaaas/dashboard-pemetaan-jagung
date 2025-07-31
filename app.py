import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import os

# === Konfigurasi halaman
st.set_page_config(layout="wide")
st.title("🌽 Dashboard Pemetaan Fase Tumbuh Jagung")
st.markdown("""
Dashboard ini menampilkan peta klasifikasi fase tumbuh jagung berbasis citra satelit di Kabupaten Karo.
Pilih bulan klasifikasi untuk menampilkan perbedaan fase pertumbuhan dari waktu ke waktu.
""")

# === Sidebar
with st.sidebar:
    st.header("🔧 Pengaturan Visualisasi")

    bulan_opsi = ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
    bulan_pilihan = st.selectbox("📅 Pilih Bulan Klasifikasi:", bulan_opsi)

    opacity = st.slider("🌓 Transparansi Layer", 0.0, 1.0, 0.6)

    show_legend = st.checkbox("📌 Tampilkan Legenda", True)

# === Path gambar klasifikasi dan koordinat geospasial (hasil konversi UTM → lat-lon WGS84)
image_path = f"data/{bulan_pilihan}.png"
image_bounds = [
    [2.867686, 97.870742],  # south, west
    [3.331565, 98.629036]   # north, east
]

# === Cek dan tampilkan peta
if not os.path.exists(image_path):
    st.error(f"❌ Gambar klasifikasi untuk bulan {bulan_pilihan} tidak ditemukan di path: {image_path}")
else:
    # Titik tengah peta
    center_lat = (image_bounds[0][0] + image_bounds[1][0]) / 2
    center_lon = (image_bounds[0][1] + image_bounds[1][1]) / 2

    # Inisialisasi peta
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Tambah layer Google Satellite
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite"
    ).add_to(m)

    # Overlay gambar klasifikasi
    ImageOverlay(
        image=image_path,
        bounds=image_bounds,
        opacity=opacity,
        name=f"Klasifikasi {bulan_pilihan}"
    ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)

    # === Legenda warna klasifikasi
    if show_legend:
        st.markdown("""
        <div style='background-color: white; padding: 10px; border:1px solid #ccc; width:300px'>
        <b>Legenda Kelas Fase Tumbuh:</b><br>
        <span style='background-color:#009c00; padding:4px 10px; margin-right:5px'></span> Vegetatif Awal (VA)<br>
        <span style='background-color:#cdbb5d; padding:4px 10px; margin-right:5px'></span> Vegetatif Akhir (VR)<br>
        <span style='background-color:#ffef00; padding:4px 10px; margin-right:5px'></span> Reproduktif Awal (RA)<br>
        <span style='background-color:#ff4400; padding:4px 10px; margin-right:5px'></span> Reproduktif Akhir (RR)<br>
        <span style='background-color:#0010ff; padding:4px 10px; margin-right:5px'></span> Bukan Lahan Jagung
        </div>
        """, unsafe_allow_html=True)
