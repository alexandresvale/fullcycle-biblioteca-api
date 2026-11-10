> **Nível escolhido:** Projeto B — Simples (API de Domínio Único: Biblioteca — Acervo e Empréstimos)

# FullCycle 4.0 — API de Biblioteca (Projeto B)

API RESTful para gestão de **Acervo, Leitores, Empréstimos e Devoluções** construída com **Python 3.13, FastAPI, PostgreSQL 16 e Clean Architecture**.

## Como subir com 1 comando (Docker Compose)

```bash
docker compose up --build -d
```

- **Healthcheck:** `http://localhost:8000/health`
- **Documentação Interativa (Swagger UI):** `http://localhost:8000/docs`

## Como rodar os testes e linters (Qualidade & Cobertura >= 80%)

```bash
# Testes automatizados + Cobertura de código
docker compose exec api pytest

# Linter (Ruff) e Verificação de Tipos (Mypy)
docker compose exec api ruff check src tests
docker compose exec api mypy src
```
