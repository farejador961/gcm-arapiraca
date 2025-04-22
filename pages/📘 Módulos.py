import streamlit as st
import os
import base64

st.set_page_config(page_title="Módulos de Estudo", layout="wide")
st.title("📘 Módulos de Estudo - GCM Arapiraca")

# Caminho relativo à raiz do projeto
MODULOS_DIR = "modulos_pdf"

if not os.path.isdir(MODULOS_DIR):
    st.error("❌ A pasta 'modulos_pdf' não foi encontrada na raiz do projeto.")
else:
    pdf_files = sorted([f for f in os.listdir(MODULOS_DIR) if f.endswith(".pdf")])

    if not pdf_files:
        st.info("Nenhum módulo PDF disponível ainda.")
    else:
        for pdf_file in pdf_files:
            pdf_path = os.path.join(MODULOS_DIR, pdf_file)
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()

            st.subheader(f"📄 {pdf_file.replace('_', ' ').replace('.pdf', '')}")

            # Botão para download
            st.download_button(
                label="⬇️ Baixar PDF",
                data=pdf_data,
                file_name=pdf_file,
                mime="application/pdf"
            )

            # Visualização embutida
            base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.markdown("---")
