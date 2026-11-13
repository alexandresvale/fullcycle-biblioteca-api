# ADR-0001: Clean Architecture Modular, Repository Pattern e Strategy Pattern para Cálculo de Multas

- **Status:** Aceita
- **Data:** 2026-11-13
- **Autores:** Alexandre Vale (@alexandresvale), Ricardo Vale (@ricardosvale)
- **Projeto:** FullCycle 4.0 — API de Biblioteca (Projeto B)

---

## Contexto e Declaração do Problema

O sistema **FullCycle Biblioteca API** gerencia o ciclo de vida completo de uma biblioteca: cadastro e disponibilidade de acervo (`/books`), cadastro e elegibilidade de leitores (`/readers`), além de empréstimos e devoluções com cálculo de multa por atraso (`/loans`).

Durante o desenho arquitetural do Projeto B, emergiram quatro requisitos críticos que precisavam ser conciliados desde o início:

1. **Evolução das regras de multa sem regressão:** A biblioteca possui perfis distintos de leitores (atualmente `STANDARD` e `ACADEMIC`, com previsão de novas categorias no futuro), cada um com regras próprias de carência e tarifa diária.
2. **Isolamento de domínio e testabilidade determinística:** O projeto exige cobertura mínima automatizada de `>= 80%`, tipagem estrita com `mypy` e `ruff`, além de testes unitários rápidos que validem invariantes de negócio sem depender de banco de dados ou servidor HTTP.
3. **Desenvolvimento paralelo em dupla:** Dois desenvolvedores precisavam implementar fatias verticais independentes (`books`/`readers` e `loans`/observabilidade) simultaneamente sem gerar conflitos constantes de merge ou acoplamento prematuro entre tabelas.
4. **Baixo overhead em produção:** A API possui metas formais de SLO (`taxa de erro < 1%` e `p95 <= 200ms`), exigindo camada de domínio enxuta e transparente em tempo de execução.

Diante disso, precisávamos decidir: **como estruturar os módulos da API, o acesso a dados e as políticas variáveis de cálculo de multa em Python 3.13 com FastAPI e SQLAlchemy 2.0?**

---

## Fatores de Decisão

- **Conformidade com SOLID (SRP, OCP, DIP):** Regras de negócio isoladas de frameworks e abertas para extensão sem modificação de fluxos estáveis.
- **Testabilidade em memória (sem I/O):** Capacidade de testar casos de uso e políticas de multa em milissegundos usando repositórios fake (`InMemory*Repository`).
- **Independência de ORM e framework Web:** Entidades de domínio puras (`@dataclass`), protegendo invariantes independentemente do SQLAlchemy 2.0 ou FastAPI.
- **Produtividade em equipe:** Fronteiras claras por funcionalidade (*Vertical Slices*) para minimizar atrito no Git e facilitar revisão de código.

---

## Decisão Tomada

Adotamos a combinação de três padrões complementares:

### 1. Clean Architecture Modular (*Package by Feature* / *Vertical Slices*)

Cada módulo de negócio em `src/modules/<feature>/` (`books`, `readers`, `loans`) é organizado estritamente em **3 camadas** com direção única de dependência rumo ao núcleo (`domain/`):

- **`api/` (Driving Adapter / Porta de Entrada HTTP):** Contém exclusivamente roteadores FastAPI (`router.py` / `loans_router.py`), schemas de serialização Pydantic v2 (`schemas.py` / `loan_schema.py`) e providers de injeção de dependência (`dependencies.py`). Traduz exceções de domínio em códigos HTTP determinísticos (`400`, `404`, `409`, `422`), sem conter regras de negócio nem acessar `Session` do SQLAlchemy.
- **`domain/` (Núcleo de Negócio Puro):** Composto por entidades ricas em `@dataclass` (`Book`, `Reader`, `Loan`) com proteção de invariantes no construtor/`__post_init__` e métodos de negócio expressivos (`allocate_copy()`, `release_copy()`, `return_book()`), exceções semânticas herdando de `DomainError`, contratos (`typing.Protocol`) e casos de uso de responsabilidade única (`execute(...)`). **É proibido importar `fastapi`, `sqlalchemy` ou `pydantic` em `domain/`.**
- **`data/` (Driven Adapter / Persistência):** Contém os modelos ORM SQLAlchemy 2.0 (`Mapped`, `mapped_column`) e os repositórios concretos (`SqlAlchemyBookRepository`, `SqlAlchemyReaderRepository`, `SqlAlchemyLoanRepository`), realizando a conversão explícita entre modelo ORM e entidade de domínio via `_to_entity(...)`.

### 2. Repository Pattern via `typing.Protocol` (Inversão de Dependência — DIP)

Os casos de uso (`BorrowBookUseCase`, `ReturnBookUseCase`, `RegisterBookUseCase`, `RegisterReaderUseCase`, etc.) dependem exclusivamente de protocolos estruturais (`LoanRepository`, `BookRepository`, `ReaderRepository`) definidos dentro de `domain/`.

- Em **produção e testes de integração**, `api/dependencies.py` injeta as implementações `SqlAlchemy*Repository` conectadas ao PostgreSQL 16.
- Em **testes unitários**, os mesmos casos de uso recebem implementações `InMemory*Repository`, validando regras como unicidade de ISBN, unicidade de e-mail/documento e limite de 3 empréstimos ativos por leitor sem subir banco de dados.

### 3. Strategy Pattern (`FinePolicy`) para Cálculo de Multas (Aberto-Fechado — OCP)

O cálculo de multa por atraso na devolução foi extraído para o contrato estrutural `FinePolicy` em `src/modules/loans/domain/policies/fine_policy.py`:

```python
class FinePolicy(Protocol):
    def calculate_fine(self, days_overdue: int) -> Decimal: ...
```

As estratégias atuais implementam esse contrato de forma independente:

- **`StandardDailyFinePolicy`:** Cobra tarifa fixa de `R$ 2,00` por dia corrido de atraso (`days_overdue * 2.00`), sem dias de carência.
- **`AcademicGraceFinePolicy`:** Concede `2 dias` de carência (`grace_days = 2`); até 2 dias de atraso a multa é `R$ 0,00`, e a partir do 3º dia cobra `R$ 1,50` por dia excedente (`(days_overdue - 2) * 1.50`).

Na camada de entrada, `resolve_fine_policy(policy_type)` seleciona a estratégia adequada e a injeta em `ReturnBookUseCase(repo, policy)`, que por sua vez delega o cálculo para `loan.return_book(returned_at=..., fine_policy=...)`.

---

## Alternativas Descartadas

### Alternativa 1 (Descartada): Arquitetura Active Record / CRUD acoplada ao ORM + `if/elif/else` fixo de multa

Nesta abordagem tradicional, as rotas FastAPI recebem diretamente a `Session` do SQLAlchemy, manipulam os modelos ORM (`BookModel`, `ReaderModel`, `LoanModel`) como objetos *Active Record* e calculam a multa com condicionais fixas dentro da rota ou de um método monolítico:

```python
# Exemplo do anti-padrão descartado:
if payload.policy_type == "STANDARD":
    fine = Decimal("2.00") * overdue_days
elif payload.policy_type == "ACADEMIC":
    fine = Decimal("1.50") * max(0, overdue_days - 2)
```

**Motivos explícitos do descarte:**

1. **Acoplamento rígido ao ORM e ao banco de dados:** Manipular `Session` e modelos SQLAlchemy diretamente nas rotas torna impossível testar regras de negócio em memória pura. Qualquer teste de regra de negócio exigiria PostgreSQL ativo ou mocks frágeis de sessão SQLAlchemy, degradando a velocidade e a confiabilidade da suíte de testes.
2. **Modelo anêmico e dispersão de invariantes:** Atualizar atributos diretamente nos endpoints (`book.available_copies -= 1`, `loan.status = "RETURNED"`) remove o encapsulamento das entidades e espalha validações pela camada HTTP, aumentando o risco de estados inválidos (ex.: devolução dupla, `due_date < borrowed_at`, ou violação do limite de 3 empréstimos simultâneos).
3. **Violação do Princípio Aberto-Fechado (OCP) via `if/elif` fixo:** Concentrar regras tarifárias em condicionais `if/elif/else` obriga a editar e retestar o núcleo de devolução toda vez que uma nova modalidade surgir (ex.: `POSTGRAD`, `ALUMNI`, `PARTNER`, teto máximo de multa ou isenção em feriados), aumentando o risco de regressão em regras já homologadas.

### Alternativa 2 (Descartada): Arquitetura em Microsserviços Distribuídos (`books-service`, `readers-service`, `loans-service`)

Separar os três módulos em processos e bancos independentes foi descartado por adicionar latência de rede entre chamadas síncronas, complexidade de consistência distribuída (Saga/Outbox) e sobrecarga operacional desproporcional ao tamanho do domínio de Biblioteca (Projeto B). O monólito modular já atendeu com folga aos SLOs no smoke test k6 (`p95 = 143.31ms` contra limite de `200ms` e `0.00%` de erros).

---

## Consequências e Trade-offs

### Positivas

- **Testabilidade extrema e feedback rápido:** Casos de uso, entidades e políticas de multa são testados em memória com `InMemory*Repository` em milissegundos, mantendo cobertura global `>= 80%` somada aos testes de integração com PostgreSQL 16 real.
- **Extensibilidade segura (OCP):** Novas políticas de multa podem ser adicionadas criando novas classes que satisfazem `FinePolicy` sem modificar `Loan` ou `ReturnBookUseCase`.
- **Desacoplamento real de infraestrutura (DIP):** A substituição ou atualização do driver/ORM em `data/` não afeta nenhuma regra em `domain/`, e `app.dependency_overrides` funciona de forma nativa nos testes de API.
- **Paralelismo sem conflitos:** A divisão em `src/modules/{books,readers,loans}/` permitiu que a dupla trabalhasse em paralelo com zero conflitos de merge e baixa carga cognitiva.
- **Desempenho preservado:** Conforme registrado em `docs/desempenho.md`, a camada de domínio manteve processamento de CPU abaixo de `5ms` por requisição, contribuindo para `p95 = 143.31ms` e `0%` de erros no k6.

### Negativas (Trade-offs Aceitos)

- **Maior número de arquivos e boilerplate inicial:** Cada módulo exige arquivos separados para entidades, protocolos, casos de uso, modelos ORM, repositórios concretos, schemas e providers de dependência, em comparação com um CRUD direto em um único arquivo.
- **Custo de mapeamento entre camadas:** É necessário manter métodos explícitos de conversão (`_to_entity` / `save`) entre entidades `@dataclass` de `domain/` e modelos ORM de `data/`, exigindo atenção redobrada para manter campos e constraints sincronizados via Alembic.
- **Resolução explícita de dependências na borda:** Como `domain/` não instancia implementações concretas, a camada `api/dependencies.py` concentra a responsabilidade de compor dependências (`Depends`) e resolver a estratégia (`resolve_fine_policy`) a partir da entrada HTTP.
