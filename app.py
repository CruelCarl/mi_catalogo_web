.*

# --- Interfaz Streamlit ---
st.title("🛠️ MI CATÁLOGO")

uploaded_excel = st.file_uploader("📤 Sube tu archivo Excel (Código, Descripción, Precio)", type=["xlsx"])
logo_file = st.file_uploader("🖼️ Sube el logo de la empresa", type=["png", "jpg", "jpeg"])
imagenes_cargadas = st.file_uploader("📸 Sube imágenes de productos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("🧹 Limpiar imágenes y logotipo"):
    shutil.rmtree("mi_catalogo/imagenes", ignore_errors=True)
    os.makedirs("mi_catalogo/imagenes", exist_ok=True)
    for ext in ["png", "jpg", "jpeg"]:
        for archivo in [f"logo_empresa.{ext}", f"portada_temp.{ext}"]:
            try:
                os.remove(archivo)
            except FileNotFoundError:
                pass
    st.success("Archivos eliminados correctamente")

if uploaded_excel:
    try:
        df = pd.read_excel(uploaded_excel, engine="openpyxl")
        df.columns = [col.strip().capitalize().replace("ó", "o") for col in df.columns]
        st.dataframe(df)

        if imagenes_cargadas:
            codigos_validos = set(df['Codigo'].astype(str))
            imagenes_validas = []
            nombres_invalidos = []

            for imagen in imagenes_cargadas:
                nombre_base = os.path.splitext(imagen.name)[0]
                if nombre_base in codigos_validos:
                    save_path = os.path.join("mi_catalogo/imagenes", f"{nombre_base}.jpg")
                    with open(save_path, "wb") as f:
                        f.write(imagen.getbuffer())
                    imagenes_validas.append(nombre_base)
                else:
                    nombres_invalidos.append(imagen.name)

            faltantes = codigos_validos - set(imagenes_validas)

            st.success(f"✅ {len(imagenes_validas)} imágenes guardadas correctamente.")
            if nombres_invalidos:
                st.warning("⚠️ Las siguientes imágenes no coinciden con ningún código del Excel:")
                st.write(nombres_invalidos)
            if faltantes:
                st.info("ℹ️ Los siguientes productos aún no tienen imagen:")
                st.write(sorted(faltantes))

        if logo_file:
            ext = logo_file.name.split(".")[-1].lower()
            with open(f"logo_empresa.{ext}", "wb") as f:
                f.write(logo_file.getbuffer())

        if st.button("🖨️ Generar PDF"):
            pdf_file = generar_pdf_estilo_original(df)
            with open(pdf_file, "rb") as f:
                st.download_button("📄 Descargar catálogo PDF", f.read(), file_name=pdf_file, mime="application/pdf")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
