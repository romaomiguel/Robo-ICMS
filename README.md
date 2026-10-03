# Robô de ICMS — Apuração a partir de XMLs de NF-e

Aplicação web que recebe os **XMLs de NF-e** de entrada de um cliente, extrai os dados de cada item e entrega uma **planilha Excel de apuração de ICMS** com as colunas e as fórmulas prontas (ICMS-ST, MVA, benefício de redução de base, DIFAL, Convênio 52/91 e Portaria 195, entre outras), a partir de uma planilha-modelo.

> Versão pública de um projeto real de uso interno. A planilha-modelo (`src/planilha_mae/teste.xlsx`) mantém a estrutura e as fórmulas, mas com identificação fictícia.

## O problema

A apuração mensal do ICMS de entradas exige abrir dezenas ou centenas de notas, copiar item por item (NCM, CEST, CFOP, CST, valores de frete, seguro, IPI...) e aplicar as regras de cada operação. É um trabalho repetitivo e propenso a erro. O robô faz a extração e a organização, e a planilha-modelo faz o cálculo.

## Como funciona

1. O usuário envia vários `.xml` (até 50 MB no total) pela interface web.
2. O `NFEProcessor` percorre cada item (`det`) e extrai as tags relevantes, aplicando formatações: NCM com pontos, valores com 2 casas, origem e CST normalizados.
3. Os itens são gravados na aba de entrada da planilha-modelo, que já contém as demais abas de cálculo (`LerXml`, `Relatorio`, `Portaria 195`, `Convenio 52-91`, `BIT`...).
4. O sistema extrai o **CNPJ** e a **competência** do primeiro XML para nomear o arquivo de saída.
5. O Excel é devolvido para download.
6. Cada processamento é registrado em um **histórico** (IP de origem, quantidade de notas, data), sem derrubar o fluxo caso o banco esteja indisponível.

## Stack

Python 3.11 · Flask · openpyxl · `xml.dom.minidom` · PostgreSQL (`psycopg2`, histórico) · Gunicorn · Docker · Kubernetes

## Como rodar

```bash
pip install -r requirements.txt
export SECRET_KEY="troque-esta-chave"
python src/main.py        # http://localhost:5000   (no Docker/Gunicorn a porta é 3939)
```

Com Docker:

```bash
docker compose up --build
```

O histórico usa PostgreSQL (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`); crie a tabela com [`sql/historico_processamento.sql`](sql/historico_processamento.sql). Sem banco disponível, o processamento continua funcionando e apenas avisa no log.

## Rotas

| Rota | Função |
|---|---|
| `POST /api/nfe/upload` | Recebe os XMLs e devolve a planilha `.xlsx` |
| `GET /` | Interface web |

## Estrutura

```
src/
  main.py             app Flask (ProxyFix, CORS, estáticos)
  nfe_processor.py    leitura dos XMLs e preenchimento da planilha-modelo
  db.py               histórico de processamentos
  routes/nfe.py       endpoint de upload
  planilha_mae/       planilha-modelo com as fórmulas
  static/             interface web
sql/                  DDL do histórico
```

## Deploy

Imagem Docker (Gunicorn, porta 3939) publicada pelo workflow em `.github/workflows/build-push.yml` e atualizada no `k8s-manifests` (Argo CD). Ajuste `seu-usuario` para a sua conta.
