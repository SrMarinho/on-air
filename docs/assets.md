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

As folhas em `characters/<personagem>/sprites/` são **fonte** (qualquer layout e escala). O jogo
usa **atlas gerados** em `atlases/characters/<personagem>/`, que o script produz assim:

1. separa cada quadro por componentes conectados, sem pixels vazando do quadro vizinho;
2. iguala o tamanho do personagem entre folhas (altura do corpo + área do topete vs. `idle`);
3. alinha todos os quadros no mesmo pivô (centro do tronco e pés), sem tremedeira;
4. empacota em células uniformes (personagem do `idle` com 160 px de altura).

```jsonc
"run": {
  "texture": "calouro-run.png",   // autoral: folha fonte em sprites/
  "frames": 10,                   // autoral
  "columns": 5,                   // autoral: quadros por linha na folha fonte
  "duration": 500,                // autoral: ms do ciclo
  "loop": true,                   // autoral
  "next": "idle",                 // autoral (opcional)
  "scaleOverride": 0.6,           // autoral (opcional): força a escala relativa ao idle
  "atlas": "atlases/characters/calouro/calouro-run.png", // gerado
  "atlasColumns": 8, "frameWidth": 153, "frameHeight": 159, // gerado
  "anchor": { "x": 0.5, "y": 0.97 },                       // gerado: pés
  "relativeScale": 0.987                                   // gerado: escala usada
}
```

Depois de adicionar/alterar uma folha:

```bash
uv run --no-project --with pillow --with numpy --with scipy     python scripts/assets/build_animations.py assets/characters/calouro
```

Se uma animação parecer maior/menor que as outras, ajuste `scaleOverride` e rode de novo.
Folhas ausentes (ex.: `calouro-build.png`) são puladas; o cliente usa `idle` no lugar.

### Animações usadas pelo cliente

`idle`, `runStart`, `run`, `brake`, `turn`, `jumpAnticipation`, `jumpRise`, `jumpApex`, `fall`,
`land`, `hit`, `death`, `build`. A escolha é feita por `AnimationController`
(`clients/web/src/game/render/animationController.ts`) a partir de velocidade e contato com o chão.

## Itens e peças fixas (`assets/gameplay/items.json`)

```jsonc
"praticavel-longo": {
  "texture": "structures/praticavel/praticavel-longo.png", // autoral
  "category": "structure",       // autoral: structure | hazard | effect | bonus | fixed (§7)
  "tiles": { "w": 3, "h": 1 },   // autoral: área no grid
  "serverItem": "plank",         // autoral (opcional): chave do item no backend
  "bounds": { "x": 124, "y": 232, "w": 1924, "h": 241 } // gerado: área opaca da imagem
}
```

O cliente recorta a imagem em `bounds` e encaixa no tamanho em tiles, então a arte pode ter
qualquer margem transparente.

| Chave | Arquivo |
|---|---|
| `praticavel` | `gameplay/structures/praticavel/praticavel.png` |
| `praticavel-longo` | `gameplay/structures/praticavel/praticavel-longo.png` |
| `rotating-stage` | `gameplay/structures/rotating-stage/rotating-stage.png` |
| `stairs` | `gameplay/structures/stairs/stairs.png` |
| `camera-rail` | `gameplay/structures/camera-rail/camera-rail.png` |
| `stage-lift` | `gameplay/structures/stage-lift/stage-lift.png` |
| `start-platform` | `gameplay/fixed/start-platform.png` |
| `golden-microphone` | `gameplay/fixed/golden-microphone.png` |

## Tilesets (`environment/tiles/<tema>/<parte>/<nome>.json`)

Folha em grade + nome de cada célula (autoral); `frames` com o recorte de cada tile é gerado.
Piso do estúdio (`studio-floor`, 4×2): `top`, `top-left`, `top-right`, `top-narrow`,
`top-left-alt`, `top-right-alt`, `fill`, `fill-base`. O cliente escolhe o tile pelos vizinhos
(topo exposto, bordas, interior, última linha).

Depois de adicionar item ou tileset:

```bash
uv run --no-project --with pillow python scripts/assets/build_sprite_manifests.py
```

## Tokens de design

`shared/design/tokens.json` é a fonte única de cores, fontes, espaçamentos, raios, movimento,
cores/formas de jogador e medidas de mundo (seção 23.4 do design system).

- Web: `npm run tokens` → `src/design/tokens.css` (tema Tailwind); TS importa o JSON via `@/design/tokens`.
- Backend: cores de jogador em `session_factory.py` seguem o mesmo arquivo.
- Godot: ler o mesmo JSON.

## Checklist

Ver seção 25 de [design-system.md](design-system.md).
