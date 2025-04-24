import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO

# Config inicial
st.set_page_config(layout="wide", page_title="Painel de Leitura")

# Estado inicial
if "page_number" not in st.session_state:
    st.session_state.page_number = 1
if "fullscreen" not in st.session_state:
    st.session_state.fullscreen = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "rerun_flag" not in st.session_state:
    st.session_state.rerun_flag = False

# Alternância de tema
theme_color = "#111" if st.session_state.dark_mode else "#fdfdfd"
text_color = "#eee" if st.session_state.dark_mode else "#222"

# Estilo dinâmico com base no tema
st.markdown(f"""
<style>
    .texto-pagina {{
        text-align: justify;
        font-size: 18px;
        line-height: 1.6;
        background-color: {theme_color};
        padding: 20px;
        border-radius: 12px;
        color: {text_color};
    }}
    .botao-flutuante {{
        position: fixed;
        bottom: 40px;
        right: 40px;
        background-color: #2e86de;
        color: white;
        padding: 12px 16px;
        border-radius: 50px;
        font-size: 16px;
        cursor: pointer;
        z-index: 9999;
    }}
    .fullscreen {{
        position: fixed;
        top: 0; left: 0;
        right: 0; bottom: 0;
        background-color: {theme_color};
        padding: 30px;
        overflow-y: scroll;
        z-index: 999;
        color: {text_color};
    }}
</style>
""", unsafe_allow_html=True)

# Título e upload
st.title("📖 Painel de Leitura com Modo Noturno & Marcações")

uploaded_file = st.file_uploader("📤 Faça upload do PDF", type="pdf")

# Muda página
def muda_pagina(delta):
    st.session_state.page_number = max(1, min(st.session_state.page_number + delta, st.session_state.total_pages))

# Modo tela cheia sem erro
if st.session_state.rerun_flag:
    st.session_state.fullscreen = True
    st.session_state.rerun_flag = False

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.session_state.total_pages = len(doc)
    page = doc[st.session_state.page_number - 1]
    text = page.get_text("text")

    # Tela cheia
    if st.session_state.fullscreen:
        st.markdown("<div class='fullscreen'>", unsafe_allow_html=True)
        st.markdown(f"<div class='texto-pagina'>{text}</div>", unsafe_allow_html=True)
        if st.button("❌ Sair do modo tela cheia"):
            st.session_state.fullscreen = False
        st.stop()

    # Navegação
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("⬅️"):
            muda_pagina(-1)
    with col2:
        st.markdown(f"<center><b>Página {st.session_state.page_number} de {len(doc)}</b></center>", unsafe_allow_html=True)
    with col3:
        if st.button("➡️"):
            muda_pagina(1)

    # Texto da página
    st.markdown("### 📄 Conteúdo da Página")
    st.markdown(f"<div class='texto-pagina'>{text}</div>", unsafe_allow_html=True)

    # Botão para ativar opções
    with st.popover("⚙️ Ações"):
        selection = st.text_input("🔎 Trecho a destacar")
        color = st.color_picker("🎨 Cor do destaque", "#ffff00")
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
                            highlight.set_info(info={"title": "Comentário", "subject": annotation})
                    st.success("✅ Marcação aplicada!")
                else:
                    st.error("⚠️ Trecho não encontrado.")
            else:
                st.warning("⚠️ Insira o texto a marcar.")

    # Lista de marcações na página
    st.markdown("### 🗂️ Marcações nesta página")
    annotations = page.annots()
    if annotations:
        for annot in annotations:
            info = annot.info
            st.write(f"🔸 **Tipo**: {annot.type[1]} | **Comentário**: {info.get('subject', '')}")
    else:
        st.info("Nenhuma marcação nesta página.")

    # Botões diversos
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("💾 Salvar PDF com anotações"):
            buffer = BytesIO()
            doc.save(buffer)
            st.download_button("⬇️ Baixar PDF", buffer.getvalue(), file_name="pdf_com_anotacoes.pdf")
    with colB:
        if st.button("🖥️ Entrar em modo tela cheia"):
            st.session_state.rerun_flag = True
            st.rerun()
    with colC:
        if st.button("🌗 Alternar tema"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.experimental_rerun()

    # Botão flutuante de ações
    st.markdown("<div class='botao-flutuante' onclick='document.querySelector(\"details\").open = true;'>⚙️</div>", unsafe_allow_html=True)



