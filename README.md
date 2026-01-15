# Scream Queens — Módulo Horrorverse

Scream Queens é um módulo do projeto Horrorverse, focado na coleta, processamento e análise de dados sobre atrizes do cinema de terror.

O projeto separa claramente o pipeline de dados (Python) da análise e aplicação de lógica (JavaScript), seguindo uma abordagem simples e organizada.

---

## Objetivo

* Coletar dados reais de filmografias
* Normalizar e validar essas informações
* Gerar um arquivo JSON processado
* Aplicar filtros e rankings utilizando estruturas de dados

O foco do projeto é arquitetura, clareza e evolução incremental.

---

## Arquitetura do Projeto

Fluxo de dados:

Web / APIs → Python (scraping e processamento) → JSON processado → JavaScript (filtros e rankings)

O JSON processado funciona como um contrato de dados entre o Python e o JavaScript.

---

## Pipeline de Dados (Python)

Responsável por:

* Scraping de filmografias
* Enriquecimento via OMDb API
* Filtragem inicial
* Normalização de campos
* Validação da estrutura final

Arquivo final gerado:

`data/processed/processed_scream_queens_clean.json`

Esse arquivo não contém lógica de análise, apenas dados organizados.

---

## Análise e Rankings (JavaScript / DSA)

Responsável por:

* Carregar o JSON processado
* Indexar dados utilizando Map
* Aplicar filtros puros
* Gerar rankings ordenados

Não há scraping ou chamadas externas nessa etapa.

---

## Estrutura do Projeto

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

## Como Executar

### Pipeline Python

Ative o ambiente virtual e execute o pipeline:

```
source .venv/bin/activate
python src/omdb_ok.py
```

O JSON final será salvo em `data/processed`.

### Executar Rankings (Node.js)

Os rankings podem ser executados via terminal:

```
node dsa/runRanking.js filmCount desc 10
node dsa/runRanking.js careerSpan desc 10
node dsa/runRanking.js boxOffice desc 10
```

Formato geral:

```
node dsa/runRanking.js <ranking> <asc|desc> <limit>
```

---

## Rankings Disponíveis

* filmCount — quantidade de filmes
* careerSpan — intervalo da carreira
* boxOffice — métricas de bilheteria
* survival — sobrevivência dos personagens

---

## Observações

* O dataset inicial é pequeno de propósito
* O foco é validar arquitetura e fluxo
* Expansões e refinamentos serão feitos posteriormente
* O projeto foi desenvolvido com commits pequenos e incrementais

---

## Sobre o Horrorverse

Horrorverse é um projeto em evolução voltado para análise de dados e sistemas relacionados ao cinema de terror.

O módulo Scream Queens representa a primeira entrega completa desse universo.
