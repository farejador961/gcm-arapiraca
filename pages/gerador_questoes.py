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

# Configurações da página
st.set_page_config(page_title="Gerador de Questões", layout="wide")
st.title("📝 Gerador de Questões - PDF → Múltipla Escolha")
st.image("dados/Maike.png", width=150)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sessão para textos
if "textos_pdf" not in st.session_state:
    st.session_state.textos_pdf = []
if "num_questoes" not in st.session_state:
    st.session_state.num_questoes = []

# Interface de múltiplos PDFs
with st.form("form_gerador"):
    col1, col2 = st.columns(2)

    with col1:
        uploaded_files = st.file_uploader("📁 Envie um ou mais PDFs", type="pdf", accept_multiple_files=True)
        urls = st.text_area("📄 URLs de PDFs (uma por linha)")

    with col2:
        default_num = 5
        num_por_pdf = st.text_input("Quantas questões por PDF? (separado por vírgula)", value="5,5")

    gerar = st.form_submit_button("🔎 Gerar Questões")

# Função para extrair texto
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
    tokens = word_tokenize(texto)
    tagged = pos_tag(tokens)
    nouns = [w for w, t in tagged if t.startswith("NN") and w.isalpha() and len(w) > 3]
    questoes = []
    random.shuffle(sentencas)
    for sent in sentencas:
        palavras = word_tokenize(sent)
        tags = pos_tag(palavras)
        subs = [w for w, tag in tags if tag.startswith("NN") and w in nouns]
        if not subs:
            continue
        resposta = random.choice(subs)
        pergunta = sent.replace(resposta, "____")
        distratores = random.sample([n for n in nouns if n != resposta], k=3) if len(nouns) > 3 else []
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

# Processamento
if gerar:
    st.session_state.textos_pdf = []
    st.session_state.num_questoes = []

    num_q_list = [int(n.strip()) for n in num_por_pdf.split(",") if n.strip().isdigit()]
    idx = 0

    # PDFs enviados
    for pdf_file in uploaded_files:
        nome_base = pdf_file.name.rsplit('.', 1)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_unico = f"{nome_base}_{timestamp}.pdf"
        path = os.path.join(UPLOAD_FOLDER, nome_unico)

        with open(path, "wb") as f:
            f.write(pdf_file.getvalue())

        texto = extrair_texto(path)
        st.session_state.textos_pdf.append(texto)
        st.session_state.num_questoes.append(num_q_list[idx] if idx < len(num_q_list) else 5)
        idx += 1

    # PDFs por URL
    for url in urls.strip().splitlines():
        if not url.strip():
            continue
        try:
            r = requests.get(url.strip())
            r.raise_for_status()
            texto = extrair_texto(BytesIO(r.content))
            st.session_state.textos_pdf.append(texto)
            st.session_state.num_questoes.append(num_q_list[idx] if idx < len(num_q_list) else 5)
            idx += 1
        except Exception as e:
            st.error(f"Erro ao baixar PDF de {url}: {e}")

    # Gerar questões para cada PDF
    st.session_state.questoes = []
    for texto, qtd in zip(st.session_state.textos_pdf, st.session_state.num_questoes):
        questoes_pdf = gerar_questoes_cloze(texto, qtd)
        st.session_state.questoes.extend(questoes_pdf)

    st.session_state.gq_resp = [None] * len(st.session_state.questoes)
    st.session_state.gq_comment = [""] * len(st.session_state.questoes)
    st.session_state.show_gabarito = [False] * len(st.session_state.questoes)
    st.success(f"✅ {len(st.session_state.questoes)} questões geradas com sucesso!")

# Exibir questões
if "questoes" in st.session_state and st.session_state.questoes:
    questoes = st.session_state.questoes
    st.markdown("### 🔍 Questões Geradas")

    for i, q in enumerate(questoes):
        st.markdown(f"---\n**Q{i+1}.** {q['pergunta']}")
        escolha = st.radio(
            f"Escolha a alternativa (Q{i+1})",
            options=q["opcoes"],
            key=f"q{i}"
        )
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
        perc = acertos / len(questoes)
        st.metric("Acertos", f"{acertos}/{len(questoes)} ({perc*100:.1f}%)")
        st.progress(perc)

        df = pd.DataFrame(resultados)
        os.makedirs("dados", exist_ok=True)
        df.to_csv("dados/questoes_geradas.csv", mode="a", index=False, header=not os.path.exists("dados/questoes_geradas.csv"))
        st.success("🗃️ Resultados salvos em dados/questoes_geradas.csv")

    if st.button("🧹 Limpar e Recomeçar"):
        for key in list(st.session_state.keys()):
            if key.startswith("q") or key.startswith("gab_") or key.startswith("c") or key in ["questoes", "gq_resp", "gq_comment", "show_gabarito", "textos_pdf", "num_questoes"]:
                del st.session_state[key]
        st.experimental_rerun()

