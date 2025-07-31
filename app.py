import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import os
from folium import Element
import json
import geopandas as gpd

# === Tambahkan gambar header (cover)
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


st.markdown("### 🗂️ Penjelasan Kelas Fase Tumbuh Jagung")

# === Data
kelas_list = [
    "Vegetatif Awal (VA)",
    "Vegetatif Akhir (VR)",
    "Reproduktif Awal (RA)",
    "Reproduktif Akhir (RR)",
    "Bukan Lahan Jagung"
]

kelas_opsi = {
    "Vegetatif Awal (VA)": {
        "deskripsi": "Jagung baru mulai tumbuh, daun masih sedikit, berwarna hijau segar.",
        "gambar": ["data/VA.jpg"]
    },
    "Vegetatif Akhir (VR)": {
        "deskripsi": "Daun jagung sudah lebat, tanaman tumbuh cepat dan tinggi.",
        "gambar": ["data/VR.jpg"]
    },
    "Reproduktif Awal (RA)": {
        "deskripsi": "Fase awal pembentukan bunga jantan dan betina, tongkol mulai muncul.",
        "gambar": ["data/RA.jpg"]
    },
    "Reproduktif Akhir (RR)": {
        "deskripsi": "Tongkol jagung membesar dan mengisi, tanaman mendekati masa panen.",
        "gambar": ["data/RR.jpg"]
    },
    "Bukan Lahan Jagung": {
        "deskripsi": "Wilayah yang bukan termasuk area pertanaman jagung, seperti hutan, permukiman, atau sawah.",
        "gambar": ["data/BJ1.jpg", "data/BJ2.jpg"]
    }
}

# Inisialisasi state
if "kelas_index" not in st.session_state:
    st.session_state.kelas_index = 0

# Layout dengan 3 kolom: kiri (tombol) - tengah (konten) - kanan (tombol)
col_kiri, col_tengah, col_kanan = st.columns([1, 6, 1])

# Tombol kiri
with col_kiri:
    st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)  # spacer
    if st.button("⬅️", key="prev", use_container_width=True):
        st.session_state.kelas_index = (st.session_state.kelas_index - 1) % len(kelas_list)

# Konten tengah
kelas_dipilih = kelas_list[st.session_state.kelas_index]
with col_tengah:
    st.markdown(f"<h4 style='text-align:center'>{kelas_dipilih}</h4>", unsafe_allow_html=True)

    gambar_list = kelas_opsi[kelas_dipilih]["gambar"]
    col_gbr = st.columns(len(gambar_list))
    for i, path in enumerate(gambar_list):
        with col_gbr[i]:
            st.image(path, width=150)

    st.markdown(
        f"<p style='text-align:center; margin-top:10px; font-size:15px; color:#444;'>"
        f"{kelas_opsi[kelas_dipilih]['deskripsi']}</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<p style='text-align:center; font-size:13px; color:gray;'>Kelas {st.session_state.kelas_index + 1} dari {len(kelas_list)}</p>",
        unsafe_allow_html=True
    )

# Tombol kanan
with col_kanan:
    st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)  # spacer
    if st.button("➡️", key="next", use_container_width=True):
        st.session_state.kelas_index = (st.session_state.kelas_index + 1) % len(kelas_list)




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

    # === Tambah batas kecamatan (GeoJSON)
    geojson_path = "data/kecamatanSHP.geojson"
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    
        folium.GeoJson(
            geojson_data,
            name="Batas Kecamatan",
            style_function=lambda x: {
                "fillOpacity": 0,
                "color": "black",
                "weight": 0.5
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["NAMOBJ"],  # sesuaikan dengan nama kolom kecamatan di file .shp/.geojson
                aliases=["Kecamatan:"],
                localize=True,
                sticky=True,
                direction="top",
                opacity=0.9,
                permanent=False
            )
        ).add_to(m)

    
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
