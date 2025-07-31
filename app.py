import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import os
from folium import Element


# === Tambahkan di bagian paling atas, sebelum st.title()
st.image("data/cover_jagung_crop.jpg", use_container_width=True)

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

# === Path gambar dan koordinat bounds
image_path = f"data/{bulan_pilihan}.png"
image_bounds = [
    [2.867686, 97.870742],  # south, west
    [3.331565, 98.629036]   # north, east
]

# === Tampilkan peta jika file tersedia
if not os.path.exists(image_path):
    st.error(f"❌ Gambar klasifikasi untuk bulan {bulan_pilihan} tidak ditemukan di path: {image_path}")
else:
    center_lat = (image_bounds[0][0] + image_bounds[1][0]) / 2
    center_lon = (image_bounds[0][1] + image_bounds[1][1]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite"
    ).add_to(m)

    ImageOverlay(
        image=image_path,
        bounds=image_bounds,
        opacity=opacity,
        name=f"Klasifikasi {bulan_pilihan}"
    ).add_to(m)

    # LEGEND: Selalu tampil (tanpa checkbox)
    legend_html = """
    <div style="
        position: absolute; 
        bottom: 20px; left: 20px; width: 240px; z-index:9999;
        background-color: white; padding: 10px; border:1px solid #ccc;
        font-size: 14px; color: #000;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        border-radius: 5px;
    ">
    <b>Legenda:</b><br>
    <div style="margin-top:5px;">
    <span style='display:inline-block; width:15px; height:15px; background-color:#009c00; margin-right:8px;'></span>Vegetatif Awal (VA)<br>
    <span style='display:inline-block; width:15px; height:15px; background-color:#cdbb5d; margin-right:8px;'></span>Vegetatif Akhir (VR)<br>
    <span style='display:inline-block; width:15px; height:15px; background-color:#ffef00; margin-right:8px;'></span>Reproduktif Awal (RA)<br>
    <span style='display:inline-block; width:15px; height:15px; background-color:#ff4400; margin-right:8px;'></span>Reproduktif Akhir (RR)<br>
    <span style='display:inline-block; width:15px; height:15px; background-color:#0010ff; margin-right:8px;'></span>Bukan Lahan Jagung
    </div>
    </div>
    """
    m.get_root().html.add_child(Element(legend_html))

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)
