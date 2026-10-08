# Protocolo WebSocket

Endpoint: `ws://<host>/ws`. Frames de texto JSON, sempre com campo `type`.
Fonte da verdade: `backend/src/onair/protocol/`. JSON Schema gerado em `shared/protocol/`
(`uv run python scripts/export_protocol.py` dentro de `backend/`).

## Handshake

1. Cliente faz login via REST (`POST /auth/login`) e recebe `access_token`.
2. Abre o socket e envia **como primeiro frame**: `{"type":"auth","token":"<access_token>"}`.
3. Servidor responde `auth_ok` ou fecha com código **1008** (token inválido/ausente em 10s).
4. Se o mesmo jogador conectar de novo, a conexão antiga é fechada com código **4000**.

## Cliente → servidor

| `type` | Campos | Quando |
|---|---|---|
| `auth` | `token` | Primeiro frame |
| `join_room` | `room_id` | Entrar numa sala (criada via `POST /rooms`) |
| `leave_room` | — | Sair da sala |
| `set_ready` | `ready` | Lobby |
| `start_match` | — | Host, com todos prontos |
| `input` | `seq`, `left`, `right`, `jump` | Corrida; enviar a cada frame de simulação (`seq` crescente) |
| `pick_item` | `offer_id` | Fase `pick` |
| `place_item` | `tile_x`, `tile_y` | Fase `place` |
| `ping` | `client_time` | Medir latência |

## Servidor → cliente

| `type` | Conteúdo |
|---|---|
| `auth_ok` | `player_id`, `username` |
| `error` | `code` (`invalid_message`, `not_allowed`, `not_found`, `conflict`, `not_host`…), `message` |
| `room_state` | Sala completa: membros, host, pronto, status |
| `match_started` | Layout do nível (linhas de tiles), jogadores e cores, `target_score`, `simulation_hz` |
| `phase_changed` | `phase` (`pick`/`place`/`run`/`score`/`end`), `round`, `duration`, `offers?`, `scores?` |
| `item_picked` | Quem pegou qual oferta |
| `level_items` | Lista completa dos itens estáticos posicionados (enviada quando muda) |
| `snapshot` | `tick`, `phase_time_left`, `acks` (último `seq` por jogador), entidades dinâmicas |
| `match_ended` | `winner_id`, placar final |
| `pong` | `client_time`, `server_time` |

### Entidade no snapshot

```json
{ "id": 12, "kind": "player", "x": 104.5, "y": 541.0, "w": 22, "h": 35,
  "vx": 260.0, "vy": 0.0, "player_id": "…", "state": "alive" }
```

`x, y` = canto superior esquerdo da caixa de colisão, em pixels de mundo (tile = 32).
O nível base nunca vem no snapshot: vem uma vez em `match_started`.

## Reconciliação (cliente)

1. Guarde cada input enviado com seu `seq` e o estado previsto resultante.
2. Ao receber `snapshot`, pegue `acks[meu_id]`, descarte inputs `≤ ack`, aplique posição/velocidade
   do servidor e reaplique os inputs restantes com `stepPlayer`.
3. Demais jogadores: interpole entre os dois últimos snapshots (~100 ms atrás).
