import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import rasterio
from folium.raster_layers import ImageOverlay
from rasterio.enums import Resampling
import matplotlib.cm as cm

st.set_page_config(layout="wide")
st.title("🌽 Dashboard Pemetaan Fase Tumbuh Jagung")
st.markdown("Silakan unggah file raster klasifikasi fase tumbuh jagung (.tif)")

# === Sidebar upload
with st.sidebar:
    st.header("Pengaturan")
    opacity = st.slider("Transparansi layer klasifikasi", 0.0, 1.0, 0.6)
    uploaded_file = st.file_uploader("Upload file raster klasifikasi (.tif)", type=["tif", "tiff"])

# === Fungsi konversi raster ke RGB
def array_to_rgb(array):
    max_val = np.max(array)
    if max_val == 0:
        st.warning("⚠️ Raster hanya berisi nilai 0.")
        array = np.ones_like(array)
        max_val = 1
    cmap = cm.get_cmap("tab10", int(max_val + 1))
    rgba = cmap(array / max_val)
    return (rgba[:, :, :3] * 255).astype(np.uint8)

# === Baca dan tampilkan raster jika ada
if uploaded_file is not None:
    try:
        with rasterio.open(uploaded_file) as src:
            data = src.read(1, resampling=Resampling.nearest)
            bounds = src.bounds
            extent = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
            rgb_image = array_to_rgb(data)

            center = [(bounds.top + bounds.bottom) / 2, (bounds.left + bounds.right) / 2]
            m = folium.Map(location=center, zoom_start=11)

            # Google Satellite basemap
            folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                attr="Google",
                name="Google Satellite",
                overlay=False,
                control=True
            ).add_to(m)

            ImageOverlay(
                image=rgb_image,
                bounds=extent,
                opacity=opacity,
                name="Klasifikasi Jagung"
            ).add_to(m)

            folium.LayerControl().add_to(m)
            st_folium(m, width=1000, height=600)

    except Exception as e:
        st.error(f"❌ Gagal membaca file raster: {e}")
else:
    st.info("📤 Silakan unggah file raster untuk mulai menampilkan peta.")
