import pandas as pd

# Definindo o cronograma
cronograma_data = [
    {"Semana": 1, "Período": "19/04–25/04", "Módulos": "1 e 2", "Horas/dia": "4h", 
     "Blocos de estudo": "Bloco 1: Teoria; Bloco 2: Exercícios", "Simulado": "Sábado", "Meta (%)": 25},
    {"Semana": 2, "Período": "26/04–02/05", "Módulos": "3 e 4", "Horas/dia": "4h", 
     "Blocos de estudo": "Bloco 1: Teoria; Bloco 2: Exercícios", "Simulado": "Sábado", "Meta (%)": 35},
    {"Semana": 3, "Período": "03/05–09/05", "Módulos": "5 e 6", "Horas/dia": "4h", 
     "Blocos de estudo": "Bloco 1: Teoria; Bloco 2: Exercícios", "Simulado": "Sábado", "Meta (%)": 45},
    {"Semana": 4, "Período": "10/05–16/05", "Módulos": "7 e 8", "Horas/dia": "4h", 
     "Blocos de estudo": "Bloco 1: Teoria; Bloco 2: Exercícios", "Simulado": "Sábado", "Meta (%)": 55},
    {"Semana": 5, "Período": "17/05–23/05", "Módulos": "9 e 10", "Horas/dia": "4h", 
     "Blocos de estudo": "Bloco 1: Teoria; Bloco 2: Exercícios", "Simulado": "Sábado", "Meta (%)": 65},
    {"Semana": 6, "Período": "24/05–30/05", "Módulos": "11 e 12", "Horas/dia": "4h", 
     "Blocos de estudo": "Bloco 1: Teoria; Bloco 2: Exercícios", "Simulado": "Sábado", "Meta (%)": 75},
    {"Semana": 7, "Período": "31/05–06/06", "Módulos": "Revisão 1–12", "Horas/dia": "4h", 
     "Blocos de estudo": "Revisão teórica & exercícios mistos", "Simulado": "Sábado", "Meta (%)": 85},
    {"Semana": 8, "Período": "07/06–13/06", "Módulos": "Foco em pontos fracos", "Horas/dia": "4h", 
     "Blocos de estudo": "Revisão direcionada", "Simulado": "Sábado", "Meta (%)": 95},
    {"Semana": "Pré-prova", "Período": "14/06", "Módulos": "Flashcards & mapas mentais", "Horas/dia": "4h", 
     "Blocos de estudo": "Revisão leve", "Simulado": "—", "Meta (%)": 100},
    {"Semana": "Prova", "Período": "15/06", "Módulos": "—", "Horas/dia": "—", 
     "Blocos de estudo": "Descanso & confiança", "Simulado": "—", "Meta (%)": 100}
]

# Criando o DataFrame
cronograma_df = pd.DataFrame(cronograma_data)

# Salvando o DataFrame como CSV
cronograma_df.to_csv('cronograma.csv', index=False)

print("Cronograma CSV gerado com sucesso!")
