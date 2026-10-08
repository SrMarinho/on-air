# Roadmap

## Feito

- [x] M0 Monorepo, uv, Vite, docker-compose, lint/tipos estritos
- [x] M1 Core backend, Postgres async, Alembic, auth JWT, players
- [x] M2 Engine ECS genérica + testes
- [x] M3 Gateway WebSocket, salas, lobby, pronto/host
- [x] M4 Simulação do plataforma (60 Hz), snapshots (30 Hz), nível base
- [x] M7 (lógica) Fases roleta → montagem → corrida → placar, registry de itens, pontuação
- [x] Cliente web: treino offline com Calouro animado, câmera, tokens do design system
- [x] Treino: HUD (placa, cronômetro, placa J1, pausa "Voltamos já") e modo Montagem (grade, fantasma, válido/inválido, bandeja de itens)

## Próximo

- [ ] **M5 Web online:** login/registro, lista e criação de salas, lobby, WS tipado com Zod,
      render de snapshots, predição + reconciliação, interpolação, HUD (placa, cronômetro, placas de jogador)
- [ ] Roleta (cartões de item) e montagem (cursor com fantasma, válido/inválido) no web
- [ ] **M6 Cliente Godot** (desktop): mesmo protocolo, mesmos assets
- [ ] **M8 Mobile** (Godot Android/iOS): controles de toque
- [ ] Momento Viral (rastrear dono da armadilha que eliminou)
- [ ] Itens do design system: alçapão, holofote, lança-torta, canhão de confete, microfone com fio,
      espuma, palco giratório, escadaria, trilho de câmera, elevador; rotação 90°
- [ ] Telegraph ≥ 0,4 s em todo perigo
- [ ] Gag de eliminação (hitstop, recorte de papelão, confete), tremida de tela
- [ ] Código de sala de 4 letras, quadros especiais, VT dos melhores momentos
- [ ] Fontes woff2 self-hosted, i18n PT/EN, opções de acessibilidade
- [ ] M9: msgpack opcional, reconexão, editor de fases, métricas
