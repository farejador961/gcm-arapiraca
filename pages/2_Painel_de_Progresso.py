import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Painel de Progresso - GCM", layout="wide")
st.title("📚 Acompanhamento de Estudos - GCM Arapiraca")

# ✅ Verifica e cria o arquivo de resultados, se necessário
if not os.path.exists("dados/resultados.csv"):
    os.makedirs("dados", exist_ok=True)
    df_vazio = pd.DataFrame(columns=["data", "módulo", "acertou", "total"])
    df_vazio.to_csv("dados/resultados.csv", index=False)

# Carregar dados
cronograma = pd.read_csv("cronograma.csv")
resultados = pd.read_csv("dados/resultados.csv")

# Agrupar por módulo
acertos_modulo = resultados.groupby("módulo")["acertou"].mean().reset_index()
acertos_modulo["% Acerto"] = (acertos_modulo["acertou"] * 100).round(1)

# Mapear % de acerto no cronograma
def calcular_media_modulos(mod_str):
    mod_str = mod_str.replace(" ", "")
    if "–" in mod_str:
        inicio, fim = mod_str.split("–")
        try:
            modulos = list(map(str, range(int(inicio), int(fim)+1)))
        except:
            return None
    elif "e" in mod_str:
        modulos = mod_str.split("e")
    else:
        modulos = [mod_str]
    
    filtro = acertos_modulo[acertos_modulo["módulo"].isin(modulos)]
    return filtro["% Acerto"].mean() if not filtro.empty else None

cronograma["% Real"] = cronograma["Módulos"].apply(calcular_media_modulos)

# 📊 Comparativo metas vs real
st.subheader("🎯 Metas vs. Desempenho Real")
st.dataframe(cronograma[["Semana", "Período", "Módulos", "Meta (%)", "% Real"]])

# 🔥 Feedback motivacional
st.subheader("💬 Feedback por Semana")
for _, row in cronograma.iterrows():
    meta = row["Meta (%)"]
    real = row["% Real"]
    semana = row["Semana"]
    if pd.notnull(real):
        if real >= meta:
            st.success(f"✅ Semana {semana}: Meta superada! ({real:.1f}% ≥ {meta}%)")
        else:
            st.warning(f"⚠️ Semana {semana}: Ainda não atingiu a meta ({real:.1f}% < {meta}%)")

# 📈 Gráfico de progresso
st.subheader("📈 Evolução Semanal")
fig, ax = plt.subplots()
ax.plot(cronograma["Semana"].astype(str), cronograma["Meta (%)"], label="Meta", linestyle="--", marker="o")
ax.plot(cronograma["Semana"].astype(str), cronograma["% Real"], label="% Real", marker="o")
ax.set_ylabel("% de Acertos")
ax.set_xlabel("Semana")
ax.legend()
st.pyplot(fig)

# ❗ Módulos com maior taxa de erro
st.subheader("🧠 Módulos com Maior Necessidade de Revisão")
mod_dificeis = acertos_modulo[acertos_modulo["% Acerto"] < 75].sort_values("% Acerto")

if mod_dificeis.empty:
    st.success("Parabéns! Nenhum módulo crítico identificado!")
else:
    st.warning("⚠️ Os seguintes módulos estão abaixo de 75% de acerto:")
    st.dataframe(mod_dificeis[["módulo", "% Acerto"]])
    for _, row in mod_dificeis.iterrows():
        st.markdown(f"- **Módulo {row['módulo']}**: reforce teoria, pratique mais exercícios e revise os erros frequentes.")
# ➕ Registro manual de acertos
st.subheader("📝 Registrar Novo Resultado")

with st.form("form_registro"):
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data do estudo")
        modulo = st.text_input("Módulo (ex: 1, 2, 3...)")
    with col2:
        acertos = st.number_input("Número de acertos", min_value=0, step=1)
        total = st.number_input("Total de questões", min_value=1, step=1)

    submitted = st.form_submit_button("Salvar Resultado")

    if submitted:
        novo_resultado = pd.DataFrame([{
            "data": data,
            "módulo": str(modulo),
            "acertou": round(acertos / total, 2),
            "total": total
        }])
        resultados = pd.concat([resultados, novo_resultado], ignore_index=True)
        resultados.to_csv("dados/resultados.csv", index=False)
        st.success("✅ Resultado registrado com sucesso! Atualize a página para visualizar os novos dados.")

# 🗑️ Botão para resetar os resultados
st.subheader("⚙️ Gerenciar Dados")

if st.button("❌ Resetar todos os resultados"):
    resultados_vazio = pd.DataFrame(columns=["data", "módulo", "acertou", "total"])
    resultados_vazio.to_csv("dados/resultados.csv", index=False)
    st.warning("Todos os resultados foram apagados. A planilha agora está limpa.")
