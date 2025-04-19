import streamlit as st
import os
import pandas as pd
from datetime import datetime
from PyPDF2 import PdfReader
import requests

# Configuração da página
st.set_page_config(page_title="📘 Simulados Inteligentes", layout="wide")
st.title("🎯 Simulados Inteligentes")

# Pastas para armazenamento
PASTA_PROVAS = "dados/provas/"
PASTA_GABARITOS = "dados/gabaritos/"
PASTA_RESULTADOS = "dados/resultados/"
os.makedirs(PASTA_PROVAS, exist_ok=True)
os.makedirs(PASTA_GABARITOS, exist_ok=True)
os.makedirs(PASTA_RESULTADOS, exist_ok=True)

# Inputs iniciais
with st.form("formulario_simulado"):
    nome_aluno = st.text_input("Seu nome completo")
    numero_simulado = st.text_input("Número do Simulado (ex: 001)")
    link_prova = st.text_input("Link para download do PDF da Prova")
    link_gabarito = st.text_input("Link para download do PDF do Gabarito")

    upload_prova = st.file_uploader("Ou envie a prova em PDF", type="pdf")
    upload_gabarito = st.file_uploader("Ou envie o gabarito em PDF", type="pdf")

    iniciar = st.form_submit_button("📥 Enviar e Corrigir")

# Função para baixar e salvar arquivos PDF
def salvar_pdf_via_link(url, pasta, nome_base):
    response = requests.get(url)
    caminho = os.path.join(pasta, f"{nome_base}.pdf")
    with open(caminho, "wb") as f:
        f.write(response.content)
    return caminho

# Função para salvar uploads manuais
def salvar_upload_pdf(arquivo, pasta, nome_base):
    caminho = os.path.join(pasta, f"{nome_base}.pdf")
    with open(caminho, "wb") as f:
        f.write(arquivo.read())
    return caminho

# Função para extrair respostas de um PDF
def extrair_respostas_pdf(caminho_pdf):
    respostas = []
    try:
        leitor = PdfReader(caminho_pdf)
        for pagina in leitor.pages:
            texto = pagina.extract_text()
            for linha in texto.splitlines():
                if linha.strip()[:2].isdigit():  # ex: "01 A"
                    partes = linha.strip().split()
                    if len(partes) >= 2:
                        respostas.append(partes[1].upper())
        return respostas
    except Exception as e:
        st.error(f"Erro ao extrair respostas: {e}")
        return []

# Correção da prova
def corrigir_respostas(respostas_aluno, respostas_gabarito):
    acertos = sum(1 for r, g in zip(respostas_aluno, respostas_gabarito) if r == g)
    total = len(respostas_gabarito)
    percentual = round((acertos / total) * 100, 2) if total > 0 else 0
    return acertos, total, percentual

# Processamento
if iniciar and nome_aluno and numero_simulado:
    nome_base = f"{nome_aluno.replace(' ', '_')}_simulado_{numero_simulado}"

    # Salvar prova
    if link_prova:
        caminho_prova = salvar_pdf_via_link(link_prova, PASTA_PROVAS, nome_base)
    elif upload_prova:
        caminho_prova = salvar_upload_pdf(upload_prova, PASTA_PROVAS, nome_base)
    else:
        st.warning("Envie ou cole o link da prova.")
        caminho_prova = None

    # Salvar gabarito
    if link_gabarito:
        caminho_gabarito = salvar_pdf_via_link(link_gabarito, PASTA_GABARITOS, nome_base)
    elif upload_gabarito:
        caminho_gabarito = salvar_upload_pdf(upload_gabarito, PASTA_GABARITOS, nome_base)
    else:
        st.warning("Envie ou cole o link do gabarito.")
        caminho_gabarito = None

    # Correção e salvamento
    if caminho_prova and caminho_gabarito:
        respostas_aluno = extrair_respostas_pdf(caminho_prova)
        respostas_gabarito = extrair_respostas_pdf(caminho_gabarito)

        acertos, total, percentual = corrigir_respostas(respostas_aluno, respostas_gabarito)

        st.success(f"🎉 Você acertou {acertos} de {total} ({percentual}%)")

        # Salvar resultado
        resultado = {
            "nome": nome_aluno,
            "simulado": numero_simulado,
            "acertos": acertos,
            "total": total,
            "percentual": percentual,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        df_resultado = pd.DataFrame([resultado])
        resultado_csv = os.path.join(PASTA_RESULTADOS, f"{nome_base}.csv")
        df_resultado.to_csv(resultado_csv, index=False)

        # Adiciona ao CSV geral se quiser usar no painel
        geral_csv = os.path.join("dados", "resultados.csv")
        if os.path.exists(geral_csv):
            df_geral = pd.read_csv(geral_csv)
            df_geral = pd.concat([df_geral, df_resultado], ignore_index=True)
        else:
            df_geral = df_resultado
        df_geral.to_csv(geral_csv, index=False)

        st.success("✅ Resultado salvo e integrado ao painel de progresso!")

