from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Módulos alinhados ao edital da GCM Arapiraca (sem discrepâncias)
modules = [
    {
        "number": 1,
        "title": "Lei Orgânica do Município",
        "submodules": [
            {
                "title": "1.1 Conteúdos",
                "content": (
                    "- Posição do Município na Federação brasileira\n"
                    "- Características, princípios e fundamentos\n"
                    "- Conceitos de autonomia municipal e participação popular\n"
                    "- Competências privativas do Município\n"
                    "- Organização: administração direta e indireta\n"
                    "- Poderes municipais: Executivo e Legislativo\n"
                    "- Prefeito: posse, funções, atribuições e responsabilidades\n"
                    "- Câmara Municipal: funções legislativas, administrativas e fiscalizadoras\n"
                    "- Orçamento público e bens municipais"
                ),
                "example": "Analise como o orçamento municipal impacta serviços de segurança comunitária.",
                "exercise": "Explique a diferença entre administração direta e indireta.",
                "references": "Lei Orgânica de Arapiraca; CF art. 144, §8º. CF art 18,19,22,23,24,28,29 e 30", 
            },
        ]
    },
    {
        "number": 2,
        "title": "Lei nº 13.675/2018 e PNPSD",
        "submodules": [
            {
                "title": "2.1 Conteúdos",
                "content": (
                    "- Criação da Política Nacional de Segurança Pública e Defesa Social\n"
                    "- Instituição do Sistema Único de Segurança Pública (SUSP)\n"
                    "- Diretrizes de integração e cooperação entre entes federados"
                ),
                "example": "Descreva uma operação que envolva SUSP e Guarda Municipal.",
                "exercise": "Liste dois objetivos fundamentais da PNPSD.",
                "references": "Lei 13.675/2018."
            }
        ]
    },
    {
        "number": 3,
        "title": "Estatuto Geral das Guardas Municipais",
        "submodules": [
            {
                "title": "3.1 Conteúdos",
                "content": (
                    "- Lei 13.022/2014: organização e atribuições das GM\n"
                    "- Cooperação com forças de segurança da União, Estados e DF\n"
                    "- Decreto 11.841/2023: regulamentação dos incisos IV, XIII e XIV do art. 5º"
                ),
                "example": "Exemplo de cooperação GM + Polícia Civil em evento público.",
                "exercise": "Cite três competências privativas da GM segundo o Estatuto.",
                "references": "Lei 13.022/2014; Decreto 11.841/2023."
            }
        ]
    },
    {
        "number": 4,
        "title": "Organização, Comando e Controle e Plano de Carreira",
        "submodules": [
            {
                "title": "4.1 Conteúdos",
                "content": (
                    "- Aspectos e princípios de organização interna\n"
                    "- Estrutura hierárquica e cadeia de comando\n"
                    "- Plano de carreira, cargos e vencimentos (Lei Complementar 05/2024)"
                ),
                "example": "Fluxograma de comando em operações especiais.",
                "exercise": "Descreva as etapas de promoção na carreira da GM.",
                "references": "Lei de Criação da GCM-Arapiraca,LC 05/2024, Capítulos I–VIII."
            }
        ]
    },
    {
        "number": 5,
        "title": "Poder de Polícia Administrativa",
        "submodules": [
            {
                "title": "5.1 Conteúdos",
                "content": (
                    "- Conceitos, fundamentos e requisitos legais\n"
                    "- Meios de atuação e sanções administrativas\n"
                    "- Áreas de aplicação (uso do solo, posturas, fiscalizações)"
                ),
                "example": "Caso de aplicação de multa ambiental pela GM.",
                "exercise": "Liste três requisitos para o exercício do poder de polícia.",
                "references": "CF Art. 78; Lei 9.784/1999."
            }
        ]
    },
    {
        "number": 6,
        "title": "Atos Administrativos",
        "submodules": [
            {
                "title": "6.1 Conteúdos",
                "content": (
                    "- Conceito e classificação de atos administrativos\n"
                    "- Espécies: normativos, ordinatórios, negociais, enunciativos e punitivos\n"
                    "- Requisitos de validade e efeitos"
                ),
                "example": "Exemplo de ato normativo municipal (decreto).",
                "exercise": "Diferencie ato ordinatório de ato normativo.",
                "references": "Lei 9.784/1999. Art. 2º: Define os princípios gerai,Arts.3,22,69A,50,53,56,65"
            }
        ]
    },
    {
        "number": 7,
        "title": "Protocolo e Gerenciamento de Documentos e Processos",
        "submodules": [
            {
                "title": "7.1 Conteúdos",
                "content": (
                    "- Tramitação, distribuição e expedição de documentos\n"
                    "- Autuação, instrução e encerramento de volumes\n"
                    "- Apensação, desentranhamento, reabertura e extinção de processos"
                ),
                "example": "Como elaborar um processo administrativo completo.",
                "exercise": "Enumere as fases de um processo administrativo.",
                "references": "Manual interno da GM Arapiraca."
            }
        ]
    },
    {
        "number": 8,
        "title": "Legislação de Proteção e Estatutos Específicos",
        "submodules": [
            {
                "title": "8.1 Conteúdos",
                "content": (
                    "- Lei de Abuso de Autoridade (Lei 13.869/2019)\n"
                    "- Lei Maria da Penha (Lei 11.340/2006)\n"
                    "- Estatuto da Criança e do Adolescente (ECA)\n"
                    "- Estatuto do Idoso\n"
                    "- Estatuto da Pessoa com Deficiência\n"
                    "- Estatuto da Igualdade Racial"
                ),
                "example": "Intervenção GM em situação de violência doméstica.",
                "exercise": "Cite dois direitos garantidos pelo ECA.",
                "references": "Leis citadas."
            }
        ]
    },
    {
        "number": 9,
        "title": "Crimes contra a Administração Pública",
        "submodules": [
            {
                "title": "9.1 Conteúdos",
                "content": (
                    "- Art. 312 a 327 CP: crimes praticados por funcionário público\n"
                    "- Art. 328 a 337 CP: crimes por particulares contra a administração"
                ),
                "example": "Estudo de caso: peculato e corrupção ativa.",
                "exercise": "Diferencie peculato de corrupção ativa.",
                "references": "Código Penal, Arts. 312–337."
            }
        ]
    },
    {
        "number": 10,
        "title": "Noções de Direito Constitucional",
        "submodules": [
            {
                "title": "10.1 Conteúdos",
                "content": (
                    "- Estudar art. 3 ao 23, art. 87 ao 102. Além disso, As observaões a baixo."
                    "- Classificação das constituições\n"
                    "- Direitos e garantias fundamentais\n"
                    "- Organização dos Poderes (Executivo, Legislativo, Judiciário)\n"
                    "- Sistema Tributário Nacional\n"
                    "- Controle de constitucionalidade\n"
                    "- Jurisprudência do STF e STJ"
                ),
                "example": "Análise de acórdão STJ sobre controle difuso.",
                "exercise": "Explique a diferença entre controle difuso e concentrado.",
                "references": "CF/88, Títulos I–III; Jurisprudência selecionada."
            }
        ]
    },
    {
        "number": 11,
        "title": "Língua Portuguesa",
        "submodules": [
            {
                "title": "11.1 Conteúdos",
                "content": (
                    "- Leitura e compreensão de textos\n"
                    "- Coesão, coerência e conectivos\n"
                    "- Classes e funções de palavras\n"
                    "- Regência, concordância e crase\n"
                    "- Acentuação gráfica e pontuação\n"
                    "- Sintaxe do período simples e composto\n"
                    "- Figuras de linguagem"
                ),
                "example": "Identifique as figuras de linguagem em um texto jornalístico.",
                "exercise": "Corrija erros de regência em frases abaixo.",
                "references": "Gramáticas normativas; Manual de Redação Oficial."
            }
        ]
    },
    {
        "number": 12,
        "title": "Conhecimentos Gerais sobre o Município de Arapiraca",
        "submodules": [
            {
                "title": "12.1 Conteúdos",
                "content": (
                    "- Origem e primeiras ocupações\n"
                    "- Evolução histórica e conflitos\n"
                    "- Aspectos físicos e geográficos\n"
                    "- Indicadores socioeconômicos e educacionais\n"
                    "- Patrimônio cultural e atrações turísticas\n"
                    "- Estrutura administrativa municipal\n"
                    "- Lei Orgânica, bandeira e hino"
                ),
                "example": "Mapa turístico de Arapiraca e pontos de interesse.",
                "exercise": "Descreva a evolução administrativa do município.",
                "references": "Site oficial da Prefeitura; Lei Orgânica."
            }
        ]
    },
    {
        "number": 13,
        "title": "Informática",
        "submodules": [
            {
                "title": "13.1 Conteúdos",
                "content": (
                    "- Conceitos de hardware e software\n"
                    "- Sistemas operacionais: Windows, Linux\n"
                    "- Pacotes Office e Google Workspace\n"
                    "- Segurança da informação e LGPD\n"
                    "- Redes de computadores e protocolos\n"
                    "- Ferramentas de colaboração (Teams, Meet)"
                ),
                "example": "Configuração de rede Wi‑Fi em ambiente municipal.",
                "exercise": "Explique as diferenças entre LAN, WAN e VPN.",
                "references": "Manuais oficiais; Lei 13.709/2018."
            }
        ]
    }
]

def generate_all_module_pdfs(modules):
    """
    Gera um PDF para cada módulo conforme edital.
    """
    styles = getSampleStyleSheet()
    for mod in modules:
        filename = f"Modulo_{mod['number']}_GCM.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        story.append(Paragraph(f"Módulo {mod['number']}: {mod['title']}", styles['Title']))
        story.append(Spacer(1, 12))
        for sub in mod['submodules']:
            story.append(Paragraph(sub['title'], styles['Heading2']))
            story.append(Spacer(1, 6))
            story.append(Paragraph(sub['content'], styles['BodyText']))
            story.append(Spacer(1, 6))
            story.append(Paragraph("Exemplo Prático:", styles['Heading3']))
            story.append(Paragraph(sub['example'], styles['BodyText']))
            story.append(Spacer(1, 6))
            story.append(Paragraph("Exercício:", styles['Heading3']))
            story.append(Paragraph(sub['exercise'], styles['BodyText']))
            story.append(Spacer(1, 6))
            story.append(Paragraph("Referências Bibliográficas:", styles['Heading3']))
            story.append(Paragraph(sub['references'], styles['BodyText']))
            story.append(Spacer(1, 12))
        doc.build(story)
        print(f"Gerado: {filename}")

if __name__ == "__main__":
    generate_all_module_pdfs(modules)



