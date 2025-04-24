import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📖 Painel de Leitura com Anotações e Marcações")

# Upload do PDF
uploaded_file = st.file_uploader("📤 Faça upload do PDF", type="pdf")
if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Escolher página
    page_number = st.slider("📄 Página", 1, len(doc), 1)
    page = doc[page_number - 1]

    # Exibir texto da página
    text = page.get_text("text")
    st.markdown("### 📜 Texto da Página:")
    st.markdown(f"<div style='text-align: justify; font-size: 16px;'>{text}</div>", unsafe_allow_html=True)

    # Seção de marcação
    st.markdown("### ✏️ Adicionar marcação")
    selection = st.text_input("🔎 Trecho a destacar (copie do texto acima)")
    color = st.color_picker("🎨 Escolha a cor do destaque", "#ffff00")
    annotation = st.text_area("📝 Comentário (opcional)")

    if st.button("➕ Aplicar marcação"):
        if selection:
            text_instances = page.search_for(selection)
            if text_instances:
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=color)
                    highlight.update()
                    if annotation:
                        highlight.set_info(info={"title": "Anotação", "subject": annotation})
                st.success("✅ Marcação aplicada!")
            else:
                st.error("⚠️ Trecho não encontrado na página.")
        else:
            st.warning("⚠️ Digite um trecho para marcar.")

    # Botão para salvar PDF anotado
    if st.button("📥 Salvar PDF com anotações"):
        new_pdf = BytesIO()
        doc.save(new_pdf)
        st.download_button("⬇️ Baixar PDF anotado", new_pdf.getvalue(), file_name="pdf_com_anotacoes.pdf")

