import streamlit as st
import requests
from bs4 import BeautifulSoup

import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Simulados Inteligentes", layout="wide")
st.title("🎯 Simulados Inteligentes")

tab1, tab2 = st.tabs(["📘 Buscar Provas Concursos Brasil", "📝 Gerador de Questões (PCI & Concursos Brasil)"])

# ---------------- TAB 1: Provas Concursos Brasil ----------------
with tab1:
    with st.form("busca_simulados"):
        col1, col2 = st.columns(2)
        with col1:
            cargo = st.text_input("Cargo (ex: Guarda Municipal)")
        with col2:
            materia = st.text_input("Matéria (opcional)")

        buscar = st.form_submit_button("🔍 Buscar Provas")

    def buscar_questoes_concursosnobrasil(cargo, materia=None):
        url = f"https://www.concursosnobrasil.com/questoes/{cargo}/"
        if materia:
            url += f"{materia}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        questoes = []
        for question in soup.find_all('div', class_='questao'):
            try:
                enunciado = question.find('div', class_='enunciado').get_text(strip=True)
                alternativas = [alt.get_text(strip=True) for alt in question.find_all('li')]
                questoes.append({'enunciado': enunciado, 'alternativas': alternativas})
            except:
                continue
        return questoes

    if buscar:
        questoes = buscar_questoes_concursosnobrasil(cargo, materia)
        if questoes:
            for q in questoes:
                st.markdown(f"**Enunciado:** {q['enunciado']}")
                for i, alt in enumerate(q['alternativas']):
                    st.markdown(f"{chr(65+i)}) {alt}")
                st.markdown("---")
        else:
            st.warning("Nenhuma questão encontrada para este cargo e matéria.")

# ---------------- TAB 2: Gerador de Questões ----------------
with tab2:
    st.subheader("Gerar questões avulsas por cargo e matéria")

    banca_sel = st.selectbox("Selecione a Fonte", ["PCI Concursos", "Concursos no Brasil"])
    cargo_sel = st.text_input("Cargo")
    materia_sel = st.text_input("Matéria")

    def buscar_questoes_pciconcursos(cargo):
        url = f"https://www.pciconcursos.com.br/provas/{cargo}/1"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        questoes = []
        for question in soup.find_all('div', class_='questao'):
            try:
                enunciado = question.find('div', class_='pergunta').get_text(strip=True)
                alternativas = [alt.get_text(strip=True) for alt in question.find_all('li')]
                questoes.append({'enunciado': enunciado, 'alternativas': alternativas})
            except:
                continue
        return questoes

    if st.button("🔍 Gerar Questões"):
        if banca_sel == "PCI Concursos":
            questoes = buscar_questoes_pciconcursos(cargo_sel)
        else:
            questoes = buscar_questoes_concursosnobrasil(cargo_sel, materia_sel)

        if questoes:
            for q in questoes:
                st.markdown(f"**Enunciado:** {q['enunciado']}")
                for i, alt in enumerate(q['alternativas']):
                    st.markdown(f"{chr(65+i)}) {alt}")
                st.markdown("---")
        else:
            st.warning("Nenhuma questão encontrada.")
