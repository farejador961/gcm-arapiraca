import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from time import sleep
from gtts import gTTS
import base64
import random

# --- Configuração da página ---
st.set_page_config(page_title="Coach GCM Arapiraca", layout="wide")
st.title("👮‍♂️ Coach GCM Arapiraca - Avaliação Inteligente")

# --- Funções auxiliares ---
def falar(texto):
    try:
        tts = gTTS(text=texto, lang='pt-br')
        tts.save("fala.mp3")
        with open("fala.mp3", "rb") as f:
            audio_bytes = f.read()
            b64 = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
                <audio autoplay>
                <source src=\"data:audio/mp3;base64,{b64}\" type=\"audio/mp3\">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
    except:
        st.warning("⚠️ Erro ao gerar áudio. Texto exibido apenas.")
        st.info(f"🗣️ {texto}")


def exibir_dialogo(texto):
    st.markdown(
        f'<p style="font-size: 20px; font-weight: bold; text-align: center; color: #4CAF50;">{texto}</p>',
        unsafe_allow_html=True
    )
    falar(texto)
    sleep(1)

# --- Carregamento de perguntas ---
with open("dados/perguntas.json", encoding="utf-8-sig") as f:
    data = json.load(f)

letras = ["A", "B", "C", "D", "E", "F"]
perguntas = []

for modulo, lista in data["modulos"].items():
    for item in lista:
        alternativas = item["alternativas"]
        
        # Normalizar alternativas: se for lista, transformar em dicionário
        if isinstance(alternativas, list):
            alternativas = {letras[i]: texto for i, texto in enumerate(alternativas)}

        perguntas.append({
            "id": item.get("id"),
            "modulo": modulo,
            "texto": item["pergunta"],
            "opcoes": alternativas,
            "correta": item["resposta_correta"]
        })

# --- Sessão ---
if "answers" not in st.session_state:
    st.session_state.answers = {}  # id -> {resposta, acertou}

# --- Controles de seleção ---
modulos_disponiveis = sorted(set(q["modulo"] for q in perguntas))
col1, col2, col3 = st.columns(3)
with col1:
    selected_modulos = st.multiselect("Selecione módulos", modulos_disponiveis, default=modulos_disponiveis)
with col2:
    num_por_modulo = st.number_input("Qnt de questões por módulo", min_value=1, max_value=300, value=5)
with col3:
    include_answered = st.checkbox("Incluir questões já respondidas", value=False)

# --- Seleção de questões ---
filtradas = [q for q in perguntas if q["modulo"] in selected_modulos]
if not include_answered:
    filtradas = [q for q in filtradas if q["id"] not in st.session_state.answers]

# agrupa por módulo e seleciona aleatoriamente
selecionadas = []
for mod in selected_modulos:
    grupo = [q for q in filtradas if q["modulo"] == mod]
    selecionadas += random.sample(grupo, min(len(grupo), num_por_modulo))

# misturar ordem geral
random.shuffle(selecionadas)

# --- Exibição das questões ---
st.image("dados/Maike.png", width=150)
for q in selecionadas:
    idx = q["id"]
    # Cabeçalho com marcação
    if idx in st.session_state.answers:
        status = "✅" if st.session_state.answers[idx]["acertou"] else "❌"
        st.subheader(f"{status} Pergunta {idx} ({q['modulo']})")
    else:
        st.subheader(f"❓ Pergunta {idx} ({q['modulo']})")
    
    escolha = st.radio(q["texto"], list(q["opcoes"].keys()), format_func=lambda x: f"{x}: {q['opcoes'][x]}", key=f"radio_{idx}")
    
    if st.button("Responder/Revisar", key=f"btn_{idx}"):
        acertou = (escolha == q["correta"])
        st.session_state.answers[idx] = {"resposta": escolha, "acertou": acertou}
        if acertou:
            st.success("✅ Acertou!")
            exibir_dialogo("Parabéns, você acertou a pergunta!")
        else:
            st.error("❌ Errou!")
            exibir_dialogo("Não desanime, vamos tentar novamente!")

# --- Finalizar avaliação ---
if st.button("✅ Finalizar Avaliação"):
    if not st.session_state.answers:
        st.warning("Você ainda não respondeu nenhuma pergunta.")
    else:
        df = pd.DataFrame.from_dict(st.session_state.answers, orient='index')
        df['modulo'] = df.index.map(lambda i: next(q['modulo'] for q in perguntas if q['id']==i))
        acertos = df['acertou'].sum()
        total = len(df)
        percentual = (acertos / total) * 100

        st.header("📊 Resultados Gerais")
        st.metric("Total de Acertos", f"{acertos}/{total}")
        st.progress(percentual / 100)

        # feedback geral
        if percentual >= 95:
            st.balloons()
            st.success("🚀 UAU! Desempenho excelente! Continue assim.")
        elif percentual >= 75:
            st.success("🎯 Ótimo progresso! Rumo aos 100%!")
        elif percentual >= 50:
            st.warning("📘 Bom começo! Continue praticando.")
        else:
            st.error("⚠️ Vamos reforçar os estudos! Você consegue!")

        # desempenho por módulo
        st.subheader("📌 Desempenho por Módulo")
        modulos = df.groupby('modulo')['acertou'].agg(['mean', 'count']).reset_index()
        modulos.columns = ['Módulo', 'Taxa de Acerto', 'Perguntas']
        modulos['% Acerto'] = (modulos['Taxa de Acerto'] * 100).round(1)
        st.dataframe(modulos[['Módulo', '% Acerto', 'Perguntas']])

        # gráfico
        fig, ax = plt.subplots()
        ax.bar(modulos['Módulo'], modulos['% Acerto'])
        ax.axhline(75, linestyle='--', label='Meta (75%)')
        ax.set_ylabel('Taxa de Acerto (%)')
        ax.set_title('Desempenho por Módulo')
        ax.legend()
        st.pyplot(fig)

        # sugestões
        st.subheader("🧠 Sugestões Personalizadas de Revisão")
        criticos = modulos[modulos['% Acerto'] < 75]['Módulo'].tolist()
        if criticos:
            st.warning("⚠️ Você teve desempenho abaixo da meta nos módulos:")
            for m in criticos:
                st.markdown(f"- **{m}**: revise teoria e refaça exercícios.")
        else:
            st.success("✨ Nenhum módulo com desempenho crítico. Excelente!")

        # salvar resultados
        df.to_csv('dados/resultados.csv', mode='a', index_label='id')

