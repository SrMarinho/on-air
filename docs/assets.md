# Pipeline de assets

Toda arte/áudio fica **uma vez** em `assets/` na raiz e é consumida pelos dois clientes
(web via `publicDir` do Vite; Godot via importação).

## Estrutura

```
assets/
├── characters/<personagem>/{sprites,data,portraits}
├── environment/{tiles/<tema>,backgrounds,decorations}
├── gameplay/{structures,hazards,effects,collectibles,fixed}
├── effects/   ui/   fonts/   audio/   atlases/
```

Nomes: minúsculas, hífen, sem acento (`calouro-run.png`, `canhao-de-confete`).

## Animações de personagem

Cada personagem tem `data/animations.json`. Os campos de **tempo** são autorais; os de
**geometria** são gerados.

```jsonc
"run": {
  "texture": "calouro-run.png",   // autoral: arquivo em sprites/
  "frames": 10,                   // autoral: total de quadros
  "columns": 5,                   // autoral: quadros por linha da folha
  "duration": 500,                // autoral: ms do ciclo inteiro
  "loop": true,                   // autoral
  "next": "idle",                 // autoral (opcional): o que toca ao terminar
  "frameWidth": 396,              // gerado
  "frameHeight": 396,             // gerado
  "anchor": { "x": 0.45, "y": 0.96 }, // gerado: pés do personagem no quadro
  "scale": 1.06                   // gerado: iguala altura do personagem à do idle
}
```

Depois de adicionar/alterar uma folha:

```bash
uv run --no-project --with pillow python scripts/assets/build_animations.py assets/characters/calouro
```

Folhas ausentes (ex.: `calouro-build.png`) são puladas; o cliente usa `idle` no lugar.

### Animações usadas pelo cliente

`idle`, `runStart`, `run`, `brake`, `turn`, `jumpAnticipation`, `jumpRise`, `jumpApex`, `fall`,
`land`, `hit`, `death`, `build`. A escolha é feita por `AnimationController`
(`clients/web/src/game/render/animationController.ts`) a partir de velocidade e contato com o chão.

## Tokens de design

`shared/design/tokens.json` é a fonte única de cores, fontes, espaçamentos, raios, movimento,
cores/formas de jogador e medidas de mundo (seção 23.4 do design system).

- Web: `npm run tokens` → `src/design/tokens.css` (tema Tailwind); TS importa o JSON via `@/design/tokens`.
- Backend: cores de jogador em `session_factory.py` seguem o mesmo arquivo.
- Godot: ler o mesmo JSON.

## Checklist

Ver seção 25 de [design-system.md](design-system.md).
