# Arquitetura

## Visão geral

```
 ┌────────────┐   REST (auth, salas, níveis)    ┌──────────────────────────────┐
 │ Web (Vue)  │ ──────────────────────────────▶ │  FastAPI                     │
 │ Godot      │ ◀──── WebSocket /ws ──────────▶ │  ├─ gateway (WS, dispatcher) │
 └────────────┘   inputs ↑   snapshots ↓        │  ├─ modules/* (domínio)      │
                                                │  └─ match loop 60 Hz (ECS)   │
                                                └──────────────┬───────────────┘
                                                               │ SQLAlchemy async
                                                         ┌─────▼─────┐
                                                         │ Postgres  │
                                                         └───────────┘
```

- **Servidor autoritativo.** Toda regra de jogo roda no backend. Clientes enviam só intenção
  (`input`, `pick_item`, `place_item`) e desenham o que o servidor diz.
- **Mesmo protocolo para todos os clientes.** Web e Godot falam WebSocket + JSON idênticos.
- **Simulação a 60 Hz, snapshots a 30 Hz.** O cliente prediz o próprio jogador com a mesma física
  (`clients/web/src/game/engine/physics.ts` espelha `backend/.../match/domain/physics.py` e `systems.py`)
  e interpola os demais.

## Backend (`backend/src/onair`)

| Pacote | Responsabilidade |
|---|---|
| `core/` | Config (pydantic-settings), banco, segurança (JWT, Argon2), erros de domínio, portas transversais (`Broadcaster`) |
| `ecs/` | Engine ECS genérica: `World`, `Entity`, `Component`, `System`, `Scheduler`, `EventBus`. Não conhece o jogo |
| `protocol/` | Contrato do fio: mensagens Pydantic com união discriminada por `type` |
| `gateway/` | Transporte WebSocket: autenticação no 1º frame, fila de saída por conexão, `Dispatcher` de handlers |
| `modules/<nome>/` | Um módulo por contexto, em camadas: `domain/` · `application/` · `infrastructure/` · `presentation/` |
| `main.py` | *Composition root*: o único lugar que liga adaptadores às portas |

### Módulos

| Módulo | O que tem |
|---|---|
| `players` | Entidade `Player`, repositório (porta + SQL), `GET /players/me` |
| `auth` | Casos de uso `RegisterPlayer`, `Login`, `RefreshTokens`; autenticador do WS |
| `rooms` | Agregado `Room` (lobby, host, pronto), `RoomService`, handlers WS, porta `MatchPort` |
| `levels` | `LevelDefinition` (grade de tiles), repositório JSON de fases embutidas |
| `match` | Componentes/sistemas ECS do plataforma, itens, fases (State), `GameSession`, `MatchLoop`, `MatchService` |

### Regras de dependência

- `domain` não importa nada de `infrastructure`, `presentation`, FastAPI ou SQLAlchemy.
- Módulos se falam por **portas** (`Protocol`/ABC) definidas por quem consome:
  `rooms` define `MatchPort`; `match` implementa. `gateway` define `Authenticator`; `auth` implementa.
- `GameSession` é **síncrona e sem I/O** → determinística e testável. O `MatchLoop` (asyncio) a dirige.

### Princípios aplicados

| Princípio | Onde |
|---|---|
| SRP | Um sistema ECS por comportamento (`GravitySystem`, `PhysicsSystem`, `HazardSystem`…) |
| OCP | Item novo = subclasse de `ItemDefinition` registrada; mensagem nova = novo `MessageHandler` |
| LSP | Toda `Phase` responde `tick/pick/place`; fases que não aceitam algo lançam `PhaseRuleError` |
| ISP | Portas pequenas: `Broadcaster`, `MatchPort`, `MatchResultRecorder`, `Authenticator` |
| DIP | Casos de uso recebem repositórios abstratos; `main.py` injeta as implementações |
| State | `PickPhase → PlacePhase → RunPhase → ScorePhase → (PickPhase \| EndPhase)` |
| Strategy | `Dispatcher` escolhe handler pelo tipo da mensagem |

## Cliente web (`clients/web/src`)

| Pasta | Responsabilidade |
|---|---|
| `game/engine/` | TS puro, sem Vue/Pixi: física (espelho do servidor), parser de nível, geometria |
| `game/render/` | Pixi: `LevelView`, `CharacterView`, `AnimationController` (puro), `Camera` |
| `game/input/` | Teclado (gamepad/touch depois) |
| `game/sandbox/` | Modo treino offline |
| `design/` | Tokens (gerados de `shared/design/tokens.json`) |
| `components/`, `views/`, `router/` | UI Vue (menus, HUD, alertas com GSAP) |

Regra: Vue cuida de telas e HUD; o canvas do jogo é Pixi, controlado por classes TS fora do Vue.
