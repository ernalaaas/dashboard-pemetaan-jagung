import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import os
from folium import Element

# === Tambahkan gambar header (cover)
st.image("data/cover_jagung_crop.jpg", use_container_width=True)

# === Konfigurasi halaman
st.set_page_config(layout="wide")
st.markdown("""
<style>
    /* === DASAR UMUM === */
    html, body, .main {
        background-color: #fdf9e6 !important;  /* Latar belakang konten utama */
        color: #2c2c2c;
    }

    .block-container {
        background-color: #fdf9e6 !important;
        padding-top: 1rem;
    }

    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background-color: #b6b565 !important;  /* Lebih gelap dan hijau tua */
        color: #1e1e1e !important;
    }

    header[data-testid="stHeader"] {
        background-color: #b6b565 !important;
        border-bottom: 1px solid #a3a357;
        color: #1e1e1e !important;
    }

    /* Top bar kanan */
    header[data-testid="stHeader"] * {
        color: #1e1e1e !important;
    }

    /* === TEKS & LABEL DI SIDEBAR === */
    .st-emotion-cache-1v0mbdj, 
    .st-emotion-cache-10trblm, 
    label, .stSelectbox label {
        color: #222 !important;
        font-weight: 600;
    }

    /* === SLIDER (warna track & thumb) === */
    .stSlider > div[data-baseweb="slider"] > div {
        background: #8c861f !important;  /* track */
    }
    .stSlider .css-1aumxhk {  /* slider value text */
        color: #2d2d1e !important;
    }

    /* === TOMBOL JIKA ADA === */
    .stButton>button {
        background-color: #8a8426 !important;
        color: white !important;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #b3ad3c !important;
    }

    /* === TEKS UMUM DAN JUDUL === */
    h1, h2, h3, h4 {
        color: #4b4a23 !important;
    }

    .stMarkdown, .css-1cpxqw2, .stText {
        color: #2f2f1e !important;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #8c861f;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)



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

# === Pemetaan nama bulan ke bahasa Indonesia
bulan_dict = {
    "01": "Januari", "02": "Februari", "03": "Maret", "04": "April",
    "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus",
    "09": "September", "10": "Oktober", "11": "November", "12": "Desember"
}
tahun, kode_bulan = bulan_pilihan.split("-")
nama_bulan_indo = bulan_dict[kode_bulan]

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

    # Basemap
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite"
    ).add_to(m)

    # Overlay klasifikasi
    ImageOverlay(
        image=image_path,
        bounds=image_bounds,
        opacity=opacity,
        name=f"Klasifikasi {bulan_pilihan}"
    ).add_to(m)

    # === Legenda warna
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

    # === Judul peta di bawah tengah
    judul_peta_html = f"""
    <div style="
        position: absolute;
        bottom: 50px; left: 50%; transform: translateX(-50%);
        z-index: 9999;
        background-color: #ffffffee;
        padding: 10px 24px;
        border: 2px solid #666;
        font-size: 16px;
        border-radius: 6px;
        font-weight: bold;
        color: #333;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    ">
    📍 Pemetaan Fase Tumbuh Jagung {nama_bulan_indo} {tahun}
    </div>
    """

    m.get_root().html.add_child(Element(judul_peta_html))

    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=600)
