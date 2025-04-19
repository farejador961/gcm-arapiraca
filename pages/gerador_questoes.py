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

# Cria diretório de uploads se não existir
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Interface: seleção de fonte PDF
with st.form("form_gerador"):
    col1, col2 = st.columns(2)
    with col1:
        num_q = st.selectbox("Quantas questões?", [5, 10, 20, 40, 50, 100])
        pdf_url = st.text_input("📄 URL do PDF")
    with col2:
        uploaded = st.file_uploader("📁 Ou envie um PDF", type="pdf")
    gerar = st.form_submit_button("🔎 Gerar Questões")

# Função para extrair texto do PDF
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

# Geração de questões: só se for clicado o botão "Gerar"
if gerar:
    try:
        st.info("🛠️ Processando PDF...")

        if uploaded is not None:
            from datetime import datetime

            nome_base = uploaded.name.rsplit('.', 1)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_unico = f"{nome_base}_{timestamp}.pdf"
            path = os.path.join(UPLOAD_FOLDER, nome_unico)

            # Use uploaded.getvalue() em vez de uploaded.read()
            with open(path, "wb") as f:
                f.write(uploaded.getvalue())

            texto = extrair_texto(path)

        elif pdf_url.strip():
            r = requests.get(pdf_url)
            r.raise_for_status()
            texto = extrair_texto(BytesIO(r.content))

        else:
            st.warning("Envie um PDF **ou** informe uma URL.")
            st.stop()

        # Continua com a geração de questões...
        questoes = gerar_questoes_cloze(texto, num_q)
        st.success(f"✅ {len(questoes)} questões geradas com sucesso!")

    except Exception as e:
        st.error(f"❌ Erro ao processar: {e}")
        st.stop()


        # Armazenar as questões na sessão
        questoes = gerar_questoes_cloze(texto, num_q)
        st.session_state.questoes = questoes
        st.session_state.gq_resp = [None]*len(questoes)
        st.session_state.gq_comment = [""]*len(questoes)
        st.session_state.show_gabarito = [False]*len(questoes)
        st.success(f"✅ {len(questoes)} questões geradas com sucesso!")
    except Exception as e:
        st.error(f"❌ Erro ao processar o PDF: {e}")
        st.stop()

# Exibe as questões se existirem
if "questoes" in st.session_state:
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

    # Botão para corrigir
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

        # Salva resultados
        df = pd.DataFrame(resultados)
        os.makedirs("dados", exist_ok=True)
        df.to_csv("dados/questoes_geradas.csv", mode="a", index=False, header=not os.path.exists("dados/questoes_geradas.csv"))
        st.success("🗃️ Resultados salvos em dados/questoes_geradas.csv")

        st.write("[➡️ Vá para o Painel de Progresso](#/pages/2_Painel_de_Progresso)")

    # Botão para limpar questões e reiniciar
    if st.button("🧹 Limpar e Recomeçar"):
        for key in list(st.session_state.keys()):
            if key.startswith("q") or key.startswith("gab_") or key.startswith("c") or key in ["questoes", "gq_resp", "gq_comment", "show_gabarito"]:
                del st.session_state[key]
        st.experimental_rerun()
