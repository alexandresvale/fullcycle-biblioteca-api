# Registro de Uso de Inteligência Artificial (Pair Programming & Co-Design)

> **Projeto:** FullCycle 4.0 — API de Biblioteca (Projeto B)  
> **Papel da IA:** Assistente Sênior de Arquitetura e Engenharia de Software (Antigravity)  
> **Metodologia:** Engenharia de Prompt Estruturada, Revisão Crítica de Código e Decisões de Design (ADR)

---

## 1. Visão Geral da Colaboração

O desenvolvimento deste projeto utilizou Inteligência Artificial não como um simples gerador de código, mas como um **parceiro sênior de pair programming**, com rigor conceitual focado em **Clean Architecture, Princípios SOLID, Tipagem Estrita (Python 3.13) e Testabilidade**.

Todas as sugestões geradas pela IA foram submetidas ao crivo técnico da dupla e passaram por portões de qualidade automatizados (`ruff`, `mypy`, `pytest` com cobertura `>= 80%` e execução de testes em containers reais).

---

## 2. Prompts Estruturados e Interações Chave

### 2.1. Arquitetura Modular (Package by Feature) e Isolamento de Domínio
- **Contexto:** Necessidade de estruturar a API para desenvolvimento paralelo entre os dois membros da equipe sem conflitos de merge e respeitando o isolamento do domínio.
- **Prompt Utilizado:**
  > *"Como Engenheiro de Software Sênior, proponha a estrutura de pastas seguindo Clean Architecture modular (Package by Feature) para a API de Biblioteca em Python 3.13. Separe estritamente em api/ (HTTP e schemas), domain/ (entidades puras, usecases e protocolos) e data/ (SQLAlchemy models e repositórios concretos), mantendo src/core/ para infraestrutura compartilhada."*
- **Decisão Técnica Tomada:**
  - Adoção de `src/modules/<feature>/{api,domain,data}`.
  - O domínio (`domain/`) não possui nenhuma importação de frameworks externos (`fastapi`, `sqlalchemy`, `pydantic`), garantindo pureza de regras de negócio e testes unitários instantâneos.

### 2.2. Modelagem de Domínio e Strategy Pattern (`FinePolicy`)
- **Contexto:** Modelagem do cálculo de multa para devoluções em atraso, variando conforme a categoria do leitor (Padrão vs. Acadêmico).
- **Prompt Utilizado:**
  > *"Modele a entidade Loan e o cálculo de multa aplicando o Strategy Pattern e OCP (Open-Closed Principle). Use typing.Protocol para definir a interface FinePolicy e implemente as estratégias StandardFinePolicy (R$ 2,00/dia) e AcademicFinePolicy (R$ 1,00/dia). Forneça testes unitários exaustivos cobrindo devolução no prazo e em atraso."*
- **Decisão Técnica Tomada:**
  - Emprego do `Strategy Pattern` via `typing.Protocol`, eliminando blocos condicionais (`if/elif`) e permitindo a extensão para novas políticas de multa sem alterar a entidade `Loan` ou os casos de uso.

### 2.3. Observabilidade e Prevenção de Explosão de Cardinalidade no Prometheus
- **Contexto:** Instrumentação de métricas HTTP com `prometheus-client` e logs estruturados via `structlog`.
- **Prompt Utilizado:**
  > *"Desenvolva o middleware de observabilidade para FastAPI que injete X-Request-ID, registre logs estruturados em JSON via structlog e contabilize latência e total de requisições no Prometheus. Como evitar a explosão de cardinalidade nas métricas para rotas com parâmetros de caminho (ex: /loans/{loan_id})?"*
- **Decisão Técnica Tomada:**
  - Extração do path do template resolvido pelo Starlette (`request.scope.get("route").path`) em vez da URL bruta com UUID, prevenindo a proliferação descontrolada de séries temporais no Prometheus.
  - Supressão de logs `INFO` ruidosos para o endpoint de healthcheck (`/health`), mantendo os contadores Prometheus fidedignos.

### 2.4. Planejamento de Carga e Automação de Smoke Test com k6
- **Contexto:** Validação de SLOs em regime de concorrência local via Docker Compose.
- **Prompt Utilizado:**
  > *"Escreva um script de smoke test k6 (smoke.js) com thresholds para SLO: taxa de falha < 1% e p95 <= 200ms. O script deve simular o ciclo de vida completo: healthcheck, listagem de empréstimos, criação de empréstimo e devolução com cálculo de multa sob 5 VUs por 30s."*
- **Decisão Técnica Tomada:**
  - Encapsulamento da execução do k6 em profile Docker (`docker compose --profile perf`), tornando a validação de performance reproduzível em qualquer ambiente de desenvolvimento ou avaliação.

---

## 3. Diretrizes de Qualidade Aplicadas (Clean Code & SOLID)

A IA foi instruída por meio de *custom skills* e regras de contexto a seguir diretrizes inegociáveis:
1. **Tipagem Estrita:** Uso de recursos modernos do Python 3.13 (`X | None` em vez de `Optional[X]`, type hints em todas as assinaturas).
2. **Imutabilidade e Encapsulamento:** Entidades de domínio ricas, protegendo invariantes de negócio através de métodos de negócio claros (`return_book()`, `calculate_fine()`).
3. **Ausência de Gambiarras:** Tratamento de avisos de linters e analisadores estáticos (`ruff`, `mypy`) como erros bloqueantes de compilação.
4. **Registro de Decisão Arquitetural (ADR):** Toda refatoração relevante incluiu justificativa do porquê, alternativas descartadas e trade-offs avaliados.
