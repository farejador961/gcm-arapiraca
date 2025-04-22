import streamlit as st
import os
import base64
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Módulos GCM", layout="wide")
st.title("📘 Módulos de Estudo da Guarda Municipal de Arapiraca")

MODULOS_DIR = "modulos_pdf"
EXCEL_FILENAME = "Plano_Estudos_Semanal_GCM.xlsx"
REPO_URL_BASE = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/main/modulos_pdf"  # Ajuste com seu repositório

# ───────────────────────────────
# EXIBE O PLANO DE ESTUDOS
# ───────────────────────────────
excel_path = os.path.join(MODULOS_DIR, EXCEL_FILENAME)
if os.path.exists(excel_path):
    st.subheader("📅 Plano de Estudos Semanal")
    df = pd.read_excel(excel_path)
    st.dataframe(df, use_container_width=True)
    with open(excel_path, "rb") as f:
        st.download_button(
            "⬇️ Baixar Plano de Estudos (Excel)",
            data=f,
            file_name=EXCEL_FILENAME,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning(f"Arquivo '{EXCEL_FILENAME}' não encontrado em '{MODULOS_DIR}'.")

st.markdown("---")

# ───────────────────────────────
# EXIBE OS MÓDULOS EM PDF
# ───────────────────────────────
if not os.path.exists(MODULOS_DIR):
    st.error("❌ Pasta 'modulos_pdf' não encontrada.")
else:
    pdf_files = sorted([f for f in os.listdir(MODULOS_DIR) if f.endswith(".pdf")])

    if not pdf_files:
        st.info("⚠️ Nenhum PDF disponível ainda.")
    else:
        for pdf_file in pdf_files:
            st.markdown(f"### 📄 {pdf_file.replace('_', ' ').replace('.pdf', '')}")

            pdf_path = os.path.join(MODULOS_DIR, pdf_file)
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
                base64_pdf = base64.b64encode(pdf_data).decode("utf-8")

            # Botão para download
            st.download_button(
                label="⬇️ Baixar PDF",
                data=pdf_data,
                file_name=pdf_file,
                mime="application/pdf"
            )

            # Link para visualizar online
            pdf_url = f"{REPO_URL_BASE}/{urllib.parse.quote(pdf_file)}"
            st.markdown(
                f'<a href="{pdf_url}" target="_blank">'
                f'<button style="background-color:#4CAF50;color:white;border:none;padding:8px 16px;border-radius:5px;">👁️ Visualizar Online</button>'
                f'</a>',
                unsafe_allow_html=True
            )

            # Visualizador via iframe + base64
            pdf_viewer = f"""
                <iframe 
                    src="data:application/pdf;base64,{base64_pdf}"
                    width="100%" height="800px"
                    style="border: 1px solid #ccc; border-radius: 6px;">
                </iframe>
            """
            st.markdown(pdf_viewer, unsafe_allow_html=True)
            st.markdown("---")


