import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Fusionador HDR Automático", layout="centered")

st.title("📸 Fusionador de Fotos HDR")
st.write("Sube 2 o más fotos tomadas con diferentes exposiciones (oscura, normal, clara) para combinarlas en una sola.")

# Selector de archivos en la interfaz web
archivos_subidos = st.file_uploader(
    "Selecciona tus imágenes...", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if archivos_subidos and len(archivos_subidos) >= 2:
    st.info(f"Procesando {len(archivos_subidos)} imágenes...")
    
    # 1. Convertir imágenes subidas al formato que entiende OpenCV
    lista_imagenes = []
    for archivo in archivos_subidos:
        file_bytes = np.asarray(bytearray(archivo.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        lista_imagenes.append(img)
    
    try:
        # 2. Alineación automática de imágenes (por si se movió la mano)
        st.write("🔄 Alineando imágenes...")
        alignMTB = cv2.createAlignMTB()
        alignMTB.process(lista_imagenes, lista_imagenes)
        
        # 3. Fusión de exposición usando el algoritmo Mertens
        # Este algoritmo no necesita los tiempos de exposición exactos (metadatos EXIF)
        st.write("🎨 Fusionando exposiciones...")
        merge_mertens = cv2.createMergeMertens()
        hdr_mertens = merge_mertens.process(lista_imagenes)
        
        # 4. Post-procesamiento (OpenCV procesa en flotantes de 0 a 1, hay que pasarlo a 8-bits)
        hdr_8bit = np.clip(hdr_mertens * 255, 0, 255).astype('uint8')
        
        # 5. Convertir de BGR (OpenCV) a RGB (Streamlit/Pillow)
        hdr_rgb = cv2.cvtColor(hdr_8bit, cv2.COLOR_BGR2RGB)
        imagen_final = Image.fromarray(hdr_rgb)
        
        # Mostrar resultado
        st.success("¡Listo! Tu imagen HDR combinada:")
        st.image(imagen_final, use_container_width=True)
        
        # Botón para descargar el resultado
        # Guardamos temporalmente en memoria para la descarga
        import io
        buf = io.BytesIO()
        imagen_final.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 Descargar Imagen HDR",
            data=byte_im,
            file_name="resultado_hdr.jpg",
            mime="image/jpeg"
        )
        
    except Exception as e:
        st.error(f"Hubo un error al procesar las imágenes: {e}")
        
elif archivos_subidos:
    st.warning("Por favor, sube al menos 2 imágenes para poder realizar la fusión HDR.")