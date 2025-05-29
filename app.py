import os
import shutil
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# --- Ruta temporal para la portada ---
portada_temp_path = "portada_temp.jpg"

# --- Menú de navegación ---
pagina = st.sidebar.radio("Selecciona una sección:", ["Inicio", "Diseñar portada", "Generar catálogo"])

if pagina == "Inicio":
    st.title("🛠️ MI CATÁLOGO")
    st.markdown("""
    Bienvenido a la herramienta para crear tu catálogo personalizado.

    Desde aquí puedes:
    - 📄 Cargar tu archivo Excel
    - 📸 Subir imágenes de productos
    - 🖼️ Agregar tu logotipo
    - 🎨 Personalizar la portada
    - 🖨️ Generar un catálogo en PDF

    Usa el menú lateral para empezar.
    """)

elif pagina == "Diseñar portada":
    # --- Personalización de portada ---
    st.sidebar.markdown("---")
    subir_fondo = st.sidebar.checkbox("¿Deseas usar una imagen de fondo?")
    portada_fondo_file = None
    if subir_fondo:
        portada_fondo_file = st.sidebar.file_uploader("Sube la imagen de fondo (JPG o PNG, tamaño ideal: 3508x2480 px)", type=["jpg", "png"])

    st.sidebar.header("🎨 Personaliza tu portada")
    portada_titulo = st.sidebar.text_input("Texto principal", "Quincenazo")
    portada_color_fondo = st.sidebar.color_picker("Color de fondo", "#FFDD00")
    portada_color_texto = st.sidebar.color_picker("Color del texto", "#FF0000")
    portada_texto_secundario = st.sidebar.text_input("Texto inferior", "www.comercial-jaramillo.com - Asesoría, Respaldo y Garantía")
    portada_tamano_titulo = st.sidebar.slider("Tamaño del título", 10, 300, 200)
    portada_tamano_pie = st.sidebar.slider("Tamaño del texto inferior", 10, 150, 60)
    portada_familia_fuente = st.sidebar.selectbox("Tipo de letra", ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Comic_Sans_MS.ttf", "times.ttf", "Verdana.ttf"])
    portada_posicion_titulo = st.sidebar.selectbox("Ubicación del título", ["Superior", "Centro", "Inferior"])
    actualizar_manual = st.sidebar.button("🔁 Refrescar portada manualmente")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🖼️ Logotipo en portada")
    incluir_logo_en_portada = st.sidebar.checkbox("Incluir logotipo en portada")
    if incluir_logo_en_portada:
        logo_posicion = st.sidebar.selectbox("Ubicación del logotipo", ["Izquierda", "Centro", "Derecha"])
        logo_tamano = st.sidebar.slider("Tamaño del logotipo (% del ancho)", 5, 50, 15)

    # --- Generar imagen de portada personalizada ---
    import hashlib
    formas = st.session_state.get("formas", [])

    def calcular_hash_portada(titulo, fondo_color, texto_color, texto_secundario, fuente, tam_titulo, tam_pie, pos_titulo, incluir_logo, logo_pos=None, logo_tam=None, usar_fondo=False, formas=[]):
        base = f"{titulo}|{fondo_color}|{texto_color}|{texto_secundario}|{fuente}|{tam_titulo}|{tam_pie}|{pos_titulo}|{incluir_logo}"
        if incluir_logo and logo_pos and logo_tam:
            base += f"|{logo_pos}|{logo_tam}"
        if usar_fondo:
            base += "|fondo"
        for f in formas:
            base += f"|{f['tipo']},{f['color']},{f['opacidad']},{f['x']},{f['y']},{f['w']},{f['h']},{f['solo_borde']}"
        return hashlib.md5(base.encode()).hexdigest()

    current_hash = calcular_hash_portada(
        portada_titulo, portada_color_fondo, portada_color_texto,
        portada_texto_secundario, portada_familia_fuente,
        portada_tamano_titulo, portada_tamano_pie,
        portada_posicion_titulo,
        incluir_logo_en_portada,
        logo_posicion if incluir_logo_en_portada else None,
        logo_tamano if incluir_logo_en_portada else None,
        subir_fondo,
        formas
    ) + ('-manual' if actualizar_manual else '')

    if st.session_state.get("_portada_input_hash") != current_hash or not os.path.exists(portada_temp_path):
        st.session_state["_portada_input_hash"] = current_hash

        if portada_fondo_file:
            img = Image.open(portada_fondo_file).convert("RGB")
            img = img.resize((3508, 2480))
        else:
            img = Image.new('RGB', (3508, 2480), color=portada_color_fondo)

        draw = ImageDraw.Draw(img)
        try:
            font_title = ImageFont.truetype(portada_familia_fuente, portada_tamano_titulo)
            font_footer = ImageFont.truetype(portada_familia_fuente, portada_tamano_pie)
        except:
            font_title = ImageFont.load_default()
            font_footer = ImageFont.load_default()

        txt_w, txt_h = draw.textbbox((0, 0), portada_titulo, font=font_title)[2:]
        footer_w, _ = draw.textbbox((0, 0), portada_texto_secundario, font=font_footer)[2:]
        if portada_posicion_titulo == "Superior":
            titulo_y = 400
        elif portada_posicion_titulo == "Centro":
            titulo_y = 900
        else:
            titulo_y = 1500
        draw.text(((3508 - txt_w) / 2, titulo_y), portada_titulo, fill=portada_color_texto, font=font_title)
        draw.text(((3508 - footer_w) / 2, 2300), portada_texto_secundario, fill="white", font=font_footer)

        if incluir_logo_en_portada:
            for ext in ['png', 'jpg', 'jpeg']:
                logo_path = f"logo_empresa.{ext}"
                if os.path.exists(logo_path):
                    logo = Image.open(logo_path).convert("RGBA")
                    max_width = int((logo_tamano / 100) * img.width)
                    aspect_ratio = logo.height / logo.width
                    new_size = (max_width, int(max_width * aspect_ratio))
                    logo = logo.resize(new_size)
                    x_pos = 0 if logo_posicion == "Izquierda" else (img.width - logo.width) // 2 if logo_posicion == "Centro" else img.width - logo.width
                    y_pos = 100
                    img.paste(logo, (x_pos, y_pos), logo)
                    break

        img.save(portada_temp_path)

    st.subheader("👁️ Vista previa de la portada")
    st.image(portada_temp_path, use_container_width=True)

elif pagina == "Generar catálogo":
    st.header("📄 Generación de catálogo")

    uploaded_excel = st.file_uploader("📤 Sube tu archivo Excel (Código, Descripción, Precio)", type=['xlsx'])
    logo_file = st.file_uploader("🖼️ Sube el logo de la empresa (opcional)", type=['png', 'jpg'])
    imagenes_cargadas = st.file_uploader("📸 Sube imágenes de productos (JPG)", type=["jpg"], accept_multiple_files=True)

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



