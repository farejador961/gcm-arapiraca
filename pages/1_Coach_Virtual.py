import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from time import sleep
from gtts import gTTS
import base64

# Configuração da página
st.set_page_config(page_title="Coach GCM Arapiraca", layout="wide")
st.title("👮‍♂️ Coach GCM Arapiraca - Avaliação Inteligente")

# Função de fala com gTTS (funciona online e localmente)
def falar(texto):
    try:
        tts = gTTS(text=texto, lang='pt-br')
        tts.save("fala.mp3")
        with open("fala.mp3", "rb") as f:
            audio_bytes = f.read()
            b64 = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
                <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.warning("⚠️ Erro ao gerar áudio. Texto exibido apenas.")
        st.info(f"🗣️ {texto}")

# Exibir fala de Jany
def exibir_dialogo(texto):
    st.markdown(
        f'<p style="font-size: 20px; font-weight: bold; text-align: center; color: #4CAF50;">{texto}</p>',
        unsafe_allow_html=True
    )
    falar(texto)
    sleep(1)

# Carrega perguntas do arquivo JSON
with open("dados/perguntas.json", encoding="utf-8-sig") as f:
    data = json.load(f)

# Converte para lista com metadados
perguntas = []
for modulo, lista in data["modulos"].items():
    for item in lista:
        perguntas.append({
            "modulo": modulo,
            "texto": item["pergunta"],
            "opcoes": item["alternativas"],
            "correta": item["resposta_correta"]
        })

# Estados da sessão
if "respostas" not in st.session_state:
    st.session_state.respostas = []
if "respondido" not in st.session_state:
    st.session_state.respondido = [False] * len(perguntas)

# Exibir imagem da Jany
st.image("dados/Mayke.png", width=100)

# Exibir perguntas
for i, q in enumerate(perguntas):
    st.subheader(f"❓ Pergunta {i+1}")
    escolha = st.radio(q["texto"], q["opcoes"], key=f"radio_{i}")

    if st.button(f"Responder {i+1}", key=f"btn_{i}") and not st.session_state.respondido[i]:
        acertou = escolha == q["correta"]
        st.session_state.respostas.append({
            "módulo": q["modulo"],
            "acertou": acertou
        })
        st.session_state.respondido[i] = True
        if acertou:
            st.success("✅ Acertou!")
            exibir_dialogo("Parabéns, você acertou a pergunta!")
        else:
            st.error("❌ Errou!")
            exibir_dialogo("Não desanime, vamos tentar novamente!")

# Finalizar avaliação
if st.button("✅ Finalizar Avaliação"):
    if not st.session_state.respostas:
        st.warning("Você ainda não respondeu nenhuma pergunta.")
    else:
        df = pd.DataFrame(st.session_state.respostas)
        acertos = df["acertou"].sum()
        total = len(df)
        percentual = (acertos / total) * 100

        st.header("📊 Resultados Gerais")
        st.metric("Total de Acertos", f"{acertos}/{total}")
        st.progress(percentual / 100)

        # Feedback geral
        if percentual >= 95:
            st.balloons()
            st.success("🚀 UAU! Desempenho excelente! Continue assim.")
        elif percentual >= 75:
            st.success("🎯 Ótimo progresso! Rumo aos 100%!")
        elif percentual >= 50:
            st.warning("📘 Bom começo! Continue praticando.")
        else:
            st.error("⚠️ Vamos reforçar os estudos! Você consegue!")

        # Desempenho por módulo
        st.subheader("📌 Desempenho por Módulo")
        modulos = df.groupby("módulo")["acertou"].agg(["mean", "count"]).reset_index()
        modulos.columns = ["Módulo", "Taxa de Acerto", "Perguntas"]
        modulos["% Acerto"] = (modulos["Taxa de Acerto"] * 100).round(1)
        st.dataframe(modulos[["Módulo", "% Acerto", "Perguntas"]])

        # Gráfico de desempenho
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(modulos["Módulo"], modulos["% Acerto"], color='skyblue')
        ax.axhline(75, color='green', linestyle='--', label='Meta (75%)')
        ax.set_ylabel("Taxa de Acerto (%)")
        ax.set_title("Desempenho por Módulo")
        ax.legend()
        st.pyplot(fig)

        # Sugestões de revisão
        st.subheader("🧠 Sugestões Personalizadas de Revisão")
        modulos_criticos = modulos[modulos["% Acerto"] < 75]["Módulo"].tolist()
        if modulos_criticos:
            st.warning("⚠️ Atenção! Você teve desempenho abaixo da meta nos seguintes módulos:")
            for m in modulos_criticos:
                st.markdown(f"- **Módulo {m}**: revise teoria, refaça exercícios e assista às aulas de reforço.")
        else:
            st.success("✨ Nenhum módulo com desempenho crítico. Excelente!")

        # Salvar resultados
        df.to_csv("dados/resultados.csv", mode="a", index=False)
