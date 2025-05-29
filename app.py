import os
import shutil
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# --- Personalización de portada (completo sin perder avances anteriores) ---
st.sidebar.markdown("---")
subir_fondo = st.sidebar.checkbox("¿Deseas usar una imagen de fondo?")
portada_fondo_file = None
if subir_fondo:
    portada_fondo_file = st.sidebar.file_uploader("Sube la imagen de fondo (JPG o PNG, tamaño ideal: 3508x2480 px)", type=["jpg", "png"])

import matplotlib.font_manager as fm


st.sidebar.header("🎨 Personaliza tu portada")
portada_titulo = st.sidebar.text_input("Texto principal", "Quincenazo")
portada_color_fondo = st.sidebar.color_picker("Color de fondo", "#FFDD00")
portada_color_texto = st.sidebar.color_picker("Color del texto", "#FF0000")
portada_texto_secundario = st.sidebar.text_input("Texto inferior", "www.comercial-jaramillo.com - Asesoría, Respaldo y Garantía")
portada_tamano_titulo = st.sidebar.slider("Tamaño del título", min_value=50, max_value=300, value=200)
portada_tamano_pie = st.sidebar.slider("Tamaño del texto inferior", min_value=30, max_value=100, value=60)
portada_familia_fuente = st.sidebar.selectbox("Tipo de letra", ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"])
portada_posicion_titulo = st.sidebar.selectbox("Ubicación del título", ["Superior", "Centro", "Inferior"])

# --- Generar imagen de portada personalizada ---
portada_temp_path = "portada_temp.jpg"
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

# Posición dinámica del título
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
img.save(portada_temp_path)

# --- Vista previa en Streamlit ---
st.subheader("👁️ Vista previa de la portada")
st.image(portada_temp_path, use_column_width=True)

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
