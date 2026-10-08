# Desenvolvimento

## Pré-requisitos

- Python 3.12+ e [uv](https://docs.astral.sh/uv/)
- Node 20+ (testado com 24)
- Docker (para o Postgres) — ou aponte `ONAIR_DATABASE_URL` para outro Postgres
- Godot 4.x (cliente desktop/mobile)

## Backend

```bash
cd backend
cp .env.example .env                 # ajuste ONAIR_JWT_SECRET (32+ bytes)
uv sync
docker compose -f ../docker-compose.yml up -d postgres
uv run alembic upgrade head
uv run uvicorn onair.main:app --reload
```

| Tarefa | Comando |
|---|---|
| Testes | `uv run pytest` (usa SQLite temporário, não precisa de Postgres) |
| Lint / formatação | `uv run ruff check . && uv run ruff format .` |
| Tipos | `uv run mypy src tests` (strict) |
| Nova migration | `uv run alembic revision --autogenerate -m "descricao"` |
| Exportar protocolo | `uv run python scripts/export_protocol.py` |

Variáveis (`ONAIR_*`): `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, `SIMULATION_HZ`,
`SNAPSHOT_HZ`, `MAX_PLAYERS_PER_ROOM`. Ver `core/config.py`.

## Cliente web

```bash
cd clients/web
npm install
npm run dev         # gera tokens e sobe o Vite em :5173
npm run build       # typecheck + build
npm run test        # vitest
```

- `publicDir` do Vite aponta para `assets/` na raiz: `/characters/calouro/...` funciona direto.
- `@design/*` → `shared/design`, `@levels/*` → fases do backend (usadas no treino offline).
- Nunca use hex solto: cores vêm de `shared/design/tokens.json` (`npm run tokens` gera o CSS).

## Commits

Conventional Commits: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `style`, `perf`, `ci`,
`build`, `revert` — com escopo quando fizer sentido (`feat(match): …`).
