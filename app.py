import os
import shutil
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import random
import socket

# --- Verificar si estamos en local o en la nube ---
IS_LOCAL = socket.gethostname() != 'localhost'

# --- Crear carpetas necesarias ---
if not os.path.exists('mi_catalogo/imagenes'):
    os.makedirs('mi_catalogo/imagenes')

# --- Solo crear datos de prueba si estamos en local ---
if IS_LOCAL:
    excel_path = 'ejemplo_catalogo.xlsx'
    productos = [
        "Martillo reforzado",
        "Destornillador plano",
        "Taladro DeWalt inalámbrico DCD996",
        "Llave inglesa",
        "Serrucho manual",
        "Alicate universal",
        "Amoladora inalámbrica Bosch GSB180 LI 123456",
        "Nivel de burbuja",
        "Brochas 2 pulgadas",
        "Flexómetro profesional",
        "Tubo PVC 1/2",
        "Guantes de seguridad"
    ]
    codigos = [f"A{str(i+1).zfill(3)}" for i in range(12)]
    precios = [round(random.uniform(20, 200), 2) for _ in range(12)]
    df = pd.DataFrame({
        'Codigo': codigos,
        'Descripcion': productos,
        'Precio': precios
    })
    df.to_excel(excel_path, index=False)

    colores = ['lightblue', 'lightgreen', 'lightcoral', 'khaki', 'lavender', 'salmon', 'lightgray', 'plum', 'peachpuff', 'aquamarine', 'thistle', 'mistyrose']
    for codigo, color in zip(codigos, colores):
        img_path = f'mi_catalogo/imagenes/{codigo}.jpg'
        img = Image.new('RGB', (200, 200), color=color)
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        text = codigo
        bbox = d.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((200 - w) / 2, (200 - h) / 2), text, fill='black', font=font)
        img.save(img_path)

# --- Clase PDF con estilo original ---
class OfertaPDF(FPDF):
    def __init__(self):
        super().__init__('L', 'mm', 'A4')
        self.set_auto_page_break(auto=False)
        self.add_page()

    def draw_portada(self):
        for ext in ['jpg', 'png', 'jpeg']:
            if os.path.exists(f"portada.{ext}"):
                self.image(f"portada.{ext}", x=0, y=0, w=297, h=210)
                break
        self.set_font("Arial", 'B', 50)
        self.set_text_color(255, 0, 0)
        self.set_xy(0, 80)
        self.cell(297, 20, "Quincenazo", align='C')
        self.set_font("Arial", '', 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 195)
        self.cell(0, 10, "www.comercial-jaramillo.com   -   Asesoría, Respaldo y Garantía", align='C')

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

def generar_pdf_estilo_original(datos, salida="catalogo_estilo_original.pdf"):
    pdf = OfertaPDF()
    pdf.draw_portada()
    pdf.add_page()
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

# --- Interfaz Streamlit ---
st.title("🛠️ MI CATÁLOGO")

uploaded_excel = st.file_uploader("📤 Sube tu archivo Excel (Código, Descripción, Precio)", type=["xlsx"])
logo_file = st.file_uploader("🖼️ Sube el logo de la empresa", type=["png", "jpg", "jpeg"])
portada_file = st.file_uploader("🌄 Sube una imagen de portada", type=["png", "jpg", "jpeg"])
imagenes_cargadas = st.file_uploader("📸 Sube imágenes de productos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("🧹 Limpiar imágenes y logotipo"):
    shutil.rmtree("mi_catalogo/imagenes", ignore_errors=True)
    os.makedirs("mi_catalogo/imagenes", exist_ok=True)
    for ext in ["png", "jpg", "jpeg"]:
        for archivo in [f"logo_empresa.{ext}", f"portada.{ext}"]:
            try:
                os.remove(archivo)
            except FileNotFoundError:
                pass
    st.success("Archivos eliminados correctamente")

if imagenes_cargadas:
    for imagen in imagenes_cargadas:
        nombre = os.path.splitext(imagen.name)[0]
        save_path = os.path.join("mi_catalogo/imagenes", f"{nombre}.jpg")
        with open(save_path, "wb") as f:
            f.write(imagen.getbuffer())

if logo_file:
    ext = logo_file.name.split(".")[-1].lower()
    with open(f"logo_empresa.{ext}", "wb") as f:
        f.write(logo_file.getbuffer())

if portada_file:
    ext = portada_file.name.split(".")[-1].lower()
    with open(f"portada.{ext}", "wb") as f:
        f.write(portada_file.getbuffer())

if uploaded_excel:
    try:
        df = pd.read_excel(uploaded_excel, engine="openpyxl")
        df.columns = [col.strip().capitalize().replace("ó", "o") for col in df.columns]
        st.dataframe(df)
        if st.button("🖨️ Generar PDF"):
            pdf_file = generar_pdf_estilo_original(df)
            with open(pdf_file, "rb") as f:
                st.download_button("📄 Descargar catálogo PDF", f.read(), file_name=pdf_file, mime="application/pdf")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")


