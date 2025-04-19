import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import pyttsx3
import os
import pygame
from time import sleep  # Importando o sleep corretamente

# Configurações iniciais
st.set_page_config(page_title="Coach GCM Arapiraca", layout="wide")
st.title("👮‍♂️ Coach GCM Arapiraca - Avaliação Inteligente")

# Carrega perguntas
with open("dados/perguntas.json", encoding="utf-8-sig") as f:
    data = json.load(f)

# Converte perguntas para lista única com referência ao módulo
perguntas = []
for modulo, lista in data["modulos"].items():
    for item in lista:
        perguntas.append({
            "modulo": modulo,
            "texto": item["pergunta"],
            "opcoes": item["alternativas"],
            "correta": item["resposta_correta"]
        })

# Estado da sessão
if "respostas" not in st.session_state:
    st.session_state.respostas = []
if "respondido" not in st.session_state:
    st.session_state.respondido = [False] * len(perguntas)

# Exibir imagem da Jany
st.image("dados/jany.png", width=150)  # Substitua "jany.png" pelo nome correto da imagem

# Inicializar fora da função para não reiniciar a engine a cada chamada
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Força o uso da voz Maria em pt-BR
for voice in voices:
    if "Maria" in voice.name and "Portuguese" in voice.name:
        engine.setProperty('voice', voice.id)
        break

def speak(texto):
    engine.say(texto)
    engine.runAndWait()
    engine.setProperty('volume', 1.0)  # Máximo = 1.0
engine.setProperty('rate', 200)   # Velocidade (padrão entre 150~200)

# Função para exibir o texto da Jany de forma interativa
def exibir_dialogo(texto):
    st.markdown(f'<p style="font-size: 20px; font-weight: bold; text-align: center; color: #4CAF50;">{texto}</p>', unsafe_allow_html=True)
    sleep(1)  # Simula um pequeno atraso entre falas

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
            speak("Parabéns, você acertou a pergunta!")
        else:
            st.error("❌ Errou!")
            exibir_dialogo("Não desanime, vamos tentar novamente!")
            speak("Não desanime, vamos tentar novamente!")

# Finalizar e mostrar resultados
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
            speak("Incrível, você teve um desempenho excelente. Continue assim!")
        elif percentual >= 75:
            st.success("🎯 Ótimo progresso! Rumo aos 100%!")
            speak("Ótimo trabalho! Estamos quase lá, vamos continuar com esse ritmo!")
        elif percentual >= 50:
            st.warning("📘 Bom começo! Continue praticando.")
            speak("Bom trabalho, mas continue praticando. Você vai melhorar a cada dia!")
        else:
            st.error("⚠️ Vamos reforçar os estudos! Você consegue!")
            speak("Não se preocupe, vamos reforçar os estudos e vamos superar juntos!")

        # Feedback por módulo
        st.subheader("📌 Desempenho por Módulo")
        modulos = df.groupby("módulo")["acertou"].agg(["mean", "count"]).reset_index()
        modulos.columns = ["Módulo", "Taxa de Acerto", "Perguntas"]
        modulos["% Acerto"] = (modulos["Taxa de Acerto"] * 100).round(1)
        st.dataframe(modulos[["Módulo", "% Acerto", "Perguntas"]])

        # Gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(modulos["Módulo"], modulos["% Acerto"], color='skyblue')
        ax.axhline(75, color='green', linestyle='--', label='Meta (75%)')
        ax.set_ylabel("Taxa de Acerto (%)")
        ax.set_title("Desempenho por Módulo")
        ax.legend()
        st.pyplot(fig)

        # Sugestões com base nos erros
        st.subheader("🧠 Sugestões Personalizadas de Revisão")
        modulos_criticos = modulos[modulos["% Acerto"] < 75]["Módulo"].tolist()
        if modulos_criticos:
            st.warning("⚠️ Atenção! Você teve desempenho abaixo da meta nos seguintes módulos:")
            speak("Atenção! Você teve um desempenho abaixo da meta em alguns módulos.")
            for m in modulos_criticos:
                st.markdown(f"- **Módulo {m}**: revise teoria, refaça exercícios e assista às aulas de reforço.")
        else:
            st.success("✨ Nenhum módulo com desempenho crítico. Excelente!")
            speak("Parabéns, você não tem nenhum módulo crítico, continue assim!")

        # Salvar resultados
        df.to_csv("dados/resultados.csv", mode="a", index=False)
