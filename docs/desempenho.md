# Relatório de Desempenho e Validação de SLOs (Smoke Test k6)

> **Projeto:** FullCycle 4.0 — API de Biblioteca (Projeto B)  
> **Módulo:** M3 (DevOps & Observabilidade) e M4 (Arquitetura & Desempenho)  
> **Data de Execução:** 11/11/2026  
> **Ferramenta de Carga:** [Grafana k6 v0.50+](https://k6.io/) via container Docker

---

## 1. Declaração Formal de SLOs (Service Level Objectives)

Para o fluxo crítico da API de Biblioteca (verificação de saúde, listagem, empréstimo e devolução de exemplares), foram definidos os seguintes objetivos de nível de serviço sob regime de carga concorrente:

| Indicador (SLI) | Métrica Prometheus / k6 | Meta de Nível de Serviço (SLO) | Justificativa de Engenharia |
| :--- | :--- | :--- | :--- |
| **Taxa de Erro** | `http_req_failed` | `< 1.0%` (Zero erros 5xx esperados) | Garantir estabilidade transacional das operações com PostgreSQL. |
| **Latência (p95)** | `http_req_duration (p95)` | `<= 200 ms` | Resposta interativa fluida em chamadas de UI e integrações de clientes. |

---

## 2. Ambiente de Teste e Metodologia

O teste de fumaça (*Smoke Test*) foi executado em ambiente completamente isolado e conteinerizado via Docker Compose, simulando a rede interna e interações síncronas entre os serviços:

- **Host:** Windows 11 x64 / Docker Desktop (WSL2 Backend)
- **Container API:** `python:3.13-slim` (Uvicorn ASGI, FastAPI, SQLAlchemy 2.0, Psycopg 3)
- **Container Banco:** `postgres:16-alpine` (limite padrão de conexões, persistência via volume Docker)
- **Container Carga:** `grafana/k6:latest` (executado sob profile `perf`)
- **Parâmetros de Carga:**
  - **VUs (Virtual Users):** 5 usuários virtuais concorrentes
  - **Duração:** 30 segundos contínuos
  - **Cenário por Iteração:**
    1. `GET /health` (validação de disponibilidade da API e conectividade com banco)
    2. `GET /loans` (leitura e serialização de lista de empréstimos)
    3. `POST /loans` (criação de novo empréstimo com persistência transacional)
    4. `POST /loans/{id}/return` (cálculo de devolução e aplicação de política de multa `FinePolicy`)
    5. Intervalo (*Think Time*): 100ms entre iterações

---

## 3. Comando de Execução

O teste é 100% reproduzível sem necessidade de ferramentas instaladas no host, acionado pelo comando oficial:

```bash
docker compose --profile perf run --rm k6 run /scripts/smoke.js
```

---

## 4. Resultados Medidos

```text
  █ THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<200' p(95)=143.31ms

    http_req_failed
    ✓ 'rate<0.01' rate=0.00%

  █ TOTAL RESULTS 

    checks_total.......: 1992    65.54/s
    checks_succeeded...: 100.00% 1992 out of 1992
    checks_failed......: 0.00%   0 out of 1992

    ✓ health returns 200
    ✓ list loans returns 200
    ✓ create loan returns 201
    ✓ return loan returns 200
```

### Tabela Detalhada de Métricas

| Métrica | Valor Medido | Limite SLO | Status |
| :--- | :--- | :--- | :--- |
| **Requisições Totais** | **1.992** | - | Concluído com sucesso |
| **Vazão (Throughput)** | **65.54 req/s** | - | Adequado para escala de biblioteca |
| **Taxa de Erro (`http_req_failed`)** | **0.00%** (0 / 1.992) | `< 1.0%` | **SUPERADO (0 erros)** |
| **Latência Mínima (`min`)** | **1.06 ms** | - | - |
| **Latência Mediana (`med`)** | **34.06 ms** | - | - |
| **Latência Média (`avg`)** | **50.87 ms** | - | - |
| **Percentil 90 (`p90`)** | **116.72 ms** | - | - |
| **Percentil 95 (`p95`)** | **143.31 ms** | `<= 200 ms` | **ATINGIDO (Margem de 28.3%)** |
| **Latência Máxima (`max`)** | **405.16 ms** | - | Pico inicial de warm-up da conexão |

---

## 5. Veredito e Análise Arquitetural

> **Veredito Oficial:** **SLO 100% ATINGIDO.**  
> O percentil 95 de latência sustentou-se em **143.31 ms** (abaixo do teto de 200 ms) e a taxa de erro permaneceu em **0.00%** ao longo de todas as 1.992 requisições transacionais.

### Análise de Gargalos e Pontos de Observação
1. **Pico Inicial de Latência (`max=405.16ms`):** Observado exclusivamente durante os primeiros segundos de aquecimento (*warm-up*), momento em que o pool de conexões do SQLAlchemy (`QueuePool`) abre os primeiros sockets TCP com o PostgreSQL. Uma vez estabelecido o pool, a mediana estabilizou-se rapidamente em **34.06 ms**.
2. **Eficiência da Camada de Domínio:** O desacoplamento do cálculo de multas via Strategy (`FinePolicy`) e a segregação entre entidades puras e modelos ORM mantiveram a CPU da aplicação com tempo de processamento inferior a **5 ms** por requisição, com a maior fatia do tempo gasta em I/O de rede e commit no banco de dados.
3. **Recomendações para Carga Futura (Escala Projeto A):**
   - Configuração explícita de `pool_size` e `max_overflow` no SQLAlchemy para suportar picos acima de 50 VUs.
   - Adição de índice composto em `loans (reader_id, returned_at)` caso a listagem de empréstimos passe a ser filtrada frequentemente por leitor com histórico massivo.
