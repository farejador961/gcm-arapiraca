import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Simulados Inteligentes", layout="wide")
st.title("🎯 Simulados Inteligentes")

# ---------------- FORMULÁRIO DE BUSCA POR Banca IBAM ----------------
with st.form("busca_simulados"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Banca: IBAM** (fixo para esta versão)")
        banca = "ibam"  # Fixo
    with col2:
        materia = st.text_input("Matéria (opcional)")

    buscar = st.form_submit_button("🔍 Listar Provas da Banca IBAM")

# Função para buscar provas da banca IBAM
def buscar_provas_ibam():
    url = f"https://www.pciconcursos.com.br/provas/ibam"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    provas = []

    for link in soup.select('a[href^="/provas/"]'):
        nome_prova = link.get_text(strip=True)
        url_prova = "https://www.pciconcursos.com.br" + link.get('href')
        if nome_prova and url_prova not in [p['url'] for p in provas]:
            provas.append({"nome": nome_prova, "url": url_prova})
    return provas


# Função para buscar questões de uma prova específica
def buscar_questoes_da_prova(url_prova, filtro_materia=None):
    response = requests.get(url_prova)
    soup = BeautifulSoup(response.text, 'html.parser')

    questoes = []
    for question in soup.find_all('div', class_='questao'):
        try:
            enunciado = question.find('div', class_='pergunta').get_text(strip=True)
            alternativas = [alt.get_text(strip=True) for alt in question.find_all('li')]

            if filtro_materia:
                if filtro_materia.lower() in enunciado.lower():
                    questoes.append({'enunciado': enunciado, 'alternativas': alternativas})
            else:
                questoes.append({'enunciado': enunciado, 'alternativas': alternativas})
        except:
            continue
    return questoes

# --------------- PROCESSAMENTO -------------------
if buscar:
    provas = buscar_provas_ibam()
    if provas:
        st.success(f"{len(provas)} prova(s) encontradas da banca IBAM.")
        nomes_provas = [p['nome'] for p in provas]
        prova_selecionada = st.selectbox("📄 Selecione a prova que deseja visualizar:", nomes_provas)

        if prova_selecionada:
            prova_url = next(p['url'] for p in provas if p['nome'] == prova_selecionada)
            mostrar = st.button("📘 Mostrar Questões da Prova Selecionada")
            if mostrar:
                questoes = buscar_questoes_da_prova(prova_url, materia)
                if questoes:
                    for idx, q in enumerate(questoes, 1):
                        st.markdown(f"### Questão {idx}")
                        st.markdown(f"**Enunciado:** {q['enunciado']}")
                        for i, alt in enumerate(q['alternativas']):
                            st.markdown(f"{chr(65+i)}) {alt}")
                        st.markdown("---")
                else:
                    st.warning("⚠️ Nenhuma questão encontrada nesta prova (ou filtro de matéria muito restrito).")
    else:
        st.warning("⚠️ Nenhuma prova encontrada para a banca IBAM.")
