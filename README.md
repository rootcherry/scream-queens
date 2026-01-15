# Scream Queens — Módulo Horrorverse

Scream Queens é um módulo do projeto Horrorverse, focado na coleta,
processamento e análise de dados sobre atrizes do cinema de terror.

O projeto separa claramente o pipeline de dados (Python) da análise
e aplicação de lógica (JavaScript).

---

## Objetivo

- coletar dados reais de filmografias
- normalizar e validar essas informações
- gerar um arquivo JSON processado
- aplicar filtros e rankings usando estruturas de dados

---

## Arquitetura do Projeto

Fluxo de dados:

Web / APIs
→ Python (scraping e processamento)
→ JSON processado (contrato de dados)
→ JavaScript (filtros e rankings)

---

## Pipeline de Dados (Python)

Responsável por:

- scraping de filmografias
- enriquecimento de dados via OMDb API
- filtragem inicial
- normalização
- validação dos dados

Arquivo final gerado:

data/processed/processed_scream_queens_clean.json

---

## Análise e Rankings (JavaScript / DSA)

Responsável por:

- carregar o JSON processado
- indexar dados utilizando Map
- aplicar filtros
- gerar rankings ordenados

---

## Estrutura do Projeto

scream-queens/
├── data/
│ ├── raw/
│ └── processed/
├── src/
├── scripts/
│ └── py/
├── dsa/
│ ├── utils/
│ ├── filters/
│ ├── rankings/
│ └── runRanking.js
└── README.md

yaml
Copy code

---

## Como Executar

### Pipeline Python

source .venv/bin/activate
python src/omdb_ok.py

shell
Copy code

### Executar rankings

node dsa/runRanking.js filmCount desc 10
node dsa/runRanking.js careerSpan desc 10
node dsa/runRanking.js boxOffice desc 10

yaml
Copy code

---

## Rankings Disponíveis

- filmCount — quantidade de filmes
- careerSpan — intervalo da carreira
- boxOffice — métricas de bilheteria
- survival — sobrevivência dos personagens

---

## Observações

- O dataset inicial é pequeno de propósito
- O foco é arquitetura e fluxo de dados
- Expansões e refinamentos serão feitos posteriormente

---

## Sobre o Horrorverse

Horrorverse é um projeto em evolução voltado para análise de dados
e sistemas relacionados ao cinema de terror.

O módulo Scream Queens representa a primeira entrega completa.
