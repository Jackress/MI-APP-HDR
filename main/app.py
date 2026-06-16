import streamlit as st
import sys
import os
import gc  # Recolector de basura para liberar RAM

try:
    import cv2
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python-headless"])
    import cv2

import numpy as np
from PIL import Image

# Configurar Streamlit para que no guarde copias pesadas en caché
st.set_page_config(page_title="Fusionador HDR Automático", layout="centered")

st.title("📸 Fusionador de Fotos HDR")
st.write("Sube fotos en alta resolución para combinarlas sin perder calidad.")

archivos_subidos = st.file_uploader(
    "Selecciona tus imágenes...", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if archivos_subidos and len(archivos_subidos) >= 2:
    st.info(f"Cargando {len(archivos_subidos)} imágenes en alta resolución...")
    
    lista_imagenes = []
    for archivo in archivos_subidos:
        file_bytes = np.asarray(bytearray(archivo.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        lista_imagenes.append(img)
        
        # Liberar memoria de bytes inmediatamente
        del file_bytes
        archivo.close()

    try:
        st.write("🔄 Alineando imágenes (Algoritmo MTB)...")
        alignMTB = cv2.createAlignMTB()
        alignMTB.process(lista_imagenes, lista_imagenes)
        
        st.write("🎨 Fusionando exposiciones a máxima calidad...")
        merge_mertens = cv2.createMergeMertens()
        hdr_mertens = merge_mertens.process(lista_imagenes)
        
        # Limpiar las imágenes base de la RAM ya que tenemos la fusión
        del lista_imagenes
        gc.collect()
        
        st.write("💾 Generando archivo final...")
        hdr_8bit = np.clip(hdr_mertens * 255, 0, 255).astype('uint8')
        del hdr_mertens
        
        hdr_rgb = cv2.cvtColor(hdr_8bit, cv2.COLOR_BGR2RGB)
        del hdr_8bit
        
        imagen_final = Image.fromarray(hdr_rgb)
        
        st.success("¡Listo! Tu imagen HDR combinada:")
        st.image(imagen_final, use_container_width=True)
        
        import io
        buf = io.BytesIO()
        imagen_final.save(buf, format="JPEG", quality=100) # Calidad 100% sin compresión
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 Descargar Imagen HDR Original",
            data=byte_im,
            file_name="resultado_hdr_maxima_calidad.jpg",
            mime="image/jpeg"
        )
        
        del byte_im
        buf.close()
        gc.collect()
        
    except Exception as e:
        st.error(f"Hubo un error de memoria o procesamiento: {e}")
        gc.collect()
        
elif archivos_subidos:
    st.warning("Por favor, sube al menos 2 imágenes para poder realizar la fusión HDR.")
