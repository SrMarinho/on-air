# Gameplay

## Fluxo da partida

```
lobby ──start──▶ PICK ──▶ PLACE ──▶ RUN ──▶ SCORE ──┬──▶ PICK (próxima rodada)
                (roleta)  (montagem) (no ar!)       └──▶ END (alguém atingiu a meta)
```

| Fase | Duração padrão | Termina quando |
|---|---|---|
| `pick` | 15 s | Todos pegaram um item (sobra 1 oferta: N+1). No tempo, item aleatório |
| `place` | 20 s | Todos posicionaram. No tempo, item não posicionado é descartado |
| `run` | 60 s | Todos chegaram ou foram eliminados |
| `score` | 4 s | Sempre por tempo |

Valores em `MatchRules` (`backend/.../match/domain/context.py`).

## Pontuação (Medidor de Audiência)

| Segmento | Pontos |
|---|---|
| CHEGOU | +2 |
| PRIMEIRO A CHEGAR | +1 |
| EXCLUSIVA! (só ele chegou) | +1 |
| MOMENTO VIRAL! (rival eliminado pela sua armadilha) | +1 *(pendente)* |

- Todos chegaram → **"A audiência despencou!"**, ninguém pontua.
- Ninguém chegou → **"Programa sem vencedor!"**.
- Meta padrão: 12 pontos (`ScoringRules.target`).

## Física (servidor = cliente)

| Parâmetro | Valor |
|---|---|
| Tile | 32 px |
| Caixa do jogador | 22 × 35 px (0,7 × 1,1 tile) |
| Gravidade / queda máx. | 2200 px/s² / 900 px/s |
| Corrida | 260 px/s (acel. 3000 no chão, 1800 no ar) |
| Pulo | 720 px/s, soltar o botão corta para 300 px/s |
| Coyote time / buffer de pulo | 100 ms / 120 ms |
| Parede | desliza a 180 px/s; pulo de parede empurra 320 px/s |

Ordem por tick: `KinematicPath → Gravity → PlayerControl → Physics → Hazard → Goal → OutOfBounds`.

## Itens

| Chave | Categoria | Tamanho | Efeito |
|---|---|---|---|
| `block` | Estrutura (praticável) | 1×1 | Sólido |
| `plank` | Estrutura (praticável longo) | 3×1 | Sólido |
| `moving_platform` | Estrutura | 3×1 | Vai e volta 4 tiles, carrega quem está em cima |
| `spikes` | Perigo letal | 1×1 | Elimina |
| `bomb` | Perigo (dinamite) | 3×3 | Destrói itens posicionados na área |

Novo item: subclasse de `ItemDefinition` em `match/domain/items.py` + registro em
`default_item_registry()`. Itens do design system (alçapão, holofote, lança-torta, canhão de
confete, microfone com fio, espuma, palco giratório, escadaria, trilho, elevador) estão no roadmap.

## Fases (níveis)

Grade de caracteres em `backend/src/onair/modules/levels/infrastructure/data/*.json`:

| Char | Significado |
|---|---|
| `.` | Vazio |
| `#` | Piso do palco |
| `^` | Perigo fixo |
| `S` | Largada (spawn) |
| `G` | Microfone de Ouro (chegada) |
