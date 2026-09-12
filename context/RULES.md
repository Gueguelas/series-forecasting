# RULES — Regras do projeto

Regras para integrantes humanos e agentes de IA.

---

## 1. Git e versionamento

### 1.1 Commits

- **Agentes de IA NÃO devem fazer `git commit`** a menos que um integrante solicite explicitamente na conversa.
- **Integrantes humanos** coordenam commits em conjunto; evitar commits genéricos ("ajustes", "wip").
- Mensagens em português, estilo imperativo, descrevendo o *porquê*:
  - ✅ `feat: adiciona walk-forward com horizonte h=7`
  - ✅ `fix: corrige lag de temperatura para evitar vazamento`
  - ❌ `update`, `changes`, `fix stuff`

### 1.2 Push

- **Agentes de IA NÃO devem fazer `git push`** — nem com `-u`, nem force push.
- Push é responsabilidade de integrantes humanos após revisão.
- **Nunca** force push em `main`/`master`.

### 1.3 Outras proibições para agentes

- Não alterar `git config`
- Não usar `--no-verify`, `--amend` (exceto se humano pedir e condições de segurança atendidas)
- Não fazer operações destrutivas (`reset --hard`, `push --force`) sem pedido explícito

### 1.4 O que versionar

| Versionar | Não versionar (`.gitignore`) |
|-----------|------------------------------|
| `notebooks/*.ipynb` — **entregas principais** | `data/` inteira (exceto `data/README.md`) |
| `context/`, `docs/` | `artifacts/` inteira (exceto `artifacts/README.md`) |
| `requirements.txt` | `.env`, credenciais, `__pycache__/`, `.venv/` |
| `data/README.md`, `artifacts/README.md` | Pickles (`.pkl`), datasets, CSVs derivados |

**Dados (`data/`):** raw fornecido + **todo dado gerado** (`cleaned_{base_id}.csv`, `predictions_*`, `mae_*`, etc.) — ver nomenclatura em [`data/README.md`](../data/README.md).

**Artifacts (`artifacts/`):** apenas modelos treinados (`{modelo}.pkl` + `{modelo}_meta.json`) — ver [`artifacts/README.md`](../artifacts/README.md).

---

## 2. Dados

- Dados **fornecidos ao grupo** — não vêm do git; cada integrante popula `data/` localmente.
- **Uma pasta por dataset:** `data/base_01/` … `data/base_05/` (ver `data/README.md`).
- Usar **exatamente** as versões congeladas das 5 bases compartilhadas pela turma.
- Notebooks carregam/salvam via: `../data/base_XX/` (dados) e `../artifacts/base_XX/` (pickles).
- Seguir nomenclatura ADR-0005: `cleaned_{base_id}.csv`, `predictions_{modelo}_{base_id}.csv`, etc.
- Alteração de base, horizonte ou protocolo → aprovação do grupo + nova ADR.

---

## 3. Metodologia

- **MAE** é a única métrica principal de comparação (ADR-0001).
- Não agregar MAE entre bases com escalas diferentes.
- **Walk-forward** obrigatório; mesmas origens e horizonte para todos os modelos (ADR-0002).
- Hiperparâmetros fixos durante avaliação final no conjunto de teste.
- **Anti-leakage:** nenhuma feature pode usar valor observado no futuro relativo à data de origem (ADR-0003).

---

## 4. Feature engineering

- Mesmo conjunto de features para Random Forest e modelo de especialização (quando compatível).
- Documentar disponibilidade temporal de cada variável externa.
- Tratar NaN produzidos por lags e janelas móveis de forma explícita.

---

## 5. Reprodutibilidade

- Fixar `random_state` / seeds onde aplicável.
- Pin de versões de bibliotecas.
- Resultados devem ser reproduzíveis a partir dos arquivos entregues (requisito do enunciado).

---

## 6. Uso de Inteligência Artificial

Conforme enunciado (seção 15):

- Revisão crítica de todo código e texto gerado por IA
- Compreensão do código antes de incluir no relatório
- Responsabilidade integral do grupo sobre resultados apresentados

Agentes devem **facilitar**, não **substituir** o raciocínio do grupo.

---

## 7. Documentação de contexto

- Decisões estruturais → ADR em `context/adr/`
- Detalhes técnicos → SPECs em `context/specs/`
- Handoff de sessão (quando solicitado) → `context/handoff/handoff_{resumo}.md`
- Conflito entre documentos → ver precedência em [`README.md`](README.md)

---

## 8. Entrega

- Pacote único: `Grupo_03_Trabalho_Series_Temporais.zip`
- Conteúdo mínimo conforme [`PRD.md`](PRD.md) seção 6
- Registro de demandas diário por integrante (apêndice para o professor)

---

## 9. Registro de demandas (gestão do grupo)

Cada linha do registro deve ter:

| Campo | Valores |
|-------|---------|
| Data | dd/mm |
| Integrante | Nome |
| Demanda | Descrição objetiva (não "ajudei no trabalho") |
| Evidência | Arquivo, seção ou resultado |
| Carga | Baixa / Média / Alta |
| Complexidade | Baixa / Média / Alta |
| Status | A fazer / Em andamento / Concluída |

Carga e complexidade são critérios **independentes**.
