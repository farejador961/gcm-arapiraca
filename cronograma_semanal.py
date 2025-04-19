import pandas as pd
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# Dados estruturados do cronograma
cronograma = [
    ["Segunda", "Português, Informática", "1h + 1h", "30min + 30min", "Reforçar interpretação de texto e sistemas"],
    ["Terça", "Direito Penal, Direito Constitucional", "1h + 1h", "30min + 30min", "Priorizar artigos do CP e CF"],
    ["Quarta", "Direitos Humanos, Legislação GCM", "1h + 1h", "30min + 30min", "Revisar Leis nº 13.022 e 13.675"],
    ["Quinta", "RLM, Atualidades", "1h + 1h", "30min + 30min", "Resolver questões de concursos anteriores"],
    ["Sexta", "Direito Administrativo, Código Penal", "1h + 1h", "30min + 30min", "Revisar jurisprudência e doutrina"],
    ["Sábado", "Simulado Geral", "—", "2h30min", "Corrigir e revisar erros do simulado"],
    ["Domingo", "Revisão da Semana, Leitura Leve", "1h", "1h", "Leituras de apoio + descanso mental"],
]

# Criar DataFrame
columns = ["Dia da Semana", "Matérias", "Tempo de Teoria", "Tempo de Exercícios", "Observações"]
df = pd.DataFrame(cronograma, columns=columns)

# Salvar como Excel
excel_path = "/mnt/data/Plano_Estudos_Semanal_GCM.xlsx"
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name="Plano de Estudos", index=False)

excel_path