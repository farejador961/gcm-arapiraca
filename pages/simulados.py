import streamlit as st
import random
import pandas as pd
import requests
from datetime import datetime
import requests
from bs4 import BeautifulSoup


st.set_page_config(page_title="Simulados por Banca", layout="wide")
st.title("📘 Simulados de Concursos - Banca e Cargo")

# Filtros de busca
st.markdown("### 🔍 Filtros para Buscar Questões")

col1, col2, col3 = st.columns(3)

with col1:
    banca = st.text_input("Nome da Banca (ex: VUNESP, CEBRASPE)")
with col2:
    materia = st.text_input("Matéria (ex: Direito Constitucional)")
with col3:
    cargo = st.text_input("Cargo (ex: Guarda Municipal, Professor)")

num_questoes = st.slider("Quantidade de Questões", 5, 100, 10)

buscar = st.button("🔍 Gerar Questões Avulsas")

# Simulação de banco de dados (depois será alimentado por scraping/API)
def buscar_questoes_simuladas(banca, materia, cargo, quantidade):
    # Aqui será substituído por scraping ou API real
    exemplos = [
        {"pergunta": f"Questão de {materia} - {cargo} [{banca}]", "opcoes": ["A", "B", "C", "D"], "resposta": "A"}
        for _ in range(quantidade)
    ]
    return exemplos

#Buscar simulados
def buscar_provas_por_banca(banca_nome):
    url_base = "https://www.pciconcursos.com.br/provas/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url_base, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    resultados = []

    for link in soup.select("a"):
        texto_link = link.text.strip().upper()
        if banca_nome.upper() in texto_link:
            href = link.get("href")
            if href and "/provas/" in href:
                resultados.append({
                    "titulo": texto_link,
                    "url": f"https://www.pciconcursos.com.br{href}"
                })

    return resultados

# Geração e exibição das questões
if buscar:
    if not banca or not materia or not cargo:
        st.warning("Preencha todos os campos antes de buscar.")
    else:
        st.info("🔄 Buscando questões...")
        questoes = buscar_questoes_simuladas(banca, materia, cargo, num_questoes)
        st.success(f"{len(questoes)} questões carregadas.")
        st.markdown("## 📄 Questões Geradas")

        for i, q in enumerate(questoes):
            st.markdown(f"---\n**Q{i+1}.** {q['pergunta']}")
            escolha = st.radio(f"Escolha (Q{i+1})", q["opcoes"], key=f"q{i}")
            if st.button(f"Mostrar Gabarito Q{i+1}", key=f"gab_{i}"):
                st.info(f"✅ Resposta correta: {q['resposta']}")

