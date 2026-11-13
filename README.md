> **Nível escolhido:** Projeto B — Simples (API de Domínio Único: Biblioteca — Acervo e Empréstimos)

# FullCycle 4.0 — API de Biblioteca (Projeto B)

API RESTful para gestão de **Acervo, Leitores, Empréstimos e Devoluções** construída com **Python 3.13, FastAPI, PostgreSQL 16 e Clean Architecture Modular (Package by Feature)**.

---

## 🚀 Como subir com 1 comando (Docker Compose)

O ambiente é 100% conteinerizado e provisiona o banco de dados PostgreSQL e a aplicação sem necessidade de configurações manuais:

```bash
docker compose up --build -d
```

### Endpoints Principais
- **Healthcheck:** [http://localhost:8000/health](http://localhost:8000/health)
- **Documentação Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Métricas Prometheus:** [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## 🎯 Objetivo de Nível de Serviço (SLO)

A API possui compromissos mensuráveis de estabilidade e latência sob regime de concorrência:

| Indicador (SLI) | Meta de Nível de Serviço (SLO) | Resultado Medido (k6 Smoke Test) | Status |
| :--- | :--- | :--- | :--- |
| **Taxa de Erro** | `< 1.0%` (Erros 5xx) | **0.00%** (0 erros em 1.992 requisições) | ✅ **Atingido** |
| **Latência (p95)** | `<= 200 ms` | **143.31 ms** | ✅ **Atingido** |

---

## ⚡ Como rodar o Teste de Carga / Smoke Test (k6)

O teste de desempenho é executado através de um contêiner descartável do k6 integrado ao Docker Compose:

```bash
docker compose --profile perf run --rm k6 run /scripts/smoke.js
```

Para detalhes completos dos percentis (`p50`, `p90`, `p95`, `p99`) e análise de vazão, consulte [docs/desempenho.md](docs/desempenho.md).

---

## 🧪 Como rodar os testes e linters (Qualidade & Cobertura >= 80%)

```bash
# Testes automatizados com relatório de cobertura (mínimo 80% exigido)
docker compose exec api pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Linter e formatação (Ruff)
docker compose exec api ruff check src tests

# Checagem estática de tipos (Mypy)
docker compose exec api mypy src
```

---

## 📚 Documentação do Projeto

- [docs/adr/0001-strategy-multa-e-arquitetura.md](docs/adr/0001-strategy-multa-e-arquitetura.md): Registro de Decisão Arquitetural (MADR) sobre Clean Architecture, Repository Pattern e Strategy Pattern (`FinePolicy`).
- [docs/openapi.yaml](docs/openapi.yaml): Contrato OpenAPI 3.1 validado automaticamente via Spectral CLI.
- [docs/desempenho.md](docs/desempenho.md): Relatório do smoke test com k6, métricas de latência e validação dos SLOs.
- [docs/requisitos-sistema.md](docs/requisitos-sistema.md): Especificação de requisitos, modelo de domínio e tabelas do sistema.
- [docs/ia.md](docs/ia.md): Registro de co-design e prompts utilizados com a IA.
- [CONTRIBUTORS.md](CONTRIBUTORS.md): Matriz de responsabilidade e divisão vertical de módulos da equipe.
