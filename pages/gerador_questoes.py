import streamlit as st
import pdfplumber
import requests
from io import BytesIO
import nltk
from nltk.tokenize import sent_tokenize
import random
import pandas as pd
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import openai

# Baixar recursos do NLTK
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

# Configurações da página
st.set_page_config(page_title="Gerador de Questões", layout="wide")
st.title("📝 Gerador de Questões Dinâmicas")
st.image("dados/Maike.png", width=150)

def extrair_texto(pdf_stream):
    texto = ""
    with pdfplumber.open(pdf_stream) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                texto += t + "\n"
    return texto

# Sidebar para configurações de IA
# Sidebar para configurações de IA
st.sidebar.header("Configurações de IA")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if api_key:
    openai.api_key = api_key

generator = st.sidebar.selectbox(
    "Método de Geração", ["Local (TF-IDF)", "OpenAI GPT"]
)
temp = st.sidebar.slider("Temperatura (apenas GPT)", 0.0, 1.0, 0.7)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Função atualizada para gerar questões usando o novo método da API
def gerar_questoes_gpt(texto, n, modulo_label, model="gpt-3.5-turbo", temperature=0.7):
    questoes = []
    for i in range(n):
        prompt = f"""
Gere uma questão de múltipla escolha (4 alternativas) com base no seguinte texto do módulo '{modulo_label}':

""" + texto + """

Formato de saída:
Pergunta: ...
A) ...
B) ...
C) ...
D) ...
Resposta correta: letra (A, B, C ou D)
"""
        try:
            # Utilizando a nova API para interagir com o modelo GPT
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=500
            )
            content = response.choices[0].message["content"]
        except Exception as e:
            st.error(f"Erro na API GPT: {e}")
            break

        # Parse resposta
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        pergunta = ''
        opts = []
        corret = None
        for line in lines:
            if line.startswith("Pergunta:"):
                pergunta = line.split("Pergunta:", 1)[1].strip()
            elif line[1:2] == ')' or line[1:2] == ')':  # A) ...
                opts.append(line[2:].strip())
            elif line.lower().startswith("resposta correta"):
                letra = line.split(":", 1)[1].strip().upper()
                mapa = {"A": 0, "B": 1, "C": 2, "D": 3}
                if letra in mapa and len(opts) == 4:
                    corret = opts[mapa[letra]]
        if pergunta and len(opts) == 4 and corret:
            questoes.append({
                "texto": pergunta,
                "opcoes": opts,
                "correta": corret,
                "modulo": modulo_label
            })
    return questoes

def gerar_questoes_interpretativas(texto, n, modulo_label):
    sentencas = sent_tokenize(texto)
    questoes = []

    # TF-IDF para pontuar sentenças
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentencas)
    scores = X.sum(axis=1).A1
    ranked = sorted(zip(sentencas, scores), key=lambda x: x[1], reverse=True)

    used = set()
    for sent, _ in ranked:
        if sent in used or len(sent.split()) < 8:
            continue
        correct = sent.strip()
        used.add(correct)
        # distratores
        options = [correct]
        tries = 0
        while len(options) < 4 and tries < 20:
            fake = random.choice(sentencas).strip()
            if fake != correct and len(fake.split()) >= 8 and fake not in options:
                options.append(fake)
            tries += 1
        if len(options) < 4:
            continue
        random.shuffle(options)
        questoes.append({
            "texto": "Com base no texto, qual das alternativas está correta?",
            "opcoes": options,
            "correta": correct,
            "modulo": modulo_label
        })
        if len(questoes) >= n:
            break
    return questoes

# --- Streamlit UI e Lógica ---

if "gerar" not in st.session_state:
    st.session_state.gerar = False

with st.form("form_gerador"):
    uploaded = st.file_uploader("📁 PDFs", type="pdf", accept_multiple_files=True)
    urls = st.text_area("📄 URLs de PDFs (uma por linha)")
    qtds = st.text_input("Quantas questões por fonte? (vírgula)", "5,5")
    if st.form_submit_button("🔎 Gerar Questões"):
        if generator.startswith("OpenAI") and not api_key:
            st.error("Informe sua OpenAI API Key na sidebar para usar o gerador GPT.")
        else:
            st.session_state.gerar = True
            st.session_state.perguntas = []
            nums = [int(x) for x in qtds.split(',') if x.strip().isdigit()]
            idx = 0
            # PDFs locais
            for pdf in uploaded:
                label = pdf.name
                path = os.path.join(UPLOAD_FOLDER, f"{label}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
                with open(path, "wb") as f:
                    f.write(pdf.getvalue())
                txt = extrair_texto(path)
                n = nums[idx] if idx < len(nums) else nums[-1]
                if generator == "Local (TF-IDF)":
                    st.session_state.perguntas += gerar_questoes_interpretativas(txt, n, label)
                else:
                    st.session_state.perguntas += gerar_questoes_gpt(txt, n, label, temperature=temp)
                idx += 1
            # URLs
            for u in urls.splitlines():
                if not u.strip(): continue
                r = requests.get(u.strip())
                r.raise_for_status()
                txt = extrair_texto(BytesIO(r.content))
                label = u.split('/')[-1]
                n = nums[idx] if idx < len(nums) else nums[-1]
                if generator == "Local (TF-IDF)":
                    st.session_state.perguntas += gerar_questoes_interpretativas(txt, n, label)
                else:
                    st.session_state.perguntas += gerar_questoes_gpt(txt, n, label, temperature=temp)
                idx += 1
            st.session_state.respondido = [False]*len(st.session_state.perguntas)
            st.session_state.respostas = []

# Exibição e avaliação
if st.session_state.gerar:
    st.markdown("### 🔍 Avaliação de Questões Dinâmicas")
    for i, q in enumerate(st.session_state.perguntas):
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

    if st.button("✅ Finalizar Avaliação"):
        df = pd.DataFrame(st.session_state.respostas)
        acertos = df["acertou"].sum()
        total = len(df)
        perc = (acertos/total)*100 if total>0 else 0
        st.header("📊 Resultados Gerais")
        st.metric("Total de Acertos", f"{acertos}/{total}")
        st.progress(perc/100)

        st.subheader("📌 Desempenho por Fonte")
        mod = df.groupby("módulo")["acertou"].agg(["mean","count"]).reset_index()
        mod["% Acerto"] = (mod["mean"]*100).round(1)
        st.dataframe(mod[["módulo","% Acerto","count"]].rename(columns={"módulo":"Fonte","count":"Perguntas"}))

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.bar(mod["módulo"], mod["% Acerto"])
        ax.axhline(75, linestyle='--')
        ax.set_ylabel("% Acerto")
        ax.set_title("Desempenho por Fonte")
        st.pyplot(fig)

