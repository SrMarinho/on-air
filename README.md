# ON AIR! — *The Show Must Fall*

Party platformer multiplayer: um programa de auditório onde o cenário quer te derrubar.
A cada rodada os jogadores pegam um item na roleta, montam o cenário e correm até o Microfone de Ouro.

| Parte | Stack | Pasta |
|---|---|---|
| Servidor autoritativo | Python 3.12, FastAPI, ECS próprio, SQLAlchemy 2 async, Alembic, uv | [`backend/`](backend) |
| Cliente web | TypeScript, Vue 3, Pinia, Zod, Axios, Tailwind 4, PixiJS 8, GSAP | [`clients/web/`](clients/web) |
| Cliente desktop/mobile | Godot 4 (GDScript) | `clients/godot/` (em breve) |
| Arte e áudio | PNG/JSON compartilhados por todos os clientes | [`assets/`](assets) |
| Contratos | JSON Schema do protocolo, tokens de design | [`shared/`](shared) |

## Começo rápido

```bash
docker compose up -d postgres                 # banco
cd backend && uv sync && uv run alembic upgrade head
uv run uvicorn onair.main:app --reload        # http://localhost:8000/docs

cd clients/web && npm install && npm run dev  # http://localhost:5173
```

O modo **Treinar** (`/sandbox`) roda offline, sem backend. **Jogar online** exige o backend
(sem Docker, use SQLite: veja [docs/progress.md](docs/progress.md#para-retomar)).

## Documentação

- **[Progresso — onde paramos](docs/progress.md)**
- [Arquitetura](docs/architecture.md) — módulos, ECS, servidor autoritativo, SOLID
- [Protocolo WebSocket](docs/protocol.md) — mensagens, fluxo de partida
- [Gameplay](docs/gameplay.md) — fases, física, itens, pontuação
- [Desenvolvimento](docs/development.md) — setup, testes, lint, migrations, commits
- [Pipeline de assets](docs/assets.md) — estrutura, animações, tokens
- [Design system](docs/design-system.md) — identidade visual completa
- [Roadmap](docs/roadmap.md)
