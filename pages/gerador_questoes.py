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
from fuzzywuzzy import fuzz

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

def gerar_questoes_interpretativas(texto, n, modulo_label, max_palavras_sentenca=60, max_caracteres_alternativa=360):
    # Quebra em sentenças e limita por número de palavras
    sentencas = [s.strip() for s in sent_tokenize(texto) if 8 <= len(s.split()) <= max_palavras_sentenca]
    if not sentencas:
        return []

    questoes = []
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentencas)
    pontuacoes = X.sum(axis=1).flatten().tolist()[0]
    sentencas_pontuadas = sorted(zip(sentencas, pontuacoes), key=lambda x: x[1], reverse=True)

    usadas = set()
    tipos_questoes = [
        "De acordo com o texto, qual das alternativas abaixo está correta?",
        "Assinale a alternativa que melhor completa a seguinte afirmação sobre o texto:",
        "Com base no texto, é INCORRETO afirmar que:",
        "Qual das alternativas representa a principal ideia contida no seguinte trecho do texto?",
        "O texto permite inferir que:",
        "Segundo o texto, qual das seguintes afirmações é verdadeira?",
        "A partir da leitura, conclui-se que:",
        "O autor do texto deixa claro que:"
    ]

    for sentenca_base, _ in sentencas_pontuadas:
        if sentenca_base in usadas:
            continue

        palavras = word_tokenize(sentenca_base)
        tagged = pos_tag(palavras)

        substantivos = [word for word, pos in tagged if pos.startswith('NN')] or ['']
        verbos = [word for word, pos in tagged if pos.startswith('VB')] or ['']
        adjetivos = [word for word, pos in tagged if pos.startswith('JJ')] or ['']

        correta = sentenca_base.strip()
        if len(correta) > max_caracteres_alternativa:
            correta = correta[:max_caracteres_alternativa].rsplit(' ', 1)[0] + "..."

        usadas.add(correta)

        tipo_questao = random.choice(tipos_questoes)
        alternativas = [correta]

        tentativas = 0
        while len(alternativas) < 4 and tentativas < 20:
            try:
                estrategia = random.randint(1, 4)

                if estrategia == 1:
                    palavra = random.choice(substantivos)
                    substitutos = [s for s in substantivos if s != palavra]
                    falsa = sentenca_base.replace(palavra, random.choice(substitutos)) if substitutos else ""
                elif estrategia == 2:
                    palavra = random.choice(verbos)
                    substitutos = [v for v in verbos if v != palavra]
                    falsa = sentenca_base.replace(palavra, random.choice(substitutos)) if substitutos else ""
                elif estrategia == 3:
                    palavra = random.choice(adjetivos)
                    substitutos = [a for a in adjetivos if a != palavra]
                    falsa = sentenca_base.replace(palavra, random.choice(substitutos)) if substitutos else ""
                else:
                    falsa = random.choice([s for s in sentencas if s != sentenca_base])

                falsa = falsa.strip()
                if len(falsa) > max_caracteres_alternativa:
                    falsa = falsa[:max_caracteres_alternativa].rsplit(' ', 1)[0] + "..."

                if falsa and falsa not in alternativas:
                    alternativas.append(falsa)

            except Exception:
                pass
            tentativas += 1

        if len(alternativas) < 4:
            continue

        random.shuffle(alternativas)

        questoes.append({
            "texto": tipo_questao,
            "opcoes": alternativas,
            "correta": correta,
            "modulo": modulo_label,
            "dica": "Analise atentamente os detalhes da sentença."
        })

        if len(questoes) >= n:
            break

    return questoes

# Processamento ao clicar em Gerar
if "gerar" not in st.session_state:
    st.session_state.gerar = False

# Inicialização do estado
if "perguntas" not in st.session_state:
    st.session_state.perguntas = []
if "respostas" not in st.session_state:
    st.session_state.respostas = []

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

        # Garantir que as respostas sejam inicializadas corretamente
        if len(st.session_state.respostas) != len(st.session_state.perguntas):
            st.session_state.respostas = [{} for _ in range(len(st.session_state.perguntas))]

# Exibir e avaliar
if st.session_state.gerar:
    st.markdown("### 🔍 Avaliação de Questões Dinâmicas")
    perguntas = st.session_state.perguntas

    for i, q in enumerate(perguntas):
        st.subheader(f"❓ Pergunta {i+1} ({q['modulo']})")
        escolha = st.radio(q["texto"], q["opcoes"], key=f"radio_{i}")

        if st.button(f"Responder {i+1}", key=f"btn_{i}"):
            acertou = escolha == q["correta"]
            st.session_state.respostas[i] = {
                "módulo": q["modulo"],
                "acertou": acertou,
                "resposta": escolha,
                "correta": q["correta"]
            }
            if acertou:
                st.success("✅ Acertou!")
            else:
                st.error(f"❌ Errou! Resposta correta: {q['correta']}")

        # Exibir feedback da última resposta, mesmo se não clicar de novo
        if st.session_state.respostas[i]:
            r = st.session_state.respostas[i]
            if r["acertou"]:
                st.success(f"✅ Última resposta: {r['resposta']} (Correta)")
            else:
                st.error(f"❌ Última resposta: {r['resposta']} (Correta: {r['correta']})")

    # Finalizar avaliação
    if st.button("✅ Finalizar Avaliação"):
        df = pd.DataFrame(st.session_state.respostas)
        acertos = df["acertou"].sum()
        total = len(df)
        perc = (acertos / total) * 100

        st.header("📊 Resultados Gerais")
        st.metric("Total de Acertos", f"{acertos}/{total}")
        st.progress(perc / 100)

        # Desempenho por módulo
        st.subheader("📌 Desempenho por PDF/Fonte")
        mod = df.groupby("módulo")["acertou"].agg(["mean", "count"]).reset_index()
        mod["% Acerto"] = (mod["mean"] * 100).round(1)
        st.dataframe(mod[["módulo", "% Acerto", "count"]].rename(columns={"módulo": "Fonte", "count": "Perguntas"}))

        # Gráfico com matplotlib
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.bar(mod["módulo"], mod["% Acerto"])
        ax.axhline(75, linestyle='--')
        ax.set_ylabel("% Acerto")
        ax.set_title("Desempenho por Fonte")
        st.pyplot(fig)



