import os
import requests
import pdfplumber
from io import BytesIO
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import nltk
import streamlit as st

# Baixar recursos do NLTK
nltk.download("punkt")
nltk.download("stopwords")
nltk.data.path.append("nltk_data")


# Diretório para uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="Extrator de Resumo Inteligente", layout="centered")

st.title("📄 Extrator de Resumo Inteligente de PDF")
st.image("dados/Mayke.png", width=150)
st.markdown("Resuma seu PDF por URL ou upload local com seleção de páginas e foco em conteúdo relevante!")

# Função de resumo

def summarize_text(text, num_sentences=3):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum() and word not in stopwords.words("portuguese")]
    freq = FreqDist(words)
    ranked_sentences = sorted(
        sentences,
        key=lambda s: sum(freq[word] for word in word_tokenize(s.lower()) if word in freq),
        reverse=True,
    )
    return " ".join(ranked_sentences[:num_sentences])

# Função para extrair texto com seleção de páginas

def extract_text_from_pdf(pdf_file, pages_to_include=None, pages_to_exclude=None):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            included_pages = set(range(total_pages))

            if pages_to_include:
                included_pages = set(pages_to_include)
            if pages_to_exclude:
                included_pages -= set(pages_to_exclude)

            text = ""
            for i in sorted(included_pages):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"

            return text
    except Exception as e:
        return f"❌ Erro ao extrair texto: {e}"

# Extrai texto de PDF remoto

def extract_text_from_url(url, pages_to_include=None, pages_to_exclude=None):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            return extract_text_from_pdf(pdf, pages_to_include, pages_to_exclude)
    except Exception as e:
        return f"❌ Erro ao processar URL: {e}"

# Interface Streamlit

with st.form("resumo_form"):
    st.subheader("🔢 Escolha o número de sentenças para o resumo")
    num_sentences = st.slider("Quantas sentenças deseja no resumo?", 1, 50, 10)

    st.subheader("📄 Defina intervalo de páginas (opcional)")
    pagina_inicio = st.number_input("Página inicial (começando do 1)", min_value=1, value=1)
    pagina_fim = st.number_input("Página final", min_value=1, value=1)
    pular_paginas = st.text_input("Páginas a pular (separadas por vírgula)", "")

    st.subheader("🌐 Ou cole o link de um PDF (URL)")
    pdf_url = st.text_input("URL do PDF")

    st.subheader("📁 Ou envie um arquivo PDF")
    uploaded_file = st.file_uploader("Selecione um PDF", type=["pdf"])

    submitted = st.form_submit_button("Gerar Resumo")

if submitted:
    with st.spinner("🔎 Processando..."):
        pages_to_include = list(range(pagina_inicio - 1, pagina_fim)) if pagina_fim >= pagina_inicio else None
        pages_to_exclude = [int(p.strip()) - 1 for p in pular_paginas.split(",") if p.strip().isdigit()] if pular_paginas else []

        if pdf_url:
            text = extract_text_from_url(pdf_url, pages_to_include, pages_to_exclude)
            if not text.startswith("❌"):
                summary = summarize_text(text, num_sentences)
                st.success("Resumo gerado com sucesso a partir da URL:")
                st.write(summary)
            else:
                st.error(text)

        elif uploaded_file:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            text = extract_text_from_pdf(file_path, pages_to_include, pages_to_exclude)
            if not text.startswith("❌"):
                summary = summarize_text(text, num_sentences)
                st.success("Resumo gerado com sucesso a partir do arquivo:")
                st.write(summary)
            else:
                st.error(text)
        else:
            st.warning("Por favor, forneça uma URL ou envie um arquivo PDF.")






#Link de site para acessar os resumos
# http://127.0.0.1:5000/

'''

Estatuto da Guarda Municipal: https://noticias.jaulacursos.com.br/wp-content/uploads/sites/23/2024/03/GCM-ARAPIRACA_JAULA-CURSOS.pdf
código de postura: https://web.arapiraca.al.gov.br/wp-content/uploads/2019/03/2180.pdf 


'''


