import streamlit as st
import pdfplumber
import requests
from io import BytesIO
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import random
import pandas as pd
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import random
from nltk.tokenize import sent_tokenize

# Baixar recursos do NLTK
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

# Configurações da página
st.set_page_config(page_title="Gerador de Questões", layout="wide")
st.title("📝 Gerador de Questões Dinâmicas")
st.image("dados/Maike.png", width=150)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Geração inteligente de questões ---

def extrair_texto(pdf_stream):
    texto = ""
    with pdfplumber.open(pdf_stream) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                texto += t + "\n"
    return texto


def gerar_questoes_interpretativas(texto, n, modulo_label):
    sentencas = sent_tokenize(texto)
    questoes = []

    # Organiza as sentenças por importância com TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentencas)
    pontuacoes = X.sum(axis=1).flatten().tolist()[0]
    sentencas_pontuadas = sorted(zip(sentencas, pontuacoes), key=lambda x: x[1], reverse=True)

    usadas = set()

    for i, (sentenca_base, _) in enumerate(sentencas_pontuadas):
        if sentenca_base in usadas or len(sentenca_base.split()) < 8:
            continue

        # Alternativa correta
        correta = sentenca_base.strip()
        usadas.add(correta)

        # Geração de alternativas incorretas
        alternativas = [correta]
        tentativas = 0
        while len(alternativas) < 4 and tentativas < 15:
            alternativa_falsa = random.choice(sentencas)
            if alternativa_falsa != correta and alternativa_falsa not in alternativas and len(alternativa_falsa.split()) >= 8:
                alternativas.append(alternativa_falsa.strip())
            tentativas += 1

        if len(alternativas) < 4:
            continue  # pula se não conseguir 4 opções

        random.shuffle(alternativas)

        questoes.append({
            "texto": "Com base no texto, qual das alternativas está correta?",
            "opcoes": alternativas,
            "correta": correta,
            "modulo": modulo_label
        })

        if len(questoes) >= n:
            break

    return questoes

# Processamento ao clicar em Gerar
if "gerar" not in st.session_state:
    st.session_state.gerar = False

with st.form("form_gerador"):
    uploaded = st.file_uploader("📁 PDFs", type="pdf", accept_multiple_files=True)
    urls = st.text_area("📄 URLs de PDFs (uma por linha)")
    qtds = st.text_input("Quantas questões por fonte? (vírgula)", "5,5")
    if st.form_submit_button("🔎 Gerar Questões"):
        st.session_state.gerar = True
        # extrair, gerar e armazenar perguntas
        st.session_state.perguntas = []
        num_list = [int(x) for x in qtds.split(",") if x.strip().isdigit()]
        idx = 0
        for pdf in uploaded:
            label = pdf.name
            path = os.path.join(UPLOAD_FOLDER, f"{label}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
            with open(path, "wb") as f: f.write(pdf.getvalue())
            txt = extrair_texto(path)
            st.session_state.perguntas += gerar_questoes_interpretativas(txt, num_list[idx] if idx < len(num_list) else 5, label)
            idx += 1
        for u in urls.splitlines():
            if not u.strip(): continue
            r = requests.get(u.strip())
            r.raise_for_status()
            txt = extrair_texto(BytesIO(r.content))
            label = u.split('/')[-1]
            st.session_state.perguntas += gerar_questoes_interpretativas(txt, num_list[idx] if idx < len(num_list) else 5, label)
            idx += 1
        # preparar estado de respostas
        st.session_state.respondido = [False] * len(st.session_state.perguntas)
        st.session_state.respostas = []

# Exibir e avaliar
if st.session_state.gerar:
    st.markdown("### 🔍 Avaliação de Questões Dinâmicas")
    perguntas = st.session_state.perguntas

    for i, q in enumerate(perguntas):
        st.subheader(f"❓ Pergunta {i+1} ({q['modulo']})")
        escolha = st.radio(q["texto"], q["opcoes"], key=f"radio_{i}")

        if st.button(f"Responder {i+1}", key=f"btn_{i}") and not st.session_state.respondido[i]:
            acertou = escolha == q["correta"]
            st.session_state.respostas.append({"módulo": q["modulo"], "acertou": acertou})
            st.session_state.respondido[i] = True
            if acertou:
                st.success("✅ Acertou!")
            else:
                st.error("❌ Errou!")

    # Finalizar avaliação
    if st.button("✅ Finalizar Avaliação"):
        df = pd.DataFrame(st.session_state.respostas)
        acertos = df["acertou"].sum()
        total = len(df)
        perc = (acertos/total)*100

        st.header("📊 Resultados Gerais")
        st.metric("Total de Acertos", f"{acertos}/{total}")
        st.progress(perc/100)

        # Desempenho por módulo
        st.subheader("📌 Desempenho por PDF/Fonte")
        mod = df.groupby("módulo")["acertou"].agg(["mean","count"]).reset_index()
        mod["% Acerto"] = (mod["mean"]*100).round(1)
        st.dataframe(mod[["módulo","% Acerto","count"]].rename(columns={"módulo":"Fonte","count":"Perguntas"}))

        # Gráfico com matplotlib
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.bar(mod["módulo"], mod["% Acerto"])
        ax.axhline(75, linestyle='--')
        ax.set_ylabel("% Acerto")
        ax.set_title("Desempenho por Fonte")
        st.pyplot(fig)


