import json
import pandas as pd
import re

# Caminho do arquivo JSON original
caminho_json = "seu_arquivo.json"

# Carregar conteúdo bruto
with open(caminho_json, "r", encoding="utf-8") as f:
    conteudo_bruto = f.read()

# Corrigir trechos com dicionários aninhados dentro de listas
conteudo_corrigido = re.sub(r',?\s*\{\s*"[^"]+":\s*\[.*?\]\s*\}', '', conteudo_bruto, flags=re.DOTALL)

# Tentar carregar JSON corrigido
try:
    dados_originais = json.loads(conteudo_corrigido)
except json.JSONDecodeError as e:
    print("Erro no JSON:", e)
    exit()

# Processar perguntas e organizar IDs únicos
perguntas_final = []
respostas_csv = []
id_unico = 1

for modulo, perguntas in dados_originais.get("modulos", {}).items():
    if isinstance(perguntas, list):
        for p in perguntas:
            if isinstance(p, dict) and all(k in p for k in ["pergunta", "alternativas", "resposta_correta"]):
                nova_pergunta = {
                    "id": id_unico,
                    "modulo": modulo,
                    "pergunta": p["pergunta"],
                    "alternativas": p["alternativas"],
                    "resposta_correta": p["resposta_correta"]
                }
                perguntas_final.append(nova_pergunta)
                respostas_csv.append({"id": id_unico, "resposta_correta": p["resposta_correta"]})
                id_unico += 1

# Salvar JSON corrigido
with open("perguntas_corrigidas.json", "w", encoding="utf-8") as f:
    json.dump(perguntas_final, f, ensure_ascii=False, indent=4)

# Salvar CSV com respostas
df_respostas = pd.DataFrame(respostas_csv)
df_respostas.to_csv("respostas.csv", index=False, encoding="utf-8")

print("Arquivos gerados: perguntas_corrigidas.json e respostas.csv")
