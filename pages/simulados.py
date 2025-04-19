import streamlit as st
import requests
import os
import csv
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simulados Inteligentes", layout="wide")
st.title("🎯 Simulados Inteligentes")

# Criação das pastas caso não existam
os.makedirs("uploads/provas", exist_ok=True)
os.makedirs("uploads/gabaritos", exist_ok=True)
os.makedirs("dados", exist_ok=True)

# Formulário de Envio
with st.form("form_envio"):
    st.subheader("📤 Enviar ou Escolher Prova e Gabarito")

    nome = st.text_input("👤 Seu nome completo")
    simulado_id = st.text_input("🧾 Número do simulado (ex: 1, 2...)")
    url_prova = st.text_input("🔗 Link do PDF da PROVA")
    url_gabarito = st.text_input("🔗 Link do PDF do GABARITO")

    enviar = st.form_submit_button("⬇️ Baixar e Armazenar")

# Nome base dos arquivos
def gerar_nome_arquivo(nome, simulado_id, tipo):
    nome_limpo = nome.replace(" ", "_").lower()
    if tipo == "prova":
        return f"uploads/provas/{nome_limpo}_simulado{simulado_id}.pdf"
    elif tipo == "gabarito":
        return f"uploads/gabaritos/{nome_limpo}_simulado{simulado_id}_gabarito.pdf"

# Função para salvar uploads manuais
def salvar_upload_pdf(arquivo, pasta, nome_base):
    caminho = os.path.join(pasta, f"{nome_base}.pdf")
    with open(caminho, "wb") as f:
        f.write(arquivo.read())
    return caminho

# Baixa e salva o PDF de uma URL
def baixar_pdf(url, destino):
    try:
        response = requests.get(url)
        with open(destino, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        st.error(f"Erro ao baixar {destino}: {e}")
        return False

# Formulário de Envio
with st.form("form_envio"):
    st.subheader("📤 Enviar ou Escolher Prova e Gabarito")

    nome = st.text_input("👤 Seu nome completo")
    simulado_id = st.text_input("🧾 Número do simulado (ex: 1, 2...)")

    st.markdown("**🔗 Ou informe os links abaixo (opcional):**")
    url_prova = st.text_input("🔗 Link do PDF da PROVA")
    url_gabarito = st.text_input("🔗 Link do PDF do GABARITO")

    st.markdown("**📁 Ou envie os arquivos diretamente do seu computador:**")
    arquivo_prova = st.file_uploader("📄 Envie o PDF da PROVA", type=["pdf"])
    arquivo_gabarito = st.file_uploader("📄 Envie o PDF do GABARITO", type=["pdf"])

    enviar = st.form_submit_button("📥 Armazenar Arquivos")

# Processamento do envio
if enviar and nome and simulado_id:
    nome_limpo = nome.lower().replace(" ", "_")
    nome_prova = f"{nome_limpo}_simulado{simulado_id}"
    nome_gabarito = f"{nome_prova}_gabarito"

    caminho_prova = f"uploads/provas/{nome_prova}.pdf"
    caminho_gabarito = f"uploads/gabaritos/{nome_gabarito}.pdf"

    sucesso_prova, sucesso_gabarito = False, False

    if url_prova:
        sucesso_prova = baixar_pdf(url_prova, caminho_prova)
    elif arquivo_prova:
        salvar_upload_pdf(arquivo_prova, "uploads/provas", nome_prova)
        sucesso_prova = True

    if url_gabarito:
        sucesso_gabarito = baixar_pdf(url_gabarito, caminho_gabarito)
    elif arquivo_gabarito:
        salvar_upload_pdf(arquivo_gabarito, "uploads/gabaritos", nome_gabarito)
        sucesso_gabarito = True

    if sucesso_prova and sucesso_gabarito:
        st.success("✅ Prova e gabarito armazenados com sucesso!")
    elif sucesso_prova or sucesso_gabarito:
        st.warning("⚠️ Apenas um dos arquivos foi salvo com sucesso.")
    else:
        st.error("❌ Nenhum arquivo foi salvo. Verifique as entradas.")
elif enviar:
    st.error("❗ Preencha o nome e número do simulado.")


# Extrai texto de PDF
def extrair_texto_pdf(caminho):
    with open(caminho, "rb") as f:
        reader = PdfReader(f)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
        return texto

# Corrige a prova
def corrigir_prova(respostas_usuario, gabarito_correto):
    acertos = 0
    total = len(gabarito_correto)
    for user, correto in zip(respostas_usuario, gabarito_correto):
        if user.upper() == correto.upper():
            acertos += 1
    return acertos, total

# Salva os resultados
def salvar_resultado(nome, simulado_id, acertos, total):
    percentual = round((acertos / total) * 100, 2) if total > 0 else 0
    caminho_csv = "dados/resultados.csv"
    existe = os.path.exists(caminho_csv)

    with open(caminho_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["nome", "simulado", "acertos", "total", "percentual"])
        writer.writerow([nome, simulado_id, acertos, total, percentual])
    return percentual

# Processamento do envio
if enviar and nome and simulado_id and url_prova and url_gabarito:
    prova_path = gerar_nome_arquivo(nome, simulado_id, "prova")
    gabarito_path = gerar_nome_arquivo(nome, simulado_id, "gabarito")

    sucesso1 = baixar_pdf(url_prova, prova_path)
    sucesso2 = baixar_pdf(url_gabarito, gabarito_path)

    if sucesso1 and sucesso2:
        st.success("📥 Prova e gabarito baixados com sucesso!")
    else:
        st.error("❌ Falha ao baixar os arquivos.")

# Mostrar provas disponíveis
st.subheader("📚 Provas Armazenadas")
provas_disponiveis = os.listdir("uploads/provas")
provas_nomes = [p.replace(".pdf", "").replace("_", " ").title() for p in provas_disponiveis]

if provas_nomes:
    selecionada = st.selectbox("Escolha uma prova para responder:", provas_nomes)
    if selecionada:
        nome_arquivo = provas_disponiveis[provas_nomes.index(selecionada)]
        nome_usuario, simulado_id = nome_arquivo.replace(".pdf", "").split("_simulado")
        prova_path = gerar_nome_arquivo(nome_usuario, simulado_id, "prova")
        gabarito_path = gerar_nome_arquivo(nome_usuario, simulado_id, "gabarito")

        if os.path.exists(prova_path) and os.path.exists(gabarito_path):
            st.subheader(f"📝 Responder Simulado {simulado_id} - {nome_usuario.title()}")

            texto_prova = extrair_texto_pdf(prova_path)
            texto_gabarito = extrair_texto_pdf(gabarito_path)

            # Extrair gabarito (exemplo: A B C D A ...)
            gabarito_lista = texto_gabarito.strip().split()
            total_questoes = len(gabarito_lista)

            st.info(f"Total de questões: {total_questoes}")

            respostas_usuario = []
            for i in range(total_questoes):
                resposta = st.radio(f"Questão {i+1}", ["A", "B", "C", "D", "E"], key=f"q_{i}")
                respostas_usuario.append(resposta)

            if st.button("✅ Corrigir"):
                acertos, total = corrigir_prova(respostas_usuario, gabarito_lista)
                percentual = salvar_resultado(nome_usuario, simulado_id, acertos, total)

                st.success(f"🎉 Você acertou {acertos} de {total} ({percentual}%)")
                st.info("📊 Seus dados foram enviados ao painel de progresso!")
else:
    st.warning("Nenhuma prova armazenada ainda.")


