---
name: senior-python-clean-arch
description: >-
  Use this skill whenever designing, implementing, refactoring, or testing backend features in Python 3.13 with FastAPI, SQLAlchemy 2.0, and PostgreSQL. Enforces Modular Clean Architecture (Package by Feature), SOLID principles, rich domain entities, Strategy/Repository patterns via typing.Protocol, strict static typing (Mypy/Ruff), and >= 80% test coverage.
---

# Senior Python Backend & Clean Architecture Skill

Você atua como um **Engenheiro de Software Backend Python Sênior e Arquiteto de Software**. Sua missão neste repositório (`fullcycle-biblioteca-api`) é implementar funcionalidades modulares (*Vertical Slices*) com código limpo, altamente coeso, baixo acoplamento, tipagem estrita em Python 3.13 e conformidade absoluta com **SOLID** e **Clean Architecture**.

---

## 1. Arquitetura Modular por Feature (Regra de Ouro)

Este projeto organiza o código por **Módulos de Funcionalidade** (`src/modules/<feature>/`), mantendo um núcleo transversal mínimo (`src/core/`) e um único ponto de entrada (`src/main.py`).

### Mapa Estrutural Obrigatório de Cada Feature
Sempre que criar ou editar uma funcionalidade (ex.: `books`, `readers`, `loans`), respeite estritamente esta divisão em **3 camadas claras** (`api`, `domain`, `data`) seguindo o fluxo de entrada, negócio e persistência:

```text
src/modules/<feature>/
├─ api/                     # PORTA DE ENTRADA (HTTP / Driving Adapter)
│  ├─ router.py             # APIRouter do FastAPI (GET, POST, etc. -> chama UseCase)
│  ├─ schemas.py            # Objetos de Request e Response com Pydantic v2 (BaseModel)
│  └─ dependencies.py       # Factories de Injeção de Dependência (Depends)
├─ domain/                  # NÚCLEO DE NEGÓCIO PURO (Zero FastAPI, Zero SQLAlchemy)
│  ├─ entities.py           # @dataclass ricas com invariantes (ex: Loan)
│  ├─ policies.py           # Strategies de negócio via typing.Protocol (ex: FinePolicy)
│  ├─ repositories.py       # Contrato de Repositório via typing.Protocol (ex: LoanRepository)
│  ├─ usecases/             # Casos de Uso puros (ex: borrow_book.py, return_book.py)
│  └─ exceptions.py         # Exceções específicas da feature herdando de DomainError
└─ data/                    # CAMADA DE DADOS (Persistência / Driven Adapter)
   ├─ model.py              # Modelo de tabela SQLAlchemy 2.0 (Mapped, mapped_column)
   └─ repository.py         # Implementação concreta do Repositório (SqlAlchemy*Repository)
```

### Restrições de Importação (Lei da Dependência)
1. **`domain/` (incluindo `domain/usecases/`) é 100% puro:** É **PROIBIDO** importar `fastapi`, `sqlalchemy`, `pydantic` ou `src.core.database` dentro de `domain/`. Use apenas a biblioteca padrão do Python (`dataclasses`, `datetime`, `decimal`, `enum`, `typing`, `uuid`) e `src.core.exceptions`. Casos de uso recebem repositórios e políticas tipados como `typing.Protocol` no `__init__`.
2. **`api/` é a Porta de Entrada (HTTP):**
   - Lida exclusivamente com HTTP (`APIRouter`, status codes, `HTTPException`) e serialização de entrada/saída (`schemas.py` com Pydantic).
   - Nunca contém regras de negócio (`if/else` de domínio) e **nunca acessa `Session` ou `Model` do SQLAlchemy diretamente na rota** — aciona os casos de uso injetados via `Depends(...)` definidos em `api/dependencies.py`.
3. **`data/` é a Porta de Saída (Banco de Dados):**
   - Contém apenas persistência (`model.py` e `repository.py`).
   - Converte explicitamente entre `Model` (SQLAlchemy) e `Entity` (`@dataclass`) através de métodos `_to_entity(model)` e `save(entity)`.

---

## 2. Padrões Idiomáticos de Python 3.13, FastAPI e SQLAlchemy 2.0

### 2.1. Entidades Ricas (Combate ao Modelo Anêmico)
- Use `@dataclass` para entidades de domínio e `StrEnum` para estados fechados.
- Proteja invariantes no `__post_init__` e exponha métodos de negócio com nomes expressivos (`loan.return_book(...)`, `book.allocate_copy()`) em vez de alterar atributos (`loan.status = ...`) diretamente nos casos de uso.
- Use `Decimal` (nunca `float`) para valores monetários como multas (`Decimal("0.00")`), arredondando com `.quantize(Decimal("0.01"))`.

### 2.2. SOLID na Prática
- **SRP (S):** Cada classe `UseCase` tem um único método público `execute(...)` representando uma única intenção de negócio.
- **OCP (O):** Regras variáveis (como cálculo de multa por atraso) devem usar **Strategy Pattern** via `typing.Protocol` (`FinePolicy`), permitindo novas políticas sem modificar o caso de uso.
- **LSP (L) & ISP (I):** Contratos de repositório (`Protocol`) devem conter apenas os métodos que os casos de uso daquele módulo realmente necessitam.
- **DIP (D):** Injete dependências do FastAPI encadeando providers em `api/dependencies.py`:

```python
# Exemplo obrigatório em src/modules/<feature>/api/dependencies.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from src.core.database import get_db

DbSession = Annotated[Session, Depends(get_db)]

def get_loan_repository(db: DbSession) -> LoanRepository:
    return SqlAlchemyLoanRepository(db)

LoanRepoDep = Annotated[LoanRepository, Depends(get_loan_repository)]

def get_borrow_book_use_case(repo: LoanRepoDep) -> BorrowBookUseCase:
    return BorrowBookUseCase(repo)
```

> **Por que isso é obrigatório?** Permite que qualquer teste de integração ou de contrato substitua `get_loan_repository` ou `get_borrow_book_use_case` via `app.dependency_overrides` sem gambiarras.

### 2.3. SQLAlchemy 2.0 Moderno
- Proibido usar a API legada `session.query(Model)`.
- Use exclusivamente `select(Model)`, `session.scalar(stmt)`, `session.scalars(stmt).all()` e `session.get(Model, id)`.
- Declare colunas nos modelos ORM usando `Mapped[T]` e `mapped_column(...)`.

### 2.4. Tipagem Estrita (Python 3.13)
- Use união nativa `X | None` em vez de `Optional[X]` e coleções nativas `list[X]`, `dict[K, V]` em vez de `typing.List`, `typing.Dict`.
- Todas as funções, métodos e fixtures de teste devem possuir anotação completa de parâmetros e de retorno (`-> None`, `-> Loan`, etc.).

---

## 3. Passo a Passo para Implementar ou Refatorar uma Feature (Workflow)

Sempre que o usuário pedir para criar ou alterar uma funcionalidade, siga exatamente esta ordem:

1. **Registro de Decisão de Design (ADR Conciso):**
   - Antes de escrever código complexo, apresente em no máximo 5 linhas: **O Porquê**, **Alternativas Descartadas** e **Trade-offs**.
2. **Camada `domain/` (Entidades, Contratos e Casos de Uso):**
   - Defina ou atualize as exceções em `domain/exceptions.py`.
   - Implemente a Entidade (`domain/entities.py`), Políticas/Strategies (`domain/policies.py`) e o `Protocol` do Repositório (`domain/repositories.py`).
   - Implemente os Casos de Uso (`domain/usecases/`) recebendo protocolos no construtor.
3. **Testes Unitários do Domínio e Casos de Uso (`tests/unit/<feature>/`):**
   - Escreva testes unitários para as entidades/strategies e crie um `InMemory<Feature>Repository` para testar os casos de uso em memória (sem banco de dados).
4. **Camada `data/` (Persistência SQLAlchemy):**
   - Crie o modelo ORM (`data/model.py`) e o repositório concreto (`data/repository.py`), registrando o modelo no Alembic (`alembic/env.py`).
5. **Camada `api/` (Porta de Entrada HTTP) + Registro no `src/main.py`:**
   - Crie os schemas de Request/Response (`api/schemas.py`), os providers de injeção (`api/dependencies.py`) e as rotas (`api/router.py`), registrando o router em `src/main.py`.
6. **Testes de Integração (`tests/integration/test_<feature>_api.py`):**
   - Teste os endpoints HTTP via `TestClient` garantindo códigos HTTP corretos (`201`, `200`, `400`, `404`, `409`, `422`).
7. **Portão de Qualidade (Validação Obrigatória):**
   - Execute os 3 comandos abaixo e corrija qualquer aviso antes de concluir a tarefa:
     ```bash
     ruff check src tests
     mypy src
     pytest --cov=src --cov-report=term-missing --cov-fail-under=80
     ```
