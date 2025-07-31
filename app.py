import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import os
from folium import Element
import json
import geopandas as gpd


# Tambahkan di bagian atas aplikasi setelah import
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# === Tambahkan gambar header (cover)
st.image("data/cover_jagung_crop.jpg", use_container_width=True)

# === Konfigurasi halaman
st.set_page_config(layout="wide")


st.title("🌽 Dashboard Pemetaan Fase Tumbuh Jagung")
st.markdown("""
<div style='text-align: justify;'>
Dashboard ini menyajikan informasi visual tentang fase-fase pertumbuhan jagung di Kabupaten Karo, berdasarkan analisis citra satelit Sentinel-1 dan Sentinel-2.
Mulai dari saat jagung baru tumbuh, hingga mendekati masa panen — semua fase pertumbuhannya ditampilkan dalam bentuk peta klasifikasi yang mudah dipahami.
Tujuannya sederhana: memberikan gambaran yang jelas dan menyeluruh tentang kondisi pertanaman jagung di berbagai wilayah,
baik untuk keperluan pemantauan, evaluasi, maupun perencanaan pertanian.
Nah, sebelum kita lihat petanya, kenalan dulu yuk sama fase-fase pertumbuhan jagung yang dipetakan di sini!
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# === Sidebar
with st.sidebar:
    st.header("🔧 Pengaturan Visualisasi")
    bulan_opsi = ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
    bulan_pilihan = st.selectbox("📅 Pilih Bulan Klasifikasi:", bulan_opsi)
    opacity = st.slider("🌓 Transparansi Layer", 0.0, 1.0, 0.6)


import streamlit as st
import base64

# === Data Kelas ===
kelas_list = [
    "Vegetatif Awal (VA)",
    "Vegetatif Akhir (VR)",
    "Reproduktif Awal (RA)",
    "Reproduktif Akhir (RR)",
    "Bukan Jagung"
]

kelas_opsi = {
    "Vegetatif Awal (VA)": {
        "deskripsi": "Fase Vegetatif Awal dimulai saat daun pertama mulai terlihat, dan berakhir ketika tanaman memiliki sekitar 3 hingga 5 daun yang terbuka sempurna",
        "gambar": ["data/VA.jpg"]
    },
    "Vegetatif Akhir (VR)": {
        "deskripsi": "Fase Vegetatif Akhir dimulai setelah terbentuknya daun ke-6 hingga daun terakhir yang terbuka sempurna (sekitar daun ke-15 hingga ke-18), dan berakhir saat munculnya malai (bunga jantan)",
        "gambar": ["data/VR.jpg"]
    },
    "Reproduktif Awal (RA)": {
        "deskripsi": "Fase Reproduktif Awal ditandai dengan munculnya malai (bunga jantan) di bagian atas tanaman serta keluarnya rambut jagung (bunga betina) dari dalam tongkol yang tertutup kelobot. Fase ini berakhir ketika rambut jagung mulai mengering dan biji memasuki tahap masak susu",
        "gambar": ["data/RA.jpg"]
    },
    "Reproduktif Akhir (RR)": {
        "deskripsi": "Fase Reproduktif Akhir dimulai ketika bagian dalam biji masih bertekstur seperti pasta (belum mengeras), kemudian berlanjut hingga biji mengeras dan tongkol mengering. Rambut jagung semakin kering dan menghitam, hingga seluruh bagian tongkol hampir kering dan siap untuk dipanen",
        "gambar": ["data/RR.jpg"]
    },
    "Bukan Jagung": {
        "deskripsi": "Wilayah yang bukan termasuk area pertanaman jagung, seperti hutan, permukiman, atau sawah",
        "gambar": ["data/BJ1.jpg", "data/BJ2.jpg"]
    }
}

# === Inisialisasi Index ===
if "kelas_index" not in st.session_state:
    st.session_state.kelas_index = 0

# === Layout Utama ===
col1, col2, col3 = st.columns([1, 6, 1])

# === Panah Kiri ===
with col1:
    st.markdown("<div style='padding-top:180px'></div>", unsafe_allow_html=True)
    if st.button("⬅️", use_container_width=True):
        st.session_state.kelas_index = (st.session_state.kelas_index - 1) % len(kelas_list)

# === Konten Tengah ===
with col2:
    kelas = kelas_list[st.session_state.kelas_index]
    data = kelas_opsi[kelas]

    st.markdown(f"<h2 style='text-align:center'>{kelas}</h2>", unsafe_allow_html=True)

    if kelas == "Bukan Jagung":
        col_a, col_b = st.columns(2)
        for i, col in enumerate([col_a, col_b]):
            with col:
                path = data["gambar"][i]
                with open(path, "rb") as f:
                    img_data = f.read()
                    img_base64 = base64.b64encode(img_data).decode("utf-8")
                    img_html = f"""
                        <div style='text-align:center;'>
                            <img src='data:image/png;base64,{img_base64}' style='width:100%; max-width:300px; border-radius:8px; margin:10px auto;'/>
                        </div>
                    """
                    st.markdown(img_html, unsafe_allow_html=True)
    else:
        for path in data["gambar"]:
            with open(path, "rb") as f:
                img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode("utf-8")
                img_html = f"""
                    <div style='text-align:center;'>
                        <img src='data:image/png;base64,{img_base64}' style='width:300px; border-radius:8px; margin:10px auto;'/>
                    </div>
                """
                st.markdown(img_html, unsafe_allow_html=True)

    st.markdown(
        f"<p style='text-align:center; font-size:16px; margin-top:10px;'>{data['deskripsi']}</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<p style='text-align:center; color:gray;'>Kelas {st.session_state.kelas_index + 1} dari {len(kelas_list)}</p>",
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

# === Panah Kanan ===
with col3:
    st.markdown("<div style='padding-top:180px'></div>", unsafe_allow_html=True)
    if st.button("➡️", use_container_width=True):
        st.session_state.kelas_index = (st.session_state.kelas_index + 1) % len(kelas_list)


st.markdown("""
<div style='text-align: justify;'>
Sekarang kamu sudah mengenal setiap fase pertumbuhan jagung yang diamati. 
Lalu, seperti apa sebaran fase-fase ini di wilayah Kabupaten Karo? 
Yuk, kita lihat hasil pemetaannya! Di bawah ini, kamu bisa melihat visualisasi dari 
klasifikasi fase tumbuh jagung berdasarkan citra satelit yang diolah menggunakan model <i>machine learning</i>. 
Peta ini menampilkan lokasi serta perkembangan fase tanaman jagung pada setiap bulan, 
sehingga kamu bisa memantau perubahan secara lebih jelas dan mudah dipahami.
</div>
""", unsafe_allow_html=True)




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
    <span style='display:inline-block; width:15px; height:15px; background-color:#0010ff; margin-right:8px;'></span>Bukan Jagung
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
    # === Tambahkan jarak vertikal
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # === Tampilkan peta di tengah laman
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st_folium(m, width=900, height=600)


st.markdown("""
<div style='text-align: justify;'>
Setelah melihat peta penyebaran fase tumbuh jagung, kita bisa melihat bagaimana kondisi pertanaman jagung berubah setiap bulannya. 
Mulai dari wilayah yang baru ditanami, sampai yang sudah mendekati masa panen, semua tergambarkan secara visual dan mudah dipahami. 
Hal ini tentu sangat membantu petani, penyuluh, hingga pengambil kebijakan dalam menentukan langkah yang tepat di lapangan.
</div>

<br/>

<div style='text-align: justify;'>
Dengan memanfaatkan teknologi penginderaan jauh dan model <i>machine learning</i>, pemantauan pertumbuhan jagung kini bisa dilakukan secara lebih cepat, efisien, dan mencakup area yang luas. 
Semoga dashboard ini bisa menjadi langkah kecil menuju pertanian yang lebih cerdas dan berbasis data. 
Terima kasih sudah menjelajahi dashboard ini — semoga bermanfaat, dan terus dukung pertanian kita tumbuh bersama teknologi!
</div>
""", unsafe_allow_html=True)


