import os
import shutil
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

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
    import streamlit as st
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    from streamlit.runtime.state import session_state
    import time
    st.experimental_rerun = lambda: None
    last_inputs = st.session_state.get("_portada_input_hash", None)
    # --- Personalización de portada (completo sin perder avances anteriores) ---
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
    def calcular_hash_portada():
        base = f"{portada_titulo}|{portada_color_fondo}|{portada_color_texto}|{portada_texto_secundario}|{portada_familia_fuente}|{portada_tamano_titulo}|{portada_tamano_pie}|{portada_posicion_titulo}|{incluir_logo_en_portada}"
        if incluir_logo_en_portada:
            base += f"|{logo_posicion}|{logo_tamano}"
        if subir_fondo:
            base += "|fondo"
        for f in formas:
            base += f"|{f['tipo']},{f['color']},{f['opacidad']},{f['x']},{f['y']},{f['w']},{f['h']},{f['solo_borde']}"
        return hashlib.md5(base.encode()).hexdigest()

    current_hash = calcular_hash_portada() + ('-manual' if actualizar_manual else '')
    if st.session_state.get("_portada_input_hash") != current_hash or not os.path.exists(portada_temp_path):
        st.session_state["_portada_input_hash"] = current_hash

        if portada_fondo_file:
            img = Image.open(portada_fondo_file).convert("RGB")
            img = img.resize((3508, 2480))
        else:
            img = Image.new('RGB', (3508, 2480), color=portada_color_fondo)

        if formas:
            shape_overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            shape_draw = ImageDraw.Draw(shape_overlay)
            for f in formas:
                fill_color = f["color"] + f"{f['opacidad']:02x}"
                x0, y0, x1, y1 = f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]
                if f["tipo"] == "Rectángulo":
                    if f.get("solo_borde"):
                        shape_draw.rectangle([x0, y0, x1, y1], outline=f["color"], width=4)
                    else:
                        shape_draw.rectangle([x0, y0, x1, y1], fill=fill_color)
                elif f["tipo"] == "Círculo":
                    if f.get("solo_borde"):
                        shape_draw.ellipse([x0, y0, x1, y1], outline=f["color"], width=4)
                    else:
                        shape_draw.ellipse([x0, y0, x1, y1], fill=fill_color)
            img = Image.alpha_composite(img.convert("RGBA"), shape_overlay).convert("RGB")

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
        # Insertar logotipo si está activado
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

        import hashlib
    input_hash = hashlib.md5((portada_titulo + portada_color_fondo + portada_color_texto + portada_texto_secundario + portada_familia_fuente + str(portada_tamano_titulo) + str(portada_tamano_pie)).encode()).hexdigest()
    if st.session_state.get("_portada_input_hash") != input_hash:
        st.session_state["_portada_input_hash"] = input_hash
        img.save(portada_temp_path)
    else:
        if not os.path.exists(portada_temp_path):
            img.save(portada_temp_path)

    # --- Vista previa en Streamlit ---
    st.subheader("👁️ Vista previa de la portada")
    st.image(portada_temp_path, use_container_width=True)

    

# --- Clase PDF y generación del catálogo ---
from fpdf import FPDF

class OfertaPDF(FPDF):
    def __init__(self):
        super().__init__('L', 'mm', 'A4')
        self.set_auto_page_break(auto=False)
        self.add_page()

    def draw_portada(self):
        for ext in ['jpg', 'jpeg', 'png']:
            if os.path.exists(f'portada_temp.{ext}'):
                self.image(f'portada_temp.{ext}', x=0, y=0, w=297)
                break
        self.ln(20)

    def draw_title(self):
        self.set_font("Arial", 'B', 28)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        self.rect(10, 10, 135, 15, 'F')
        self.rect(145, 10, 135, 15, 'F')
        self.set_xy(10, 10)
        self.cell(135, 15, "OFERTA", 0, 0, 'C')
        self.set_xy(145, 10)
        self.cell(135, 15, "OFERTA", 0, 0, 'C')
        self.ln(20)

    def draw_price_tag(self, x, y, price):
        self.set_fill_color(200, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 12)
        self.set_xy(x, y)
        self.cell(26, 10, f"${price}", border=0, ln=0, align='C', fill=True)
        self.set_text_color(0, 0, 0)

    def draw_product_block(self, x, y, img_path, code, desc, price):
        if os.path.exists(img_path):
            self.image(img_path, x + 2, y + 2, w=38, h=38)
        else:
            self.set_fill_color(255, 200, 200)
            self.rect(x + 2, y + 2, 38, 38, 'F')
            self.set_font("Arial", '', 6)
            self.set_xy(x + 2, y + 20)
            self.multi_cell(38, 3, "Imagen no encontrada", align='C')

        self.draw_price_tag(x + 14, y + 2, price)
        self.set_font("Arial", 'B', 10)
        self.set_xy(x, y + 42)
        self.cell(42, 5, code, 0, 2, 'C')
        self.set_font("Arial", '', 8)
        self.set_xy(x, y + 47)
        desc_text = desc.upper()[:85] + ('...' if len(desc) > 85 else '')
        wrapped_lines = self.multi_cell(42, 4, desc_text, align='C', split_only=True)
        limited_text = "\n".join(wrapped_lines[:2])
        self.multi_cell(42, 4, limited_text, align='C')

    def draw_logo(self):
        for ext in ['png', 'jpg', 'jpeg']:
            path = f'logo_empresa.{ext}'
            if os.path.exists(path):
                self.image(path, x=245, y=193, w=30, type=ext)
                break


if pagina == "Generar catálogo":
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

    if uploaded_excel:
        try:
            df = pd.read_excel(uploaded_excel, engine='openpyxl')
            df.columns = [col.strip().capitalize().replace("ó", "o") for col in df.columns]
            st.dataframe(df)
            if st.button("🖨️ Generar PDF estilo catálogo original"):
                pdf_file = generar_pdf_estilo_original(df)
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 Descargar PDF generado", f.read(), file_name=pdf_file, mime='application/pdf')
        except Exception as e:
            st.error("❌ Error al leer el archivo Excel. Asegúrate de que el archivo sea un .xlsx válido y no esté dañado.")

def generar_pdf_estilo_original(datos, salida="catalogo_estilo_original.pdf"):
    pdf = OfertaPDF()
    pdf.draw_portada()
    pdf.draw_title()
    start_x = 25
    start_y = 20
    cols = 4
    spacing_x = 65
    spacing_y = 70

    for i, row in datos.iterrows():
        col = i % cols
        row_pos = (i // cols) % 3
        if i > 0 and i % 12 == 0:
            pdf.add_page()
            pdf.draw_title()
            pdf.draw_logo()
        x = start_x + col * spacing_x
        y = start_y + row_pos * spacing_y
        if row_pos == 0:
            y += 5
        elif row_pos == 1:
            y -= 10
        elif row_pos == 2:
            y -= 20
        img_path = f"mi_catalogo/imagenes/{row['Codigo']}.jpg"
        pdf.draw_product_block(x, y, img_path, row['Codigo'], row['Descripcion'], row['Precio'])

    pdf.draw_logo()
    pdf.output(salida)
    return salida

