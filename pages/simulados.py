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

        buscar = st.form_submit_button("🔍 Buscar Provas")

    def buscar_provas_ibam(banca=None, cargo=None, materia=None):
        url_base = "https://www.ibamsp-concursos.org.br/"
        url = url_base + "provas.php"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        provas_encontradas = []

        for item in soup.select("div.prova"):
            try:
                nome_banca = item.select_one(".banca").text.strip()
                nome_cargo = item.select_one(".cargo").text.strip()
                nome_materia = item.select_one(".materia").text.strip()
                link_prova = item.select_one("a[href]")["href"]

                if (not banca or banca.lower() in nome_banca.lower()) and \
                   (not cargo or cargo.lower() in nome_cargo.lower()) and \
                   (not materia or materia.lower() in nome_materia.lower()):
                    provas_encontradas.append({
                        "banca": nome_banca,
                        "cargo": nome_cargo,
                        "materia": nome_materia,
                        "link": url_base + link_prova
                    })
            except:
                continue

        return provas_encontradas

    if buscar:
        provas = buscar_provas_ibam(banca, cargo, materia)
        if not provas:
            st.warning("Nenhuma prova encontrada com esses filtros.")
        else:
            st.success(f"{len(provas)} prova(s) encontrada(s).")
            for prova in provas:
                st.markdown(f"### 📘 {prova['cargo']} - {prova['materia']}")
                st.markdown(f"**Banca:** {prova['banca']}")
                st.markdown(f"[📄 Acessar Prova]({prova['link']})")

# ---------------- TAB 2: Gerador de Questões ----------------
with tab2:
    st.subheader("Gerar questões avulsas por matéria e cargo")

    banca_sel = st.selectbox("Selecione a Fonte", ["PCI Concursos", "Concursos no Brasil"])
    cargo_sel = st.text_input("Cargo (opcional)")
    materia_sel = st.text_input("Matéria (opcional)")

    def buscar_questoes_concursosnobrasil(cargo=None, materia=None):
        base_url = "https://www.concursosnobrasil.com/questoes/"
        if cargo and materia:
            url = f"{base_url}{cargo}/{materia}/"
        elif cargo:
            url = f"{base_url}{cargo}/"
        else:
            url = base_url

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

    def buscar_questoes_pciconcursos(cargo):
        base_url = "https://www.pciconcursos.com.br/provas/ibam"
        url = f"{base_url}/1"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        questoes = []
        cargo_encontrado = False

        for question in soup.find_all('div', class_='questao'):
            try:
                titulo = question.find_previous('h2')
                if cargo and titulo and cargo.lower() in titulo.get_text(strip=True).lower():
                    cargo_encontrado = True
                if not cargo or cargo_encontrado:
                    enunciado = question.find('div', class_='pergunta').get_text(strip=True)
                    alternativas = [alt.get_text(strip=True) for alt in question.find_all('li')]
                    questoes.append({'enunciado': enunciado, 'alternativas': alternativas})
            except:
                continue

        return questoes, cargo_encontrado

    if st.button("🔍 Gerar Questões"):
        questoes = []
        cargo_encontrado = True

        if banca_sel == "PCI Concursos":
            questoes, cargo_encontrado = buscar_questoes_pciconcursos(cargo_sel)
        else:
            questoes = buscar_questoes_concursosnobrasil(cargo_sel, materia_sel)

        if questoes:
            if banca_sel == "PCI Concursos" and not cargo_encontrado and cargo_sel:
                st.info(f"Nenhuma questão encontrada especificamente para o cargo '{cargo_sel}'. Exibindo outras questões do IBAM semelhantes.")

            for q in questoes:
                st.markdown(f"**Enunciado:** {q['enunciado']}")
                for i, alt in enumerate(q['alternativas']):
                    st.markdown(f"{chr(65+i)}) {alt}")
                st.markdown("---")
        else:
            st.warning("Nenhuma questão encontrada.")

