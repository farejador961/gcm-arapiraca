import streamlit as st
import os
import base64
import pandas as pd

st.set_page_config(page_title="Módulos GCM", layout="wide")
st.title("📘 Módulos de Estudo da Guarda Municipal de Arapiraca")

# Caminho para os arquivos
MODULOS_DIR = "modulos_pdf"
EXCEL_FILENAME = "Plano_Estudos_Semanal_GCM.xlsx"

# ──────────────────────────────────────────────
# VISUALIZAÇÃO DO PLANO DE ESTUDOS SEMANAL
# ──────────────────────────────────────────────
excel_path = os.path.join(MODULOS_DIR, EXCEL_FILENAME)
if os.path.exists(excel_path):
    st.subheader("📅 Plano de Estudos Semanal")
    
    df = pd.read_excel(excel_path)
    st.dataframe(df, use_container_width=True)

    with open(excel_path, "rb") as f:
        excel_bytes = f.read()
        st.download_button(
            label="⬇️ Baixar Plano de Estudos (Excel)",
            data=excel_bytes,
            file_name=EXCEL_FILENAME,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning(f"⚠️ Arquivo {EXCEL_FILENAME} não encontrado em `{MODULOS_DIR}`.")

st.markdown("---")

# ──────────────────────────────────────────────
# VISUALIZAÇÃO DOS MÓDULOS EM PDF
# ──────────────────────────────────────────────
if not os.path.exists(MODULOS_DIR):
    st.error("❌ Pasta 'modulos_pdf' não encontrada.")
else:
    pdf_files = sorted([f for f in os.listdir(MODULOS_DIR) if f.endswith(".pdf")])

    if not pdf_files:
        st.info("⚠️ Nenhum PDF disponível ainda.")
    else:
        for pdf_file in pdf_files:
            pdf_path = os.path.join(MODULOS_DIR, pdf_file)
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()

            base64_pdf = base64.b64encode(pdf_data).decode("utf-8")

            st.markdown(f"### 📄 {pdf_file.replace('_', ' ').replace('.pdf', '')}")
            st.download_button(
                label="⬇️ Baixar PDF",
                data=pdf_data,
                file_name=pdf_file,
                mime="application/pdf"
            )

            pdf_display = f"""
            <iframe
                src="data:application/pdf;base64,{base64_pdf}"
                width="100%"
                height="700"
                type="application/pdf"
                style="border: 1px solid #ccc; border-radius: 8px;"
            ></iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.markdown("---")

