import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Simulados Inteligentes", layout="wide")
st.title("🎯 Simulados Inteligentes")

tab1, tab2 = st.tabs(["📘 Buscar Provas IBAM", "📝 Gerador de Questões (IBAM & PCI)"])

# ---------------- TAB 1: Provas IBAM ----------------
with tab1:
    with st.form("busca_simulados"):
        col1, col2, col3 = st.columns(3)
        with col1:
            banca = st.text_input("Nome da Banca", value="IBAM")
        with col2:
            cargo = st.text_input("Cargo (ex: Guarda Municipal)")
        with col3:
            materia = st.text_input("Matéria (opcional)")
        ano = st.text_input("Ano (opcional)")

        buscar = st.form_submit_button("🔍 Buscar Provas")

    def buscar_provas_ibam(banca=None, cargo=None, materia=None, ano=None):
        url_base = "https://www.ibamsp-concursos.org.br/"
        url = url_base + "provas.php"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        provas_encontradas = []

        # Simulação de scraping — adaptar conforme HTML real
        for item in soup.select("div.prova"):
            try:
                nome_banca = item.select_one(".banca").text.strip()
                nome_cargo = item.select_one(".cargo").text.strip()
                nome_materia = item.select_one(".materia").text.strip()
                nome_ano = item.select_one(".ano").text.strip() if item.select_one(".ano") else ""
                link_prova = item.select_one("a[href]")["href"]

                if (not banca or banca.lower() in nome_banca.lower()) and \
                   (not cargo or cargo.lower() in nome_cargo.lower()) and \
                   (not materia or materia.lower() in nome_materia.lower()) and \
                   (not ano or ano in nome_ano):
                    provas_encontradas.append({
                        "banca": nome_banca,
                        "cargo": nome_cargo,
                        "materia": nome_materia,
                        "ano": nome_ano,
                        "link": url_base + link_prova
                    })
            except:
                continue

        return provas_encontradas

    if buscar:
        provas = buscar_provas_ibam(banca, cargo, materia, ano)
        if not provas:
            st.warning("Nenhuma prova encontrada com esses filtros.")
        else:
            st.success(f"{len(provas)} prova(s) encontrada(s).")
            for prova in provas:
                st.markdown(f"### 📘 {prova['cargo']} - {prova['materia']} ({prova['ano']})")
                st.markdown(f"**Banca:** {prova['banca']}")
                st.markdown(f"[📄 Acessar Prova]({prova['link']})")
                st.markdown("---")

# ---------------- TAB 2: Gerador de Questões ----------------
with tab2:
    st.subheader("Gerar questões avulsas por matéria, cargo e ano")

    banca_sel = st.selectbox("Selecione a Fonte", ["PCI Concursos", "Concursos no Brasil"])
    cargo_sel = st.text_input("Cargo")
    materia_sel = st.text_input("Matéria")
    ano_sel = st.text_input("Ano (opcional)")

    def buscar_questoes_pciconcursos(cargo):
        url = f"https://www.pciconcursos.com.br/provas/{cargo}/1"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        questoes = []
        for question in soup.find_all('div', class_='questao'):
            try:
                enunciado = question.find('div', class_='pergunta').get_text(strip=True)
                alternativas = [alt.get_text(strip=True) for alt in question.find_all('li')]
                resposta_correta = alternativas[0]  # Simulado: marcar primeira como correta
                questoes.append({'enunciado': enunciado, 'alternativas': alternativas, 'resposta': resposta_correta})
            except:
                continue
        return questoes

    def buscar_questoes_concursosnobrasil(cargo, materia):
        url = f"https://www.concursosnobrasil.com/questoes/{cargo}/{materia}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        questoes = []
        for question in soup.find_all('div', class_='questao'):
            try:
                enunciado = question.find('div', class_='enunciado').get_text(strip=True)
                alternativas = [alt.get_text(strip=True) for alt in question.find_all('li')]
                resposta_correta = alternativas[0]  # Simulado
                questoes.append({'enunciado': enunciado, 'alternativas': alternativas, 'resposta': resposta_correta})
            except:
                continue
        return questoes

    if st.button("🔍 Gerar Questões"):
        if banca_sel == "PCI Concursos":
            questoes = buscar_questoes_pciconcursos(cargo_sel)
        else:
            questoes = buscar_questoes_concursosnobrasil(cargo_sel, materia_sel)

        if questoes:
            st.success(f"{len(questoes)} questão(ões) carregadas!")
            for i, q in enumerate(questoes):
                with st.expander(f"Questão {i+1}"):
                    st.markdown(f"**Enunciado:** {q['enunciado']}")
                    resposta_usuario = st.radio("Escolha uma alternativa:", q['alternativas'], key=f"questao_{i}")
                    if st.button("Verificar Resposta", key=f"verificar_{i}"):
                        if resposta_usuario == q['resposta']:
                            st.success("✅ Resposta correta!")
                        else:
                            st.error(f"❌ Resposta incorreta. Resposta correta: {q['resposta']}")
        else:
            st.warning("Nenhuma questão encontrada.")
