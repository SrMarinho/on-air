# Progresso do projeto

> Atualizado em 08/10/2026. Último commit de código: `feat(web): add online play with login, rooms, lobby and predicted match client`.

## Onde paramos

O **cliente web online está jogável de ponta a ponta**: cadastro/login → lista de salas → sala
(cadeiras, pronto, dono começa) → roleta (N+1 cartões) → montagem (fantasma, válido/inválido,
clique coloca) → corrida (predição do próprio jogador, rivais interpolados, placas de nome) →
Medidor de Audiência → próxima rodada → tela de fim → volta à sala.

Testado com **dois navegadores reais** (Playwright + Chrome) contra o backend local, sem erros
no console. O **próximo passo** é o **cliente Godot (M6)**; antes dele, vale fazer os itens de
polimento marcados como *próximo* abaixo.

### Para retomar

```bash
# Backend com SQLite (sem Docker) e fases curtas para testar
cd backend
ONAIR_DATABASE_URL="sqlite+aiosqlite:///./dev.db" uv run alembic upgrade head
ONAIR_DATABASE_URL="sqlite+aiosqlite:///./dev.db" \
ONAIR_JWT_SECRET="troque-por-um-segredo-com-32-bytes-ou-mais" \
ONAIR_PICK_SECONDS=6 ONAIR_PLACE_SECONDS=8 ONAIR_RUN_SECONDS=15 \
uv run uvicorn onair.main:app --port 8000

# Web
cd clients/web && npm run dev     # http://localhost:5173
```

Abra duas janelas (uma anônima), crie duas contas, uma cria a sala, a outra entra pelo link
("Copiar link"), marca **Pronto**, o dono clica **Começar o programa**.

## Feito

### Backend (Python, FastAPI, ECS)
- [x] Monorepo, uv, ruff, mypy strict, pytest (34 testes), Alembic async, docker-compose Postgres
- [x] Core: config (`ONAIR_*`), banco async, JWT + Argon2, erros de domínio, portas
- [x] Engine ECS genérica (`World`, `Scheduler`, `EventBus`, consultas tipadas)
- [x] Auth (cadastro, login, refresh), perfil `/players/me`, estatísticas de partidas
- [x] Gateway WebSocket: auth no 1º frame, fila de saída por conexão, dispatcher por tipo
- [x] Salas em memória: entrar/sair, dono, pronto, começar, volta ao lobby ao fim
- [x] Simulação 60 Hz / snapshots 30 Hz: gravidade, corrida, pulo com coyote/buffer, pulo variável,
      parede (deslizar/pular), plataformas móveis que carregam, perigos, chegada, queda
- [x] Fases (State): roleta → montagem → corrida → placar → fim; itens block/plank/spikes/
      moving_platform/bomb; pontuação do design (Chegou +2, Primeiro +1, Exclusiva +1, meta 12)
- [x] Durações das fases configuráveis por env (`ONAIR_PICK_SECONDS` etc.)
- [x] JSON Schema do protocolo exportado em `shared/protocol/`

### Cliente web (TypeScript, Vue 3, Pinia, Zod, Axios, Tailwind 4, PixiJS 8, GSAP)
- [x] Tokens de design únicos (`shared/design/tokens.json` → CSS/TS), fontes e componentes do design system
- [x] Física espelhada do servidor (`game/engine/physics.ts`)
- [x] Calouro animado a partir de atlas limpos (sem tremedeira nem vazamento de quadros)
- [x] Cenário com tileset do estúdio, largada, Microfone de Ouro, perigo listrado
- [x] Treino offline: HUD, pausa "Voltamos já", modo Montagem
- [x] Online: login/cadastro (Zod + refresh automático de token), salas (REST), lobby (WS)
- [x] Partida online: `OnlineGame` com predição + reconciliação, interpolação (100 ms),
      itens estáticos (`level_items`), plataformas móveis com setas, placas de nome, câmera
- [x] Telas: roleta, dica de montagem, Medidor de Audiência, fim com ranking, toasts de erro
- [x] Vitest (10 testes): posicionamento, interpolação, predição

### Assets e docs
- [x] Estrutura `assets/` (personagens, cenário, gameplay, UI, atlas) espelhada em `F:\Downloads\on-air`
- [x] Scripts: `build_animations.py` (atlas), `build_sprite_manifests.py` (itens/tileset), `build_ui.py` (fatiar UI)
- [x] Docs: arquitetura, protocolo, gameplay, desenvolvimento, assets, design system, roadmap, este arquivo

## Falta

### Próximo (polimento do web online)
- [ ] Contagem "3, 2, 1, NO AR!" antes da corrida (§15.8) — hoje começa direto
- [ ] Ordem de escolha na roleta (último no placar escolhe primeiro, 10 s por jogador) — hoje é simultânea
- [ ] Reconexão automática do WebSocket e tela "SINAL FRACO, RECONECTANDO…"
- [ ] Seta de jogador fora da tela, coroa do líder, estado vivo/chegou/eliminado nas placas do rodapé
- [ ] Gag de eliminação (hitstop, recorte de papelão, confete) e tremida de tela
- [ ] Momento Viral (+1 por rival eliminado pela sua armadilha): rastrear dono do perigo no `HazardSystem`
- [ ] Arte de espinhos/dinamite (pastas `gameplay/hazards/` ainda vazias); hoje espinho é desenhado em código
- [ ] Testes de componentes Vue e E2E automatizado no repositório (hoje o E2E roda por script local)

### Depois
- [ ] **M6 Cliente Godot** (desktop) com o mesmo protocolo e assets
- [ ] **M8 Mobile** (Godot Android/iOS) com controles de toque
- [ ] Itens do design system: alçapão, holofote, lança-torta, canhão de confete, microfone com fio,
      espuma, palco giratório, escadaria (precisa de "subir degrau" na física), trilho, elevador; rotação 90°
- [ ] Demais personagens (Tia da Excursão, Vovô, Pãozinho, Mini-Herói) e seleção de personagem
- [ ] Código de sala de 4 letras, quadros especiais, VT dos melhores momentos, chat
- [ ] Fontes woff2 locais, i18n PT/EN, opções (som, vídeo, acessibilidade), áudio
- [ ] Postgres validado de verdade (até aqui só SQLite: Docker não está instalado nesta máquina)
- [ ] Deploy, msgpack opcional, métricas

## Decisões importantes

- **Servidor autoritativo**: toda regra roda no Python; cliente só prediz o próprio movimento.
- **Mesmo protocolo para web e Godot** (WebSocket + JSON validado por Pydantic/Zod).
- **Arte fonte ≠ arte do jogo**: folhas geradas ficam em `characters/*/sprites` e `ui/sheets`;
  o jogo usa atlas/recortes gerados por script. Rodar os scripts após colar arte nova.
- **Texto fora dos sprites** (§21.2): sprites com texto (botões "JOGAR") são só referência visual.
