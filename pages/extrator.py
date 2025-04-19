import os
import requests
import pdfplumber
from io import BytesIO
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import nltk
import streamlit as st

# Baixar os recursos do NLTK se necessário
nltk.download("punkt")
nltk.download("stopwords")

# Diretório para uploads locais
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="Extrator de Resumo", layout="centered")

st.title("📄 Extrator de Resumo de PDF")
st.image("dados/Maike.png", width=150)
st.markdown("Resuma um PDF por **URL** ou **upload local**. Ideal para estudar com foco!")

# Função de resumo
def summarize_text(text, num_sentences=3):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    words = [
        word for word in words if word.isalnum() and word not in stopwords.words("portuguese")
    ]
    freq = FreqDist(words)
    ranked_sentences = sorted(
        sentences,
        key=lambda s: sum(freq[word] for word in word_tokenize(s.lower()) if word in freq),
        reverse=True,
    )
    return " ".join(ranked_sentences[:num_sentences])

# Extrai texto de PDF remoto
def summarize_pdf_from_url(url, num_sentences=3):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)
        return summarize_text(text, num_sentences)
    except Exception as e:
        return f"❌ Erro: {e}"

# Extrai texto de PDF local
def summarize_pdf_from_file(file_path, num_sentences=3):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)
        return summarize_text(text, num_sentences)
    except Exception as e:
        return f"❌ Erro ao processar o arquivo: {e}"

# Interface Streamlit
with st.form("resumo_form"):
    st.subheader("🔢 Escolha o número de sentenças")
    num_sentences = st.slider("Quantas sentenças deseja no resumo?", 1, 10, 3)

    st.subheader("🌐 Ou cole o link de um PDF (URL)")
    pdf_url = st.text_input("URL do PDF")

    st.subheader("📁 Ou envie um arquivo PDF")
    uploaded_file = st.file_uploader("Selecione um PDF", type=["pdf"])

    submitted = st.form_submit_button("Gerar Resumo")

if submitted:
    with st.spinner("🔎 Processando..."):
        if pdf_url:
            summary = summarize_pdf_from_url(pdf_url, num_sentences)
            st.success("Resumo gerado com sucesso a partir da URL:")
            st.write(summary)

        elif uploaded_file:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            summary = summarize_pdf_from_file(file_path, num_sentences)
            st.success("Resumo gerado com sucesso a partir do arquivo:")
            st.write(summary)
        else:
            st.warning("Por favor, forneça uma URL ou envie um arquivo PDF.")





#Link de site para acessar os resumos
# http://127.0.0.1:5000/

'''

Estatuto da Guarda Municipal: https://noticias.jaulacursos.com.br/wp-content/uploads/sites/23/2024/03/GCM-ARAPIRACA_JAULA-CURSOS.pdf
código de postura: https://web.arapiraca.al.gov.br/wp-content/uploads/2019/03/2180.pdf 


'''


