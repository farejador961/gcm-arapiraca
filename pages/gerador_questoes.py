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

# Baixar recursos do NLTK
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

st.set_page_config(page_title="Gerador de Questões", layout="wide")
st.title("📝 Gerador de Questões - Vários PDFs")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.subheader("📂 Envie múltiplos PDFs")
pdf_files = st.file_uploader("Selecionar PDFs", type="pdf", accept_multiple_files=True)

quantidades = {}
if pdf_files:
    for pdf in pdf_files:
        quantidades[pdf.name] = st.slider(f"Quantas questões do arquivo '{pdf.name}'?", 1, 50, 5)

if st.button("🔎 Gerar Simulado"):
    todas_questoes = []

    def extrair_texto(pdf_stream):
        texto = ""
        with pdfplumber.open(pdf_stream) as pdf:
            for p in pdf.pages:
                t = p.extract_text()
                if t:
                    texto += t + "\n"
        return texto

    def gerar_questoes_cloze(texto, n):
        sentencas = sent_tokenize(texto)
        tokens = word_tokenize(texto)
        tagged = pos_tag(tokens)
        nouns = [w for w,t in tagged if t.startswith("NN") and w.isalpha() and len(w)>3]
        questoes = []
        random.shuffle(sentencas)
        for sent in sentencas:
            palavras = word_tokenize(sent)
            tags = pos_tag(palavras)
            subs = [w for w,tag in tags if tag.startswith("NN") and w in nouns]
            if not subs: 
                continue
            resposta = random.choice(subs)
            pergunta = sent.replace(resposta, "____")
            distratores = random.sample([n for n in nouns if n!=resposta], k=3) if len(nouns)>3 else []
            opcoes = distratores + [resposta]
            random.shuffle(opcoes)
            questoes.append({
                "pergunta": pergunta,
                "opcoes": opcoes,
                "resposta": resposta
            })
            if len(questoes) >= n:
                break
        return questoes

    for pdf in pdf_files:
        with st.spinner(f"Extraindo de: {pdf.name}"):
            path = os.path.join(UPLOAD_FOLDER, pdf.name)
            with open(path, "wb") as f:
                f.write(pdf.read())
            texto = extrair_texto(path)
            num_questoes = quantidades[pdf.name]
            questoes_pdf = gerar_questoes_cloze(texto, num_questoes)
            todas_questoes.extend(questoes_pdf)

    if not todas_questoes:
        st.warning("Nenhuma questão gerada.")
        st.stop()
    
    st.success(f"✅ Total de {len(todas_questoes)} questões geradas!")

    if "gq_resp" not in st.session_state:
        st.session_state.gq_resp = [None]*len(todas_questoes)
        st.session_state.gq_comment = [""]*len(todas_questoes)
        st.session_state.show_gabarito = [False]*len(todas_questoes)

    for i, q in enumerate(todas_questoes):
        st.markdown(f"---\n**Q{i+1}.** {q['pergunta']}")
        escolha = st.radio(f"Escolha a alternativa (Q{i+1})", options=q["opcoes"], key=f"q{i}")
        st.session_state.gq_resp[i] = escolha

        if st.button("Mostrar Gabarito", key=f"gab_{i}"):
            st.session_state.show_gabarito[i] = True
        if st.session_state.show_gabarito[i]:
            st.info(f"**Resposta correta:** {q['resposta']}")

        comment = st.text_input("Comentário (opcional)", key=f"c{i}")
        st.session_state.gq_comment[i] = comment

    if st.button("📥 Enviar Respostas e Salvar"):
        acertos = 0
        resultados = []
        for idx, q in enumerate(todas_questoes):
            acertou = (st.session_state.gq_resp[idx] == q["resposta"])
            if acertou: acertos += 1
            resultados.append({
                "timestamp": datetime.now().isoformat(),
                "pergunta": q["pergunta"],
                "escolha": st.session_state.gq_resp[idx],
                "resposta": q["resposta"],
                "acertou": acertou,
                "comentario": st.session_state.gq_comment[idx]
            })
        perc = acertos / len(todas_questoes)
        st.metric("Acertos", f"{acertos}/{len(todas_questoes)} ({perc*100:.1f}%)")
        st.progress(perc)

        df = pd.DataFrame(resultados)
        df.to_csv("dados/questoes_geradas.csv", mode="a", index=False, header=not os.path.exists("dados/questoes_geradas.csv"))
        st.success("🗃️ Resultados salvos em dados/questoes_geradas.csv")
        st.write("[➡️ Vá para o Painel de Progresso](#/pages/2_Painel_de_Progresso)")



