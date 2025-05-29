import os
import shutil
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import hashlib
import socket

# --- Verificar si estamos en local o en la nube ---
IS_LOCAL = socket.gethostname() != 'localhost'

# --- Crear carpetas necesarias ---
if not os.path.exists('mi_catalogo/imagenes'):
    os.makedirs('mi_catalogo/imagenes')

# --- Función para calcular hash único de la portada ---
def calcular_hash_portada(titulo, fondo_color, texto_color, texto_secundario, fuente, tam_titulo, tam_pie, pos_titulo, incluir_logo, logo_pos=None, logo_tam=None, usar_fondo=False, formas=[]):
    base = f"{titulo}|{fondo_color}|{texto_color}|{texto_secundario}|{fuente}|{tam_titulo}|{tam_pie}|{pos_titulo}|{incluir_logo}"
    if incluir_logo and logo_pos and logo_tam:
        base += f"|{logo_pos}|{logo_tam}"
    if usar_fondo:
        base += "|fondo"
    for f in formas:
        base += f"|{f['tipo']},{f['color']},{f['opacidad']},{f['x']},{f['y']},{f['w']},{f['h']},{f['solo_borde']}"
    return hashlib.md5(base.encode()).hexdigest()

# --- Interfaz de carga de archivos ---
st.set_page_config(layout="wide")
st.title("🛠️ MI CATÁLOGO")
st.markdown("<div style='text-align:right; font-size:12px; color:gray;'>📄 Creado por Carlos Ricaurte</div>", unsafe_allow_html=True)

# --- Menú lateral para navegación ---
pagina = st.sidebar.radio("Selecciona una sección:", ["Cargar archivos", "Diseñar portada"])

if pagina == "Cargar archivos":
    with st.expander("📤 Subir archivos para el catálogo"):
        uploaded_excel = st.file_uploader("Sube tu archivo Excel (Código, Descripción, Precio)", type=['xlsx'])
        logo_file = st.file_uploader("Sube el logo de la empresa (opcional)", type=['png', 'jpg'])
        imagenes_cargadas = st.file_uploader("Sube imágenes de productos (JPG)", type=["jpg"], accept_multiple_files=True)

        if imagenes_cargadas:
            codigos_excel = set()
            if uploaded_excel:
                try:
                    df_temp = pd.read_excel(uploaded_excel, engine='openpyxl')
                    codigos_excel = set(df_temp['Codigo'].astype(str))
                except:
                    pass

            imagenes_guardadas = []
            nombres_invalidos = []

            if not os.path.exists("mi_catalogo/imagenes"):
                os.makedirs("mi_catalogo/imagenes")

            for imagen in imagenes_cargadas:
                nombre_base = os.path.splitext(imagen.name)[0]
                if not codigos_excel or nombre_base in codigos_excel:
                    save_path = os.path.join("mi_catalogo", "imagenes", imagen.name)
                    with open(save_path, "wb") as f:
                        f.write(imagen.getbuffer())
                    imagenes_guardadas.append(nombre_base)
                else:
                    nombres_invalidos.append(imagen.name)

            st.success(f"✅ {len(imagenes_guardadas)} imágenes guardadas correctamente.")
            if nombres_invalidos:
                st.warning("⚠️ Las siguientes imágenes no coinciden con ningún código del Excel:")
                st.write(nombres_invalidos)

            if uploaded_excel:
                codigos_faltantes = codigos_excel - set(imagenes_guardadas)
                if codigos_faltantes:
                    st.info("ℹ️ Los siguientes productos aún no tienen imagen:")
                    st.write(sorted(codigos_faltantes))

        if logo_file:
            for ext in ['png', 'jpg', 'jpeg']:
                try:
                    os.remove(f"logo_empresa.{ext}")
                except FileNotFoundError:
                    pass
            logo_ext = logo_file.name.split('.')[-1].lower()
            image = Image.open(logo_file)
            save_path = f"logo_empresa.{logo_ext}"
            image.save(save_path)
            st.success("✅ Logotipo guardado correctamente.")

        st.markdown("---")
        if st.button("🧹 Limpiar imágenes y logotipo"):
            try:
                shutil.rmtree("mi_catalogo/imagenes")
                os.makedirs("mi_catalogo/imagenes")
                for ext in ['png', 'jpg', 'jpeg']:
                    try:
                        os.remove(f"logo_empresa.{ext}")
                    except FileNotFoundError:
                        pass
                st.success("🧼 Imágenes y logotipo eliminados correctamente.")
            except Exception as e:
                st.warning("⚠️ No se pudo limpiar completamente. Puede que algunas carpetas no existan todavía.")

        if uploaded_excel:
            try:
                df = pd.read_excel(uploaded_excel, engine='openpyxl')
                df.columns = [col.strip().capitalize().replace("ó", "o") for col in df.columns]
                st.dataframe(df)
            except Exception as e:
                st.error("❌ Error al leer el archivo Excel. Asegúrate de que el archivo sea válido.")

if pagina == "Diseñar portada":
    from portada_editor import mostrar_editor_portada
    mostrar_editor_portada()

st.markdown("---")
st.write("✅ Módulo de carga de archivos restaurado. ¿Avanzamos ahora con el editor visual de la portada?")
