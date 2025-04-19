import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Simulados Inteligentes", layout="wide")
st.title("🎯 Simulados Inteligentes")

# ---------------- TAB 1: Gerador de Questões PCI Concursos ----------------
with st.form("busca_simulados"):
    col1, col2 = st.columns(2)
    with col1:
        cargo = st.text_input("Cargo (ex: Guarda Municipal)")
    with col2:
        materia = st.text_input("Matéria (opcional)")

    buscar = st.form_submit_button("🔍 Buscar Questões PCI Concursos")

# Função para buscar questões no PCI Concursos
def buscar_questoes_pciconcursos(cargo, materia=None):
    url = f"https://www.pciconcursos.com.br/provas/{cargo}/1"
    if materia:
        url += f"?materia={materia}"  # Se houver matéria, adicionar à URL
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

# Se o botão de buscar for pressionado
if buscar:
    if cargo:
        questoes = buscar_questoes_pciconcursos(cargo, materia)
        if questoes:
            for q in questoes:
                st.markdown(f"**Enunciado:** {q['enunciado']}")
                for i, alt in enumerate(q['alternativas']):
                    st.markdown(f"{chr(65+i)}) {alt}")
                st.markdown("---")
        else:
            st.warning("Nenhuma questão encontrada para este cargo e matéria.")
    else:
        st.warning("Por favor, insira um cargo para realizar a busca.")

