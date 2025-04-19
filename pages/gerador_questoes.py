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

# Configurações de página
st.set_page_config(page_title="Gerador de Questões", layout="wide")
st.title("📝 Gerador de Questões - PDF → Múltipla Escolha")

# Pasta de uploads locais
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Interface: fonte do PDF
with st.form("form_gerador"):
    col1, col2 = st.columns(2)
    with col1:
        num_q = st.selectbox("Quantas questões?", [10, 20, 40, 50, 100])
        pdf_url = st.text_input("📄 URL do PDF")
    with col2:
        uploaded = st.file_uploader("📁 Ou envie um PDF", type="pdf")
    gerar = st.form_submit_button("🔎 Gerar Questões")

def extrair_texto(pdf_stream):
    texto = ""
    with pdfplumber.open(pdf_stream) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                texto += t + "\n"
    return texto

# Geração de questões tipo cloze
def gerar_questoes_cloze(texto, n):
    sentencas = sent_tokenize(texto)
    # Filtra e coleta todos os substantivos do texto
    tokens = word_tokenize(texto)
    tagged = pos_tag(tokens)
    nouns = [w for w,t in tagged if t.startswith("NN") and w.isalpha() and len(w)>3]
    questoes = []
    random.shuffle(sentencas)
    for sent in sentencas:
        # encontra substantivos na sentença
        palavras = word_tokenize(sent)
        tags = pos_tag(palavras)
        subs = [w for w,tag in tags if tag.startswith("NN") and w in nouns]
        if not subs: 
            continue
        resposta = random.choice(subs)
        # cria lacuna
        pergunta = sent.replace(resposta, "____")
        # escolhe 3 distratores
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

# Se gerou
if gerar:
    st.info("🛠️ Processando PDF...")

    # Obtém texto
    try:
        if uploaded:
            path = os.path.join(UPLOAD_FOLDER, uploaded.name)
            with open(path, "wb") as f: f.write(uploaded.read())
            texto = extrair_texto(path)
        elif pdf_url:
            r = requests.get(pdf_url); r.raise_for_status()
            texto = extrair_texto(BytesIO(r.content))
        else:
            st.warning("Envie um PDF ou informe a URL.") 
            st.stop()

        # Cria as questões
        questoes = gerar_questoes_cloze(texto, num_q)
        st.success(f"✅ {len(questoes)} questões geradas com sucesso!")
    except Exception as e:
        st.error(f"❌ Falha ao processar: {e}")
        st.stop()

    # Inicializa sessão
    if "gq_resp" not in st.session_state:
        st.session_state.gq_resp = [None]*len(questoes)
        st.session_state.gq_comment = [""]*len(questoes)
        st.session_state.show_gabarito = [False]*len(questoes)

    # Exibe cada questão
    for i, q in enumerate(questoes):
        st.markdown(f"---\n**Q{i+1}.** {q['pergunta']}")
        escolha = st.radio(
            label=f"Escolha a alternativa (Q{i+1})",
            options=q["opcoes"],
            key=f"q{i}"
        )
        st.session_state.gq_resp[i] = escolha

        # Botão para gabarito
        if st.button("Mostrar Gabarito", key=f"gab_{i}"):
            st.session_state.show_gabarito[i] = True
        if st.session_state.show_gabarito[i]:
            st.info(f"**Resposta correta:** {q['resposta']}")

        # Campo de comentário
        comment = st.text_input("Comentário (opcional)", key=f"c{i}")
        st.session_state.gq_comment[i] = comment

    # Botão de envio e correção
    if st.button("📥 Enviar Respostas e Salvar"):
        acertos = 0
        resultados = []
        for idx, q in enumerate(questoes):
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
        # Exibe feedback
        perc = acertos/len(questoes)
        st.metric("Acertos", f"{acertos}/{len(questoes)} ({perc*100:.1f}%)")
        st.progress(perc)

        # Salva em CSV para o painel de progresso
        df = pd.DataFrame(resultados)
        df.to_csv("dados/questoes_geradas.csv", mode="a", index=False, header=not os.path.exists("dados/questoes_geradas.csv"))
        st.success("🗃️ Resultados salvos em dados/questoes_geradas.csv")

        # Opcional: redirecionar ao Painel de Progresso
        st.write("[➡️ Vá para o Painel de Progresso](#/pages/2_Painel_de_Progresso)")


