# 👑 Scream Queens — Horrorverse Module 🧛‍♀️

**Scream Queens** é um módulo do projeto **Horrorverse**, focado em coletar,
processar e analisar dados sobre atrizes icônicas do cinema de terror.

O projeto separa claramente:
- Python → coleta e processamento de dados
- JavaScript → análise, filtros e rankings

---

## 🎯 Objetivo

Construir um fluxo completo para:

- coletar dados reais de filmes
- organizar e normalizar essas informações
- gerar um arquivo JSON confiável
- aplicar filtros e rankings de forma simples

O foco é **clareza e organização**, não volume de dados.

---

## 🧠 Visão Geral da Arquitetura

Fluxo do projeto:

Web / APIs
↓
Python (scraping e processamento)
↓
JSON processado (contrato de dados)
↓
JavaScript (DSA, filtros e rankings)

---

## 1️⃣ Pipeline de Dados (Python)

Responsável por:

- scraping de filmografias
- enriquecimento via OMDb API
- filtragem inicial
- normalização
- validação dos dados

Arquivo final gerado:

data/processed/processed_scream_queens_clean.json

---

## 2️⃣ Análise e Rankings (JavaScript / DSA)

Responsável por:

- carregar o JSON processado
- indexar dados com Map
- aplicar filtros
- gerar rankings ordenados

---

## 📂 Estrutura do Projeto

```
scream-queens/
├── data/
│   ├── raw/
│   └── processed/
├── src/
├── scripts/
│   └── py/
├── dsa/
│   ├── utils/
│   ├── filters/
│   ├── rankings/
│   └── runRanking.js
└── README.md
```

---

## ▶️ Como Executar

### 1️⃣ Pipeline Python

```
source .venv/bin/activate
python src/omdb_ok.py
```

### 2️⃣ Executar Rankings (Node.js)

```
node dsa/runRanking.js filmCount desc 10
node dsa/runRanking.js careerSpan desc 10
node dsa/runRanking.js boxOffice desc 10
```

---

## 🏆 Rankings Disponíveis

- filmCount — quantidade de filmes
- careerSpan — intervalo da carreira
- boxOffice — métricas de bilheteria
- survival — sobrevivência dos personagens

---

## 📌 Observações

- Dataset inicial é pequeno de propósito
- Foco em arquitetura e fluxo
- Expansão virá depois

---

## 🚀 Próximos Passos

- expandir dataset
- refinar critérios
- criar API
- criar interface visual

---

## 📚 Sobre o Horrorverse

**Horrorverse** é um projeto em evolução para análise de dados
relacionados ao cinema de terror.

O módulo **Scream Queens** é a primeira entrega completa.
