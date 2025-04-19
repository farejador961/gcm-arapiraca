import csv
import json
import questionary

# 1. Carrega perguntas
with open("dados/perguntas.json") as f:
    perguntas = json.load(f)

# 2. Itera pelas questões
respostas = []
for q in perguntas:
    answer = questionary.select(
        q["texto"],
        choices=q["opcoes"]
    ).ask()
    correct = (answer == q["correta"])
    respostas.append({
        "módulo": q["modulo"],
        "acertou": correct
    })

# 3. Salva resultados
with open("dados/resultados.csv", "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["módulo","acertou"])
    writer.writerows(respostas)

# 4. Feedback rápido
acertos = sum(r["acertou"] for r in respostas)
total = len(respostas)
print(f"Você acertou {acertos}/{total} ({acertos/total*100:.1f}%)")
