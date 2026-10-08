# ON AIR! — Design System Visual

> *The show must fall.* O programa de auditório onde o cenário quer te derrubar.

Documento de referência visual do jogo **ON AIR!** (título em português: **NO AR!**). Ele descreve a identidade, as cores, a tipografia, as regras de desenho dos sprites, todos os personagens jogáveis e não jogáveis, cada item e peça de cenário, todas as telas e menus, os componentes de interface, a animação, o som e a voz do jogo. Quem for desenhar, animar ou programar qualquer coisa do jogo deve partir daqui.

---

## Sumário

1. [Conceito e pilares visuais](#1-conceito-e-pilares-visuais)
2. [Marca: nome, logo e bordões](#2-marca-nome-logo-e-bordões)
3. [Cores](#3-cores)
4. [Tipografia](#4-tipografia)
5. [Grid, espaçamento, raios, contornos e sombras](#5-grid-espaçamento-raios-contornos-e-sombras)
6. [Linguagem dos sprites](#6-linguagem-dos-sprites)
7. [Código de categorias: o que mata, o que atrapalha, o que segura](#7-código-de-categorias)
8. [Personagens jogáveis](#8-personagens-jogáveis)
9. [Personagens não jogáveis (NPCs)](#9-personagens-não-jogáveis-npcs)
10. [Itens: estruturas](#10-itens-estruturas)
11. [Itens: perigos letais](#11-itens-perigos-letais)
12. [Itens: efeitos não letais](#12-itens-efeitos-não-letais)
13. [Bônus e coletáveis](#13-bônus-e-coletáveis)
14. [Palco e cenário](#14-palco-e-cenário)
15. [Fluxo da partida e telas](#15-fluxo-da-partida-e-telas)
16. [HUD durante o jogo](#16-hud-durante-o-jogo)
17. [Componentes de interface](#17-componentes-de-interface)
18. [Ícones](#18-ícones)
19. [Movimento, animação e feedback](#19-movimento-animação-e-feedback)
20. [Som](#20-som)
21. [Voz, textos e bordões](#21-voz-textos-e-bordões)
22. [Acessibilidade](#22-acessibilidade)
23. [Especificações técnicas para web](#23-especificações-técnicas-para-web)
24. [Nomenclatura e organização de arquivos](#24-nomenclatura-e-organização-de-arquivos)
25. [Checklist de um asset novo](#25-checklist-de-um-asset-novo)

---

## 1. Conceito e pilares visuais

Os jogadores são participantes de um programa de auditório de domingo, transmitido ao vivo e completamente fora de controle. A cada rodada eles giram a **Roleta de Prêmios**, pegam um item, viram contrarregras por alguns segundos para **montar o cenário** e, quando a placa de **ON AIR** acende, correm da largada até o **Microfone de Ouro**. Quem manda na pontuação é a **audiência**.

A estética mistura **TV brasileira dos anos 80 e 90** (placas luminosas, letreiros com lâmpadas, telão com barras de cor, cortina de veludo, plateia com cartazes) com **desenho animado flat e contornado**, que é rápido de produzir para um dev solo e legível em telas pequenas.

### Os cinco pilares

1. **Legibilidade antes de tudo.** Em meio segundo o jogador precisa saber o que mata, o que atrapalha e o que segura. Isso vale mais que qualquer detalhe bonito. A seção 7 define o código que garante isso.
2. **Silhueta antes de cor.** Quatro jogadores pulando ao mesmo tempo só são distinguíveis pela forma. Cada personagem tem um recorte único: o topete do calouro, a bengala do vovô, o corpo redondo do Pãozinho.
3. **Exagero de palco.** Tudo é cenário, nada é "real": as dinamites são cenográficas, as tortas são de chantilly, o perigo é teatral. O tom é de pastelão, nunca de violência.
4. **Brilho de estúdio.** O ambiente é escuro e os elementos importantes "acendem": a placa ON AIR, os holofotes, o letreiro com lâmpadas, o Microfone de Ouro.
5. **Produção barata e consistente.** Formas geométricas, poucas cores por sprite, contorno uniforme e nenhum degradê. Qualquer asset novo deve ser desenhável em uma ou duas horas.

### O que evitar

- Imitar programas, apresentadores ou marcas reais (nomes, rostos, vinhetas, logos).
- Degradês, brilhos realistas, texturas fotográficas e sombras suaves nos sprites.
- Sangue ou ferimentos. A "morte" é sempre um efeito cômico (ver seção 19).
- Usar as listras amarelo e preto em qualquer coisa que não seja um perigo letal.
- Texto dentro dos sprites, porque quebra a localização. A exceção é o telão de cenário.

---

## 2. Marca: nome, logo e bordões

### Nome

| Uso | Nome |
|---|---|
| Título internacional | **ON AIR!** |
| Título em português | **NO AR!** |
| Subtítulo fixo (EN) | *The Show Must Fall* |
| Tagline (PT) | *O único programa onde o cenário quer te derrubar.* |
| Tagline alternativa | *Monte o palco. Derrube os rivais. Não caia.* |

O ponto de exclamação faz parte do nome e aparece sempre, inclusive em textos corridos ("jogue ON AIR! com os amigos").

### Logo: a placa luminosa

O logo é a **placa vermelha de "ON AIR" de estúdio de TV**, a mesma que acende dentro do jogo no início de cada corrida. Logo, interface e mecânica compartilham um único símbolo.

**Construção (arquivo base 360 × 140):**

- **Moldura externa:** retângulo `#1B1418` (tinta), cantos de 22px.
- **Painel:** retângulo `#D91E26` (vermelho no ar), recuado 12px da moldura, cantos de 14px.
- **Filete de brilho:** contorno interno de 3px em `#FF4D4F`, recuado 8px do painel, cantos de 9px. Ele simula o tubo de luz.
- **Parafusos:** quatro círculos dourados `#FFC93C` de raio 4 nos cantos da moldura.
- **Texto:** "ON AIR!" em Bungee, cor creme `#FFF4DE`, centralizado, com altura de versal em torno de 45% da altura do painel. No arquivo final o texto é convertido em curvas.

**Variações:**

| Arquivo | Uso |
|---|---|
| `logo-on-air.svg` | Logo principal, telas de título, itch.io, redes sociais |
| `logo-no-ar.svg` | Mesma construção com "NO AR!", para o lançamento em português |
| `app-icon.svg` | Ícone quadrado 128 × 128: mesma moldura e painel, com um "!" gigante no centro. Favicon e ícone de PWA |

**Estados animados do logo (tela de título e HUD):**

- **Apagada:** painel em `#5A1418`, sem filete de brilho, texto em `#8C5A5A`.
- **Acendendo:** pisca 2 vezes (60ms ligada, 80ms apagada) e então fica ligada.
- **No ar:** painel em `#D91E26`, filete aceso e brilho externo `0 0 24px rgba(255,77,79,.6)`. Pulsa levemente (opacidade do brilho de 60% a 85% num ciclo de 1,6s).
- **Intervalo:** a placa apaga e uma faixa creme atravessa com "INTERVALO" / "COMMERCIAL BREAK".

**Regras do logo:**

- Área de respiro mínima igual à altura do "O" ao redor de toda a placa.
- Tamanho mínimo de 120px de largura na tela. Abaixo disso, use o `app-icon`.
- Nunca recolorir o painel, inclinar, aplicar degradê ou colocar sobre fundo vermelho.

### Bordões oficiais

| Momento | Português | Inglês |
|---|---|---|
| Início da corrida | **Tá no ar!** | **We're on air!** |
| Jogador morre | **Caiu, perdeu!** | **Down you go!** |
| Todos chegam (rodada fácil) | **A audiência despencou!** | **Ratings dropped!** |
| Ninguém chega | **Programa sem vencedor!** | **No winner tonight!** |
| Só um chega | **Exclusiva!** | **Exclusive!** |
| Morte por armadilha de outro | **Momento viral!** | **Viral moment!** |
| Morte nos primeiros 2s | *(gongo)* **Gongou!** | *(gong)* **Gonged!** |
| Vitória da partida | **É campeão!** | **And the winner is…!** |

---

## 3. Cores

A paleta tem três camadas: as **cores de identidade** (o estúdio), as **cores de sprite** (o que é desenhado no mundo) e os **tokens de interface**, que mudam entre o tema escuro "Estúdio" (padrão do jogo) e o tema claro "Cartão" (site, itch.io, materiais impressos e modo de alto brilho).

### 3.1 Cores de identidade

| Token | Hex | Papel |
|---|---|---|
| `no-ar` | `#D91E26` | Vermelho da placa ON AIR. Cor da marca e do botão principal |
| `no-ar-brilho` | `#FF4D4F` | Só para brilho, filetes acesos e luz de gravação. Nunca para texto |
| `holofote` | `#FFC93C` | Dourado das lâmpadas, troféus, destaques e da listra de perigo |
| `turquesa` | `#19B5A5` | Cor "segura": estruturas, largada, confirmações |
| `confete` | `#FF5FA2` | Rosa dos efeitos não letais e da alegria do programa |
| `cortina` | `#8E1424` | Veludo da cortina e fundos de destaque |
| `cortina-dobra` | `#B21E35` | Luz nas dobras da cortina |
| `tinta` | `#1B1418` | Contorno de todos os sprites e listra escura de perigo |
| `creme` | `#FFF4DE` | O "branco" do jogo. Branco puro só em olhos e dentes |

### 3.2 Paleta de sprites

Toda arte do mundo é desenhada **só** com estas cores. Uma cor nova precisa entrar nesta tabela antes de ser usada.

| Grupo | Cores |
|---|---|
| Contorno | `#1B1418` |
| Claros | `#FFF4DE` creme · `#FFFFFF` branco (só olhos e dentes) · `#D9DCE3` prata |
| Madeira | `#C98A4B` madeira · `#8A5A2B` madeira escura |
| Metal | `#9AA1B3` aço · `#4E5568` aço escuro |
| Vermelhos | `#D91E26` vermelho · `#FF4D4F` vermelho aceso · `#8E1424` veludo · `#B21E35` veludo claro |
| Quentes | `#FFC93C` dourado · `#FF7A2F` laranja · `#F0C25A` massa de pão · `#D9952F` casquinha |
| Frios | `#19B5A5` turquesa · `#2FB8F0` céu · `#0E6E66` telão |
| Rosa | `#FF5FA2` confete |
| Peles | `#F2C29B` clara · `#C68A5E` média · `#8D5A3B` escura |
| Cabelos | `#5A3825` castanho · `#2A1E1A` preto · `#B7B0C2` grisalho · `#7A5C3E` tweed |
| Tecidos extras | `#3E5A7A` jeans · `#3A3340` camiseta escura |
| Piso do palco | `#5A3424` tábua · `#7A4A32` borda · `#3E2218` junta |

### 3.3 Tokens de interface por tema

| Token | Estúdio (escuro) | Cartão (claro) | Uso |
|---|---|---|---|
| `fundo` | `#1B1418` | `#FFF4DE` | Fundo das telas |
| `fundo-elevado` | `#2A2027` | `#FFFFFF` | Painéis, cartões, modais |
| `fundo-poco` | `#120D10` | `#F3E3C3` | Campos de texto, trilhas de slider, áreas rebaixadas |
| `texto` | `#FFF4DE` | `#1B1418` | Texto principal |
| `texto-suave` | `#C9B9A6` | `#6A5A4E` | Legendas, dicas, rótulos secundários |
| `linha` | `#4A3B44` | `#DCC8A6` | Divisórias decorativas |
| `linha-forte` | `#8C7A86` | `#8F7A63` | Bordas de controles (mínimo 3:1) |
| `no-ar` | `#D91E26` | `#D91E26` | Botão principal, placa, alertas de corrida |
| `sobre-no-ar` | `#FFF4DE` | `#FFF4DE` | Texto sobre vermelho (contraste 4,6:1) |
| `holofote` | `#FFC93C` | `#FFC93C` | Destaques, pontos, estrelas |
| `sobre-holofote` | `#1B1418` | `#1B1418` | Texto sobre dourado (nunca branco) |
| `turquesa` | `#19B5A5` | `#19B5A5` | Confirmação, "pronto" |
| `sobre-turquesa` | `#1B1418` | `#1B1418` | Texto sobre turquesa |
| `foco` | `#FFC93C` | `#1B1418` | Anel de foco de teclado e controle |

**Contrastes verificados:** `texto` sobre `fundo` e `fundo-elevado` passa de 12:1 nos dois temas; `texto-suave` sobre `fundo-elevado` fica em 8,2:1 no Estúdio e 6,6:1 no Cartão; `sobre-no-ar` sobre `no-ar` fica em 4,6:1.

### 3.4 Cores dos jogadores

Cada jogador recebe uma cor **e uma forma**. A forma garante que daltônicos e quem joga em telas ruins consigam diferenciar os jogadores mesmo quando as cores se confundem.

| Jogador | Cor | Hex | Forma | Onde aparece |
|---|---|---|---|---|
| J1 | Laranja | `#FF7A2F` | ● círculo | Placa de nome, anel no chão, cursor de construção, barra de audiência |
| J2 | Céu | `#2FB8F0` | ▲ triângulo | idem |
| J3 | Rosa | `#FF5FA2` | ■ quadrado | idem |
| J4 | Lima | `#B8E04A` | ◆ losango | idem |

Regras:

- A cor do jogador **nunca** pinta o personagem. Os personagens mantêm as cores próprias, e a identificação vem do anel no chão, da placa de nome e do cursor.
- Dois jogadores podem escolher o mesmo personagem. A cor e a forma é que distinguem quem é quem.
- O texto sobre as cores de jogador é sempre `#1B1418`.
- Para até 8 jogadores no futuro, as reservas são: J5 `#FFC93C` com ★, J6 `#19B5A5` com ⬢, J7 `#C9B9A6` com ✚ e J8 `#9B7BFF` com ✖.

### 3.5 Cores de estado

| Estado | Cor | Sinal extra obrigatório |
|---|---|---|
| Posição válida | `#2FB8F0` céu | Ícone ✓ no cursor |
| Posição inválida | `#FF4D4F` vermelho aceso | Ícone ✕ e tremida de 4px no cursor |
| Pronto (lobby) | `#19B5A5` turquesa | Texto "PRONTO" |
| Aguardando | `#C9B9A6` texto-suave | Texto "AGUARDANDO" e reticências animadas |
| Pontuação ganha | `#FFC93C` dourado | Estrela e "+N" |

Válido e inválido usam azul contra vermelho-alaranjado (e não verde contra vermelho), sempre com um ícone junto.

---

## 4. Tipografia

Três famílias, todas gratuitas (OFL) e servidas pelo próprio jogo em woff2.

| Família | Pesos | Papel | Fallback |
|---|---|---|---|
| **Bungee** | 400 | Display: títulos, placar, contagem regressiva, a placa ON AIR. Fonte de letreiro, feita para sinalização | `"Arial Black", sans-serif` |
| **Barlow** | 500, 700 | Texto corrido: descrições, opções, chat, dicas | `system-ui, sans-serif` |
| **Barlow Condensed** | 600, 800 | HUD e rótulos: botões, nomes de jogador, legenda do apresentador, timer | `"Arial Narrow", sans-serif` |

### Escala tipográfica

| Estilo | Família | Tamanho / entrelinha | Peso | Extras | Uso |
|---|---|---|---|---|---|
| `contagem` | Bungee | 160 / 140px | 400 | — | "3, 2, 1, NO AR!" no centro da tela |
| `titulo-tela` | Bungee | 64 / 60px | 400 | — | Título de cada tela ("SALA", "RESULTADO") |
| `titulo-secao` | Bungee | 36 / 38px | 400 | — | Títulos de painéis, nome do quadro especial |
| `placar` | Bungee | 32 / 32px | 400 | algarismos tabulares | Pontos, audiência, código da sala |
| `botao` | Barlow Condensed | 22 / 24px | 800 | caixa alta, +0,04em | Texto de botões |
| `legenda` | Barlow Condensed | 26 / 32px | 600 | — | Fala do apresentador |
| `nome-jogador` | Barlow Condensed | 16 / 18px | 800 | caixa alta, +0,06em | Placa sobre a cabeça, lista do lobby |
| `rotulo` | Barlow Condensed | 14 / 16px | 800 | caixa alta, +0,08em | Rótulos de HUD ("RODADA", "TEMPO") |
| `corpo` | Barlow | 18 / 26px | 500 | — | Descrições, regras, opções |
| `corpo-forte` | Barlow | 18 / 26px | 700 | — | Ênfase dentro do corpo |
| `pequeno` | Barlow | 14 / 20px | 500 | — | Dicas, rodapés, créditos |

Regras:

- O tamanho mínimo na tela é de **14px** numa resolução de referência de 1280 × 720. Com escala menor, o mínimo continua sendo 14px físicos.
- A Bungee é sempre em caixa alta (ela já é desenhada assim).
- Números que mudam (timer, pontos) usam algarismos tabulares para não "dançar".
- Nada de itálico, exceto em citações do apresentador em textos de marketing.

---

## 5. Grid, espaçamento, raios, contornos e sombras

### 5.1 Grid do mundo

- **1 tile = 32px** na resolução de referência (1280 × 720). Os sprites são desenhados a **64px por tile** (2×) para ficarem nítidos em telas de alta densidade.
- O palco jogável padrão tem **40 × 22 tiles** (1280 × 704), com 16px livres embaixo para a barra de HUD.
- Todo item ocupa um número inteiro de tiles e encaixa no grid durante a montagem. A rotação é em passos de 90°.
- Os personagens ocupam **1 tile de largura e 1,25 de altura** (64 × 80 na arte). A caixa de colisão é menor que o desenho: 0,7 × 1,1 tile, centralizada embaixo, para que o jogador "passe raspando" e sinta que o jogo é justo.

### 5.2 Espaçamento de interface (base de 4px)

| Token | Valor | Uso |
|---|---|---|
| `espaco-1` | 4px | Entre ícone e texto pequeno |
| `espaco-2` | 8px | Padding interno de chips e placas de nome |
| `espaco-3` | 12px | Entre itens de lista |
| `espaco-4` | 16px | Padding de botões e cartões |
| `espaco-6` | 24px | Entre blocos de um painel |
| `espaco-8` | 32px | Margem de painéis e área segura de HUD |
| `espaco-12` | 48px | Separação entre seções de tela |

### 5.3 Raios

| Token | Valor | Uso |
|---|---|---|
| `raio-sm` | 4px | Chips, placas de nome, campos pequenos |
| `raio-md` | 10px | Botões, cartões de item, campos |
| `raio-lg` | 18px | Painéis, modais, cartões de personagem |
| `raio-pilula` | 999px | Toggles, medidores, contadores |

### 5.4 Contornos

| Token | Valor | Uso |
|---|---|---|
| `contorno-sprite` | 3px a 64px/tile (1,5px na tela) | Todo sprite do mundo, cor `#1B1418` |
| `contorno-detalhe` | 2px | Detalhes internos (óculos, botões de roupa, frisos) |
| `contorno-ui` | 3px | Botões e cartões da interface, cor `#1B1418` em ambos os temas |

O contorno grosso e escuro em **todo** elemento de UI é proposital: ele conversa com os sprites e faz a interface parecer parte do mesmo desenho animado.

### 5.5 Sombras

O jogo usa **sombras duras, sem desfoque**, como recorte de papel.

| Token | Valor | Uso |
|---|---|---|
| `sombra-pop` | `0 4px 0 #120D10` (Estúdio) / `0 4px 0 #1B1418` (Cartão) | Botões e cartões em repouso |
| `sombra-pop-pressionada` | `0 1px 0` com a mesma cor | Botão pressionado (o botão desce 3px) |
| `sombra-brilho` | `0 0 24px rgba(255,77,79,.6)` | Placa ON AIR acesa, item raro na roleta |
| `sombra-chao` | elipse `#1B1418` a 25% de opacidade | Embaixo de todo personagem e objeto apoiado |

---

## 6. Linguagem dos sprites

### 6.1 Regras de desenho

1. **Contorno de 3px** em `#1B1418` em toda forma externa, com junções e pontas arredondadas.
2. **Cores chapadas.** No máximo uma tonalidade mais escura para volume, aplicada como forma recortada, nunca como degradê.
3. **Máximo de 5 cores por sprite**, sem contar o contorno e os olhos.
4. **Luz vem de cima e um pouco da esquerda.** Brilhos são pequenas formas creme no canto superior esquerdo de superfícies lisas (latas, microfones).
5. **Olhos simples:** pontos pretos de 3–4px, ou olhos brancos ovais com pupila quando o personagem precisa de expressão (Pãozinho, óculos do vovô).
6. **Todos os personagens olham para a direita** no arquivo base. O motor espelha o sprite para a esquerda.
7. **Sombra de chão** elíptica a 25% de opacidade embaixo de tudo que toca o chão.
8. **Proporção cabeçuda:** a cabeça tem cerca de 1/3 da altura total, o que ajuda a ler expressões em tamanho pequeno.

### 6.2 Exagero e escala

- Objetos que importam para a jogabilidade são **maiores do que seriam na vida real** (o microfone do apresentador, a lâmpada do holofote).
- Detalhes menores que **4px na arte (2px na tela)** somem e devem ser removidos.
- Teste todo sprite reduzido a 32px de altura. Se a silhueta não for reconhecível, simplifique.

### 6.3 Camadas de profundidade

| Camada | Conteúdo | Tratamento |
|---|---|---|
| 0, fundo distante | Cortina, telão, letreiro | Cores dessaturadas 20%, sem contorno ou contorno de 1px |
| 1, plateia | Faixa da plateia | Parallax leve (0,3×), escurecida 30% durante a corrida |
| 2, palco | Piso, itens, largada, chegada | Cores cheias, contorno completo |
| 3, jogadores | Personagens | Cores cheias, contorno completo e anel colorido no chão |
| 4, efeitos | Confete, espuma, tortas voando, faíscas | Cores cheias, partículas sem contorno abaixo de 6px |
| 5, HUD | Interface | Sempre por cima, nunca afetada pela câmera |

---

## 7. Código de categorias

Este é o sistema mais importante do jogo. Todo item pertence a **uma** categoria, e cada categoria tem uma assinatura visual exclusiva.

| Categoria | Assinatura visual | Cores dominantes | Comportamento |
|---|---|---|---|
| **Estrutura** | Madeira com topo creme ou plataformas turquesa. **Nunca tem listras** | `#C98A4B`, `#FFF4DE`, `#19B5A5` | Serve de apoio ou passagem. Pode se mover, mas não machuca |
| **Perigo letal** | **Sempre** tem uma faixa de listras amarelo e preto a 45° | `#FFC93C` + `#1B1418`, detalhes em `#D91E26` | Elimina o jogador da rodada |
| **Efeito** | Rosa-confete como cor principal, sem listras | `#FF5FA2` | Empurra, prende, faz escorregar ou atrasa. Não mata sozinho |
| **Bônus** | Dourado com brilho em estrela, flutuando levemente | `#FFC93C`, `#D91E26` | Dá pontos ao ser coletado |
| **Palco fixo** | Largada turquesa, chegada dourada | `#19B5A5`, `#FFC93C` | Não pode ser destruído |

**Listra de perigo (especificação):** faixas de 6px pretas e 6px douradas, a 45°, em módulos de 12px (na arte de 64px). Use a mesma listra em todos os perigos, sem variação de ângulo ou espessura.

**Teste dos três segundos:** mostre um print do jogo a alguém que nunca jogou e pergunte "o que te mata aqui?". Se a pessoa não apontar todos os perigos em três segundos, o código está sendo quebrado em algum lugar.

---

## 8. Personagens jogáveis

Cinco participantes do programa, todos arquétipos de quem aparece em auditório de domingo. Cada um tem a mesma caixa de colisão e a mesma física. A diferença é **só visual e de personalidade**, para que ninguém leve vantagem.

### Animações obrigatórias de todos

| Animação | Quadros | Duração | Descrição |
|---|---|---|---|
| Parado | 4 | 0,8s em loop | Respiração: corpo sobe 1px e desce |
| Correndo | 6 | 0,5s em loop | Pernas alternadas e corpo inclinado 5° para frente |
| Pulo (subida) | 2 | segura no último | Corpo esticado e braços para cima |
| Pulo (queda) | 2 | segura no último | Braços abertos e expressão de susto |
| Agarrado na parede | 2 | loop lento | Encostado de lado, deslizando |
| Pouso | 2 | 0,1s | Achatamento de 15% e volta |
| Eliminado | 6 | 0,6s | Vira um "recorte de papelão" que gira e some num puf de confete (ver seção 19) |
| Chegada | 8 | 1,2s | Dança de vitória própria de cada personagem |
| Montagem | 4 | loop | Segura o item com as duas mãos, acima da cabeça, durante a fase de construção |
| Emotes (4) | 4–6 cada | 1s | Acenar, rir, apontar, chorar (usados no lobby e entre rodadas) |

### 8.1 Tia da Excursão

> *"Vim de excursão, ganhei camiseta e agora quero o prêmio."*

- **Silhueta:** vestido trapezoidal largo e bolsa a tiracolo saindo para o lado. Tem o perfil mais largo do elenco.
- **Visual:** vestido rosa-confete `#FF5FA2` com bolinhas creme; viseira turquesa `#19B5A5` com aba longa; cabelo castanho `#5A3825` cacheado em formato de capacete; bolsa dourada `#FFC93C` com alça cruzando o peito; pele média `#C68A5E`; bochechas rosadas.
- **Expressão:** sorriso fechado e satisfeito, olhos pequenos.
- **Dança de chegada:** gira a bolsa no alto como hélice e aponta para a câmera.
- **Emote característico:** abana o rosto com a viseira.
- **Som:** "Uhuuul!" agudo, sacolejar de bijuterias ao pousar.

### 8.2 Calouro

> *"Hoje é meu dia de brilhar. Literalmente."*

- **Silhueta:** o mais alto, por causa do **topete enorme** curvado para frente. Um braço sempre erguido com o microfone.
- **Visual:** paletó dourado `#FFC93C` com brilhos creme em forma de estrela de quatro pontas; camisa branca com gravata-borboleta vermelha; calça aço escuro `#4E5568`; topete preto `#2A1E1A`; pele clara `#F2C29B`; microfone prata `#D9DCE3`.
- **Expressão:** olhos fechados em arco e boca aberta em "O", sempre cantando.
- **Dança de chegada:** joelho no chão, braço esticado para o alto, nota final segurada.
- **Emote característico:** ajeita o topete com um pente.
- **Som:** vocalizações curtas ("lá-rá-rá!") e a nota final desafinada quando é eliminado.

### 8.3 Vovô da Plateia

> *"Assisto esse programa desde 1987. Agora é minha vez."*

- **Silhueta:** **bengala** saindo à frente e boina chata. Postura levemente curvada.
- **Visual:** cardigã turquesa `#19B5A5` com botões creme; boina tweed `#7A5C3E`; óculos redondos com lentes brancas; bigode branco farto; tufos de cabelo branco nas laterais; calça aço escuro; sapatos de madeira escura; bengala de madeira `#C98A4B` com contorno.
- **Expressão:** olhos ampliados pelos óculos e bigode escondendo a boca.
- **Dança de chegada:** gira a bengala como um sapateador e dá um pulinho batendo os calcanhares.
- **Emote característico:** levanta a bengala e balança para os rivais.
- **Som:** "Ôpa!" rouco, toc-toc da bengala ao pousar.

### 8.4 Mascote Pãozinho

> *"Sou o mascote do patrocinador. Ninguém me perguntou se eu queria correr."*

- **Silhueta:** uma **bola**. Corpo redondo e irregular de pão de queijo, com braços e pernas curtíssimos. É o mais fácil de reconhecer de longe.
- **Visual:** massa `#F0C25A` com pontos de casquinha `#D9952F` e reflexos creme de queijo; luvas creme; perninhas creme; tênis vermelhos `#D91E26`; olhos ovais grandes com pupila; boca vermelha sorridente.
- **Expressão:** olhos arregalados e sorriso grande. É o "palhaço" do elenco.
- **Dança de chegada:** pula três vezes quicando como uma bola e solta migalhas.
- **Emote característico:** vira de costas e mostra a "etiqueta" do patrocinador.
- **Som:** "boing" fofo ao pular e um "puf" de farinha ao ser eliminado.

### 8.5 Mini-Herói

> *"Minha mãe me inscreveu. Eu vim pra ganhar."*

- **Silhueta:** o **menor** do elenco, com **capa** triangular abrindo atrás e punho erguido.
- **Visual:** macacão turquesa `#19B5A5` com estrela dourada no peito; capa vermelha `#D91E26`; botas vermelhas; máscara preta com olhos brancos; cabelo preto; pele escura `#8D5A3B`.
- **Expressão:** sorriso confiante e sobrancelhas franzidas de determinação.
- **Dança de chegada:** pose de herói com a capa esvoaçando e o punho para o céu.
- **Emote característico:** "voa" no lugar, de braços esticados.
- **Som:** "Tchá-ram!" e o barulho de capa ao vento quando pula.

### 8.6 Customização (futuro)

Os acessórios entram por cima do sprite, numa camada própria, sem mudar a silhueta base: chapéus, óculos e itens de mão. Prêmios cosméticos podem ser desbloqueados por "temporadas" do programa.

---

## 9. Personagens não jogáveis (NPCs)

### 9.1 Waldo Ribalta, o apresentador

> *"Boa noite, auditóóório!"*

O rosto do jogo. É um personagem original, sem referência direta a nenhum apresentador real.

- **Silhueta:** alto (1,5 tile), braços sempre abertos, **microfone gigante** dourado e prateado.
- **Visual:** smoking vermelho `#D91E26` com lapelas douradas; camisa branca; gravata-borboleta dourada; cabelo prateado `#D9DCE3` penteado para trás com topete; **sorriso enorme** com dentes brancos à mostra e um brilho de estrela no canto; sapatos pretos lustrosos.
- **Onde aparece:**
  - No canto inferior esquerdo, em retrato de busto, junto com a **legenda** (seção 16).
  - Em tamanho grande na tela de título e de resultados.
  - Correndo pela frente do palco no início de cada "quadro especial".
- **Expressões (retrato):** sorrindo (padrão), gargalhando, chocado, piscando, decepcionado (rodada fácil demais) e eufórico (Momento Viral).
- **Voz:** não tem dublagem. Ele "fala" com um blablablá sintetizado (sílabas aleatórias com pitch variável), no ritmo do texto da legenda.

### 9.2 Zé Contrarregra

> *"Monta aí, que daqui a pouco entra no ar."*

- **Silhueta:** boné virado para trás com fone de rádio, cinto de ferramentas e chave inglesa na mão.
- **Visual:** camiseta escura `#3A3340` com faixa dourada; boné turquesa; headset aço escuro com microfone de haste; cinto de madeira com ferramentas; calça jeans `#3E5A7A`; botas marrons; pele escura.
- **Onde aparece:** na **fase de montagem**. Ele entra empurrando a caixa com os itens escolhidos e, quando o tempo acaba, aparece correndo e apontando para a placa ON AIR. Também é o ícone do tutorial ("Zé explica").
- **Animações:** empurrar caixa, apontar o relógio, sinal de "joia" e correr para fora de cena.

### 9.3 Jurada Odete

> *"Gongo!"*

- **Silhueta:** sentada atrás da bancada de jurada, com o **gongo dourado** suspenso ao lado e um martelo erguido.
- **Visual:** cabelo grisalho `#B7B0C2` preso em coque; óculos redondos enormes; blusa rosa; colar de pérolas; bancada de madeira com painel vermelho veludo e estrela dourada.
- **Onde aparece:** num canto do cenário, fixa. Quando alguém morre nos primeiros 2 segundos da corrida, ela bate o gongo, a tela treme e aparece "GONGOU!". Ela também segura placas de nota (0 a 10) na tela de resultados.
- **Animações:** parada (olha de um lado para o outro), martelada no gongo e erguer placa de nota.

### 9.4 Plateia

- **Formato:** faixa horizontal de 3 a 6 tiles de largura com cabeças e ombros em fileira, na frente da cortina.
- **Visual:** cinco tipos de torcedor, com camisetas nas cores laranja, turquesa, rosa, dourado e céu; peles e cabelos variados; um segurando cartaz com coração; outro com os dois braços erguidos.
- **Comportamento:**
  - **Calma:** balanço sutil.
  - **Empolgada:** pula, levanta os braços, e os cartazes sobem (Momento Viral, chegada solo).
  - **Vaiando:** braços para baixo e cabeças balançando (rodada fácil demais).
  - **"Ôôôô":** onda de pé correndo da esquerda para a direita (início de quadro especial).
- **Variações de cartaz:** coração, estrela, "10", seta e o rosto de um jogador (no lobby, mostrando a placa de quem está ganhando).

### 9.5 Câmeras e equipe de fundo

Silhuetas escuras sem detalhes nas laterais do palco (cinegrafista, operador de boom e assistente com claquete), desenhadas em `#120D10` com 40% de opacidade. Elas só dão ambiência e não interagem.

---

## 10. Itens: estruturas

Assinatura: madeira com topo creme ou turquesa. Nunca listras.

| Item | Tamanho | Aparência | Comportamento |
|---|---|---|---|
| **Praticável** | 1 × 1 | Caixa de madeira `#C98A4B` com tampa creme, duas tábuas horizontais e pregos nos cantos | Bloco sólido básico |
| **Praticável longo** | 3 × 1 | Igual ao praticável, com emendas verticais a cada tile | Plataforma longa sólida |
| **Palco giratório** | 4 × 1 | Barra turquesa arredondada com eixo dourado no centro e duas setas curvas indicando o giro | Gira 360° em 4s em torno do eixo. Parar em cima exige timing |
| **Escadaria** | 2 × 2 | Três degraus creme com carpete vermelho na quina de cada degrau | Rampa em degraus: sobe sem pular |
| **Trilho de câmera** | 4 × 2 | Trilho de aço com dormentes, carrinho cinza com rodas e uma câmera preta com lente turquesa e luz vermelha de gravação | Plataforma que vai e volta horizontalmente pelo trilho (3 tiles em 2,5s) |
| **Elevador de palco** | 2 × 2 | Plataforma turquesa sobre tesoura de aço, base cinza e seta dupla vertical | Sobe e desce 3 tiles em 3s, parando 0,5s em cada ponta |

**Sinalização de movimento:** tudo que se move mostra **setas pretas** no próprio desenho. Durante a montagem, uma linha pontilhada creme mostra o caminho completo que o item vai fazer.

---

## 11. Itens: perigos letais

Assinatura: listras amarelo e preto. Detalhes de alerta em vermelho.

Todo perigo tem um **aviso visual antes de agir (telegraph)** de pelo menos 0,4s. Ninguém pode morrer sem ter tido a chance de ver o que vinha.

| Item | Tamanho | Aparência | Comportamento | Aviso |
|---|---|---|---|---|
| **Alçapão** | 1 × 1 | Moldura listrada com abertura preta no centro e duas portinholas de madeira | Fica fechado por 2s, abre por 1s e repete. Aberto, mata quem cair | As portinholas tremem 0,4s antes de abrir |
| **Holofote** | 1 × 1 (pendurado) | Barra de aço no teto, suporte listrado, refletor cinza com lente dourada e cone de luz translúcido até o chão | Quando um jogador entra no cone, o holofote despenca em linha reta. Volta a aparecer depois de 3s | O cone pisca em vermelho e o suporte range 0,5s antes da queda |
| **Lança-torta** | 1 × 1 | Caixa listrada com mola e uma torta de chantilly com cereja em cima | Dispara uma torta a cada 2,5s na direção apontada. A torta mata no contato | A mola se comprime 0,4s antes e a cereja balança |
| **Dinamite cenográfica** | 1 × 1 | Três bananas vermelhas com cinta listrada, pavio e faísca dourada | Item de destruição, usado só na montagem. Explode em cruz (estilo Bomberman), alcançando 2 tiles para cada lado e destruindo itens que não sejam palco fixo | Mostra a área de explosão em cruz com listras transparentes durante o posicionamento |

**Animação de morte por perigo:** cada perigo tem um "gag" próprio antes do efeito comum de eliminação. A torta deixa o rosto coberto de chantilly, o holofote deixa o personagem achatado como panqueca, e o alçapão faz o personagem cair com a mão acenando.

---

## 12. Itens: efeitos não letais

Assinatura: rosa-confete, sem listras. Eles atrapalham, mas sozinhos não matam. A graça está na combinação com perigos.

| Item | Tamanho | Aparência | Comportamento |
|---|---|---|---|
| **Canhão de confete** | 1 × 1 | Cano rosa inclinado com anéis creme, roda dourada e confetes coloridos saindo da boca | A cada 3s dispara uma rajada que **empurra** quem estiver em até 3 tiles na direção do cano |
| **Microfone com fio** | 1 × 1 | Pedestal de aço com microfone prateado, faixa rosa e um fio rosa enrolado no chão | Quem toca o fio fica **enroscado por 1s** (não pode pular, anda a 40% da velocidade) |
| **Máquina de espuma** | 1 × 1 | Caixa rosa com grade, bico cinza, bolhas brancas subindo e poça de espuma creme | Cria uma área de 3 tiles de chão **escorregadio** à frente (aceleração e frenagem reduzidas a 25%) |

O aviso é mais leve que o dos perigos: um brilho rosa pulsante 0,3s antes de agir.

---

## 13. Bônus e coletáveis

| Item | Aparência | Comportamento |
|---|---|---|
| **Refri Tchan** | Lata dourada com faixa vermelha, estrela creme, lacre prateado e brilhinhos ao redor. Marca fictícia, sem texto | Aparece no quadro "Merchan do Patrocinador". Vale +1 ponto. Flutua 2px para cima e para baixo em 1,2s |
| **Estrela de audiência** | Estrela dourada com contorno, girando | Pontos extras que voam do jogador até o medidor de audiência ao fim da rodada (só efeito visual) |

---

## 14. Palco e cenário

### 14.1 Peças fixas

| Peça | Tamanho | Aparência | Papel |
|---|---|---|---|
| **Largada** | 2 × 1 | Plinto turquesa com tampa creme e uma grande seta "play" creme | Ponto de partida. Os jogadores surgem aqui, um ao lado do outro |
| **Microfone de Ouro** | 2 × 3 | Pedestal de madeira com tampa creme e estrela dourada; haste dourada; microfone dourado gigante com grade riscada; brilhos ao redor | A chegada. Encostar nele termina a corrida do jogador |
| **Piso do palco** | tile 1 × 1 | Tábuas marrom-escuras `#5A3424` com borda mais clara em cima e juntas desencontradas | Chão e limites do mapa |
| **Cortina** | tile 4 × 4 | Veludo vermelho `#8E1424` com dobras verticais mais claras e uma franja dourada em zigue-zague no topo | Fundo do palco |
| **Telão** | 4 × 3 | Moldura preta com lâmpadas douradas, tela com barras de cor (creme, dourado, turquesa, verde, rosa, vermelho, céu) e uma faixa inferior com "ON AIR" | Decoração de fundo. Durante o jogo pode mostrar o rosto do líder ou "INTERVALO" |

### 14.2 Composição padrão de um palco

De trás para frente:

1. **Cortina** cobrindo todo o fundo, com um **letreiro de lâmpadas** com o nome do programa no topo.
2. **Telão** central e duas **torres de holofotes** decorativas nas laterais (estas não fazem mal a ninguém).
3. **Plateia** numa faixa na parte de baixo da tela, na frente do palco (camada de parallax).
4. **Palco jogável:** piso nas bordas, largada na esquerda, Microfone de Ouro na direita.
5. A **bancada da Jurada Odete** fica num dos cantos superiores, fora da área jogável.

### 14.3 Variações de palco (mapas)

| Palco | Ambiente | Diferença visual | Diferença de jogo |
|---|---|---|---|
| **Estúdio Principal** | O palco padrão descrito acima | — | Mapa plano, bom para aprender |
| **Auditório Lotado** | Arquibancada subindo pelos lados | Plateia nas laterais em degraus | Mapa em formato de "U", com subida |
| **Externa na Praia** | Gravação ao ar livre com tenda e coqueiros cenográficos | Céu dourado de fim de tarde, areia no lugar do piso | Buracos com "água" no chão |
| **Bastidores** | Atrás do palco: cabos, caixas, araras de figurino | Iluminação baixa e tons frios | Muitos andares e passagens estreitas |
| **Especial de Fim de Ano** | Neve de isopor, árvore cenográfica, fitas | Paleta com mais dourado e vermelho | Chão levemente escorregadio |

---

## 15. Fluxo da partida e telas

Todas as telas são desenhadas em **1280 × 720 (16:9)** com área segura de 32px nas bordas e se adaptam até 960 × 540. A interface usa o tema **Estúdio** dentro do jogo.

### 15.1 Tela de título

- **Fundo:** cortina fechada ocupando a tela, iluminada por dois holofotes que cruzam lentamente.
- **Centro:** a placa ON AIR, inicialmente **apagada**. Ao apertar qualquer tecla ela acende com o efeito de piscar e a cortina abre.
- **Rodapé:** "APERTE QUALQUER TECLA" em `rotulo`, piscando a cada 1s, e a versão do jogo em `pequeno`, `texto-suave`.

### 15.2 Menu principal

- **Layout:** à esquerda, a placa ON AIR menor e uma coluna de botões; à direita, Waldo Ribalta em tamanho grande, acenando, na frente do telão.
- **Botões, em ordem:**
  1. **JOGAR ONLINE** (primário, vermelho)
  2. **CRIAR SALA**
  3. **ENTRAR COM CÓDIGO**
  4. **JOGO LOCAL**
  5. **OPÇÕES**
  6. **CRÉDITOS** (botão fantasma)
- **Detalhe:** ao passar o mouse ou o foco sobre um botão, Waldo muda de expressão e a legenda dele comenta a opção ("Jogar com desconhecidos? Que coragem!").

### 15.3 Criar sala / entrar com código

- **Criar sala:** um painel com o **código da sala** em `placar` (4 letras, sem letras ambíguas como O/0 ou I/1), botão **COPIAR** com ícone e um botão para copiar o link direto. Abaixo, as opções da sala: número de rodadas, pontos para vencer, sala pública ou privada e quadros especiais ligados ou desligados.
- **Entrar com código:** quatro caixas de caractere grandes no estilo de "fichas" de programa de TV, que avançam sozinhas ao digitar. Erro: as caixas tremem e ficam com borda vermelha acesa, com a mensagem "Essa sala não existe (ou o programa já acabou)".

### 15.4 Lobby (a sala de espera)

- **Cenário:** os bastidores, com o espelho de camarim cheio de lâmpadas ao fundo.
- **Quatro cadeiras de camarim**, uma por jogador. Cada uma mostra:
  - o personagem escolhido parado (ou uma silhueta com "?" se a cadeira está vazia);
  - a placa de nome com a cor e a forma do jogador;
  - o estado: "PRONTO" em turquesa ou "AGUARDANDO…" em texto-suave.
- **Topo:** código da sala grande, com o botão de copiar.
- **Rodapé:** botão **PRONTO** (vira **CANCELAR** depois de apertado) e, para o dono da sala, **COMEÇAR O PROGRAMA** (só fica ativo com todos prontos).
- **Lateral:** um chat simples, com mensagens em `corpo`, nomes na cor de cada jogador e emotes rápidos.

### 15.5 Seleção de personagem

- Uma fileira de **cartões de personagem** (estilo "ficha de inscrição" do programa): fundo creme, foto do personagem, nome em `titulo-secao`, frase de efeito em `pequeno`.
- **Cartão em foco:** sobe 8px, ganha `sombra-pop` maior e uma moldura na cor do jogador. O personagem faz o emote característico.
- **Cartão escolhido por outro:** mostra uma pequena placa com a forma e a cor desse jogador no canto. A escolha continua liberada, porque personagens repetidos são permitidos.

### 15.6 Roleta de Prêmios (escolha de item)

- **Transição:** o apresentador grita "Roda a roleta!" e uma roleta gigante gira no centro do palco.
- **Resultado:** a roleta para e abre uma "vitrine" com **N + 1 cartões de item** (N = número de jogadores), lado a lado.
- **Cartão de item:** fundo creme, item centralizado, nome em `botao` e uma faixa de categoria colorida embaixo: listrada (perigo), rosa (efeito) ou madeira/turquesa (estrutura).
- **Ordem de escolha:** quem está em último no placar escolhe primeiro. Uma faixa no topo mostra a fila com as formas e cores dos jogadores.
- **Escolha:** o cursor do jogador (a mãozinha com a forma dele) passa sobre os cartões. Ao escolher, o cartão voa até a placa de nome do jogador e fica "carimbado" com a forma e a cor dele.
- **Tempo:** 10s por jogador, com uma barra encolhendo. Ao fim, é feita uma escolha aleatória.

### 15.7 Montagem do Cenário

- **Clima:** a plateia escurece, uma luz de trabalho branca acende e o Zé Contrarregra entra empurrando os itens.
- **Grid visível:** linhas pontilhadas creme a 15% de opacidade sobre o palco.
- **Cursor de construção:**
  - o item fantasma a 70% de opacidade, preso ao grid;
  - uma moldura na cor do jogador com a forma dele no canto;
  - **válido:** moldura céu com ✓;
  - **inválido:** moldura vermelha acesa com ✕ e tremida;
  - itens móveis mostram o caminho pontilhado;
  - a dinamite mostra a área de explosão em cruz.
- **Controles na tela:** dicas de botão no rodapé ("[R] GIRAR · [CLIQUE] COLOCAR").
- **Tempo:** 20s. Quem coloca primeiro fica com um selo "PRONTO" na placa de nome.
- **Fim:** o Zé aponta para a placa, que pisca e acende.

### 15.8 No Ar! (a corrida)

- **Abertura:**
  1. a tela escurece 30%;
  2. contagem "3, 2, 1" em `contagem`, cada número batendo como um carimbo;
  3. **"NO AR!"** / **"ON AIR!"** em vermelho, enquanto a placa ON AIR do HUD acende e a plateia grita.
- **Durante:** HUD mínimo (seção 16). A câmera enquadra todos os jogadores vivos com uma margem de 3 tiles e dá zoom suave.
- **Jogador eliminado:** vira espectador e assiste com a câmera geral. A placa de nome dele fica cinza com um ícone de gongo.
- **Fim:** quando todos chegam, morrem ou o tempo de 60s acaba.

### 15.9 Resultado da rodada: o Medidor de Audiência

- **Tela:** o palco desfocado ao fundo, com um painel de resultados no centro.
- **Uma barra por jogador**, na cor dele, crescendo da esquerda para a direita. Os pontos ganhos entram como **segmentos** com rótulo:
  - **CHEGOU** (+2)
  - **EXCLUSIVA!** (+1 extra se só ele chegou)
  - **MOMENTO VIRAL!** (+1 por rival eliminado pela armadilha dele)
  - **PRIMEIRO A CHEGAR** (+1)
  - **MERCHAN** (+1 por produto coletado)
- **Ordem da animação:** os segmentos entram um de cada vez, com 0,3s entre eles, e um "tchan" sonoro cada.
- **Rodada fácil demais:** em vez das barras, a placa ON AIR apaga, entra a faixa **INTERVALO**, o apresentador aparece decepcionado e a legenda diz "A audiência despencou! Ninguém pontua."
- **Ninguém chegou:** a plateia boceja e o texto é "Programa sem vencedor!".
- **Linha de chegada:** uma linha vertical dourada marca a pontuação necessária para vencer, com um troféu na ponta.

### 15.10 Quadros especiais

A cada 3 rodadas (se ligados), o apresentador anuncia um quadro. A tela mostra um **cartão de quadro** girando até ficar de frente: fundo na cor do quadro, ícone grande, nome em `titulo-secao` e uma linha explicando a regra.

| Quadro | Cor do cartão | Ícone | Regra | Efeito visual na rodada |
|---|---|---|---|---|
| **Rodada Premiada** | Dourado | Estrela | Pontos em dobro | Confete dourado caindo e moldura de lâmpadas piscando na tela |
| **Apagão no Estúdio** | Tinta (preto) | Lâmpada apagada | Tudo escuro, só um holofote segue cada jogador | A tela fica a 8% de brilho, com círculos de luz de 4 tiles de raio |
| **Merchan do Patrocinador** | Vermelho | Lata | Latas de Refri Tchan espalhadas valem pontos | Banners do patrocinador fictício nas laterais |
| **Câmera Lenta** | Céu | Relógio | Tudo a 50% da velocidade | Filtro de scanlines e um "REC" piscando no canto |
| **Plateia Participa** | Rosa | Mão | A plateia joga objetos inofensivos no palco | Cartazes e chinelos de espuma caindo |

### 15.11 Fim de partida e VT dos Melhores Momentos

- **Pódio:** os três primeiros sobem num pódio dourado, prateado e de madeira, com uma chuva de confete. O vencedor segura o Microfone de Ouro e faz a dança de vitória.
- **VT dos Melhores Momentos:** uma sequência de replays curtos (3 a 5 clipes de 3s) com as mortes mais absurdas da partida.
  - **Moldura de TV de tubo:** cantos arredondados, scanlines, leve aberração cromática e "VT" piscando no canto superior.
  - **Legenda por clipe:** "Momento viral: J3 derrubou J1 com uma torta."
  - O jogador pode pular com qualquer tecla.
- **Botões finais:** **REVANCHE** (primário), **TROCAR PERSONAGEM** e **SAIR DO PROGRAMA**.

### 15.12 Menu de pausa

- **Apresentação:** fundo escurecido a 70% e a faixa **"VOLTAMOS JÁ"** no estilo de cartão de intervalo, com barras de cor no topo.
- **Opções:** **CONTINUAR**, **OPÇÕES**, **COMO JOGAR** e **SAIR DO PROGRAMA** (pede confirmação).
- **Online:** o jogo não pausa de verdade, e a faixa diz "O programa continua no ar…" para lembrar que a partida segue.

### 15.13 Opções

Organizadas em abas: **SOM**, **VÍDEO**, **CONTROLES** e **ACESSIBILIDADE**.

- **Som:** sliders de música, efeitos, plateia e voz do apresentador.
- **Vídeo:** filtro de TV de tubo (liga/desliga), tremida de tela (0–100%) e escala da interface (90%, 100%, 125%).
- **Controles:** remapeamento com ícones de teclado e controle.
- **Acessibilidade:** ver seção 22.

### 15.14 Tela de carregamento e conexão

- **Carregando:** o telão com barras de cor e a frase "ENTRANDO NO AR…" em `rotulo`, com uma barra de progresso dourada.
- **Reconectando:** o sinal "chuviscado" (estática animada) com "SINAL FRACO, RECONECTANDO…".
- **Desconectado:** a placa apagada e "SAÍMOS DO AR", com o botão **VOLTAR AO MENU**.

---

## 16. HUD durante o jogo

Princípio: **o HUD sai da frente durante a corrida.** Tudo fica nas bordas, com no máximo 15% da tela ocupada.

| Elemento | Posição | Descrição |
|---|---|---|
| **Placa ON AIR** | Topo, centro | Versão pequena (120px de largura) da placa. Acesa durante a corrida, apagada na montagem |
| **Cronômetro** | Topo, à direita da placa | Segundos restantes em `placar`, dentro de uma pílula escura. Nos últimos 10s fica vermelho e pulsa |
| **Rodada** | Topo, à esquerda da placa | "RODADA 4/12" em `rotulo` |
| **Fase** | Topo, abaixo da placa | Faixa de fase: "ROLETA", "MONTAGEM" ou "NO AR", entra deslizando e some depois de 2s |
| **Placas de jogador** | Rodapé, em linha | Uma por jogador: forma colorida, nome, pontuação e estado (vivo, chegou ✓, eliminado com gongo) |
| **Placa de nome no mundo** | Acima da cabeça de cada personagem | Pílula na cor do jogador com a forma e o nome em `nome-jogador`. Some durante a corrida para quem estiver a mais de 8 tiles da câmera |
| **Legenda do apresentador** | Canto inferior esquerdo | Retrato de busto do Waldo e balão creme com o texto em `legenda`, digitado letra a letra. Dura 3s e nunca cobre o centro da tela |
| **Alerta de evento** | Centro, terço superior | Bordões grandes ("CAIU, PERDEU!", "MOMENTO VIRAL!") em `titulo-secao`, com contorno grosso, entrando com escala de 0 a 110% a 100% em 0,25s |
| **Indicador fora de tela** | Bordas | Quando um jogador sai do enquadramento, uma seta na cor dele aparece na borda apontando para onde ele está |

---

## 17. Componentes de interface

Todos os componentes têm **contorno de 3px em `#1B1418`**, sombra dura e cantos arredondados. A interface parece feita de recortes de cartolina.

### 17.1 Botões

| Variante | Fundo | Texto | Uso |
|---|---|---|---|
| **Primário** | `no-ar` `#D91E26` | `sobre-no-ar` | A ação principal da tela. **Só um por tela** |
| **Secundário** | `fundo-elevado` | `texto` | Demais ações |
| **Destaque** | `holofote` | `sobre-holofote` | Ações de celebração (REVANCHE, COPIAR CÓDIGO) |
| **Fantasma** | transparente, contorno `linha-forte` | `texto` | Ações de baixa importância (CRÉDITOS, VOLTAR) |
| **Perigoso** | `fundo-elevado` com listras finas na borda esquerda | `texto` | Ações destrutivas (SAIR DO PROGRAMA, EXPULSAR) |

**Anatomia:** altura de 52px (40px no tamanho pequeno), padding horizontal de 24px, texto `botao`, ícone opcional à esquerda com 8px de espaço, raio `raio-md` e `sombra-pop`.

**Estados:**
- **Hover:** sobe 2px e a sombra cresce para 6px.
- **Pressionado:** desce 3px e a sombra cai para 1px.
- **Foco:** anel `foco` de 3px com 3px de afastamento.
- **Desabilitado:** 40% de opacidade, sem sombra.
- **Carregando:** o texto vira três lâmpadas piscando em sequência.

### 17.2 Campos

- **Campo de texto:** fundo `fundo-poco`, contorno 3px `linha-forte`, altura de 48px, texto `corpo`. No foco, o contorno fica `foco`.
- **Campo de código:** 4 caixas de 64 × 72px com uma letra em `placar` cada, avançando automaticamente.
- **Erro:** contorno vermelho aceso, tremida de 4px (3 ciclos em 0,3s) e mensagem em `pequeno` abaixo, sempre com ícone ✕.

### 17.3 Controles de opção

- **Toggle:** pílula de 56 × 32px. Desligado: fundo `fundo-poco` com bolinha `texto-suave` à esquerda. Ligado: fundo `turquesa` com bolinha creme à direita e um ✓ dentro.
- **Slider:** trilha de 8px em `fundo-poco`, parte preenchida em `holofote` e puxador circular de 24px creme com contorno. O valor aparece em `rotulo` à direita.
- **Seletor de opções:** setas ‹ › nas laterais e o valor no centro em `botao` ("12 RODADAS"). Funciona bem com controle.
- **Abas:** texto `botao`. A aba ativa tem fundo `fundo-elevado` e um sublinhado de 4px em `no-ar`.

### 17.4 Cartões

- **Cartão de personagem:** 200 × 280px, fundo creme mesmo no tema escuro (é uma "ficha"), personagem centralizado sobre um círculo turquesa, nome, frase e `raio-lg`.
- **Cartão de item:** 140 × 160px, item centralizado, nome e faixa de categoria de 12px embaixo.
- **Cartão de quadro especial:** 480 × 300px, cor do quadro, ícone de 96px e textos centralizados.
- **Painel:** fundo `fundo-elevado`, contorno 3px, `raio-lg`, padding `espaco-6` e título em `titulo-secao`.

### 17.5 Placas e selos

- **Placa de nome:** pílula de altura 28px na cor do jogador, com a forma em tinta à esquerda e o nome em `nome-jogador`.
- **Selo de pontuação:** círculo dourado de 36px com "+N" em `placar` reduzido e estrela atrás.
- **Selo de estado:** chips pequenos ("PRONTO", "DONO DA SALA", "ESPECTADOR") com fundo da cor do estado e `rotulo`.

### 17.6 Mensagens

- **Toast:** faixa no topo da tela, fundo `fundo-elevado`, ícone à esquerda e texto em `corpo`. Fica 3s e sai deslizando para cima. Ex.: "J2 entrou na sala".
- **Modal de confirmação:** painel centralizado com título, uma frase e dois botões (o destrutivo à esquerda, como fantasma, e o seguro à direita, como primário). Ex.: "Sair do programa? Sua vaga na plateia será liberada."

### 17.7 Legenda do apresentador (componente)

- **Retrato:** busto do Waldo num círculo de 96px com moldura dourada e lâmpadas.
- **Balão:** fundo creme, contorno 3px, cauda apontando para o retrato e texto `legenda` em tinta.
- **Animação:** o texto aparece letra a letra (35ms por caractere) junto com o blablablá. Um clique ou tecla completa o texto na hora.
- **Limite:** no máximo 2 linhas e 70 caracteres.

---

## 18. Ícones

- **Grade:** 24 × 24px, com área útil de 20px.
- **Traço:** 2,25px, pontas e junções arredondadas, sem preenchimento (exceto o "jogar", que pode ser preenchido no botão primário).
- **Cor:** desenhados em tinta e aplicados como máscara CSS (`mask-image`), herdando a cor do texto ao lado.
- **Tamanhos de uso:** 20px dentro de botões, 24px em listas e 32px no HUD.

| Ícone | Uso |
|---|---|
| `jogar` | Jogar, continuar, começar |
| `pausa` | Pausar |
| `config` | Opções |
| `jogadores` | Sala, lista de jogadores |
| `microfone` | Voz do apresentador, chat de voz (futuro) |
| `trofeu` | Vitória, pódio, pontos para vencer |
| `coroa` | Líder do placar, dono da sala |
| `tempo` | Cronômetro, tempo de montagem |
| `som` | Volume |
| `controle` | Configuração de controle, jogo local |
| `copiar` | Copiar código ou link da sala |
| `sair` | Sair do programa |
| `check` | Confirmar, pronto, posição válida |
| `fechar` | Fechar, cancelar, posição inválida |
| `estrela` | Pontos, quadro Rodada Premiada |
| `gongo` | Jogador eliminado |

Ícones novos seguem a mesma grade e o mesmo traço, e devem ser testados a 20px.

---

## 19. Movimento, animação e feedback

### 19.1 Princípios

- **Tudo tem "pop":** entradas com leve passagem do ponto (escala de 0 a 110% e então 100%) e saídas rápidas.
- **Comédia física:** achatar e esticar (squash and stretch) em pulos e pousos, sempre com no máximo 15% de deformação.
- **Rapidez:** nenhuma transição de interface passa de 0,4s. O jogador nunca espera por uma animação para jogar.

### 19.2 Durações e curvas

| Token | Duração | Curva | Uso |
|---|---|---|---|
| `rapido` | 120ms | ease-out | Hover, pressionar botão |
| `padrao` | 220ms | ease-out | Abrir painel, trocar aba |
| `pop` | 250ms | `cubic-bezier(.34,1.56,.64,1)` (passa do ponto) | Alertas de evento, cartões entrando |
| `cena` | 400ms | ease-in-out | Trocar de tela, abrir a cortina |

### 19.3 Eliminação (a "morte")

Os personagens nunca se machucam. A eliminação é um gag de bastidor:

1. **Congelamento (hitstop):** 80ms.
2. O personagem vira um **recorte de papelão** plano (perde o contorno interno e ganha uma borda branca grossa).
3. O recorte **gira para trás** como uma placa caindo, em 0,3s.
4. Ele some num **puf de confete** nas cores do jogador.
5. Em seguida o alerta "CAIU, PERDEU!" entra, e a plateia reage com um "Ohhh!".

### 19.4 Feedback de tela

| Evento | Tremida de tela | Outros |
|---|---|---|
| Pouso de pulo alto | — | Poeira em duas nuvenzinhas creme |
| Eliminação | 4px, 0,15s | Hitstop de 80ms |
| Holofote caindo | 8px, 0,25s | Faíscas douradas |
| Dinamite | 12px, 0,4s | Clarão branco de 2 quadros e fumaça cinza em cruz |
| Gongo da Jurada | 6px, 0,3s | Ondas sonoras desenhadas saindo do gongo |
| Chegada ao Microfone de Ouro | — | Raios de luz dourados e confete |

A tremida respeita o ajuste de acessibilidade e pode ser desligada.

### 19.5 Partículas

| Partícula | Forma | Cores |
|---|---|---|
| Confete | Retângulos de 4 × 6px girando | Laranja, céu, rosa, lima, dourado |
| Espuma | Círculos brancos com contorno fino | Branco e creme |
| Migalhas (Pãozinho) | Pontos irregulares | Massa e casquinha |
| Faíscas | Estrelas de 4 pontas | Dourado e creme |
| Fumaça | Círculos sobrepostos | `#9AA1B3` a 60% |

---

## 20. Som

O som carrega metade do humor do jogo. A paleta é a de um programa de TV de domingo.

### 20.1 Música

| Momento | Estilo |
|---|---|
| Menu e título | Vinheta de abertura de programa: metais, bateria animada e palmas no tempo |
| Lobby | Versão "bastidor" da vinheta: baixo e teclado, mais calma |
| Roleta | Rufar de tambores crescendo até o resultado |
| Montagem | Loop leve de "música de espera" com teclado e marimba |
| Corrida | Versão acelerada da vinheta, com metais intensos |
| Últimos 10 segundos | A mesma faixa com o andamento 10% mais rápido e um tique-taque por cima |
| Resultados | Fanfarra curta |
| Intervalo | Jingle de comercial falso, 5 segundos |

### 20.2 Efeitos

| Evento | Som |
|---|---|
| Placa ON AIR acendendo | Zumbido elétrico + "clunk" de interruptor |
| Pulo | "Fiu" curto, com uma variação por personagem |
| Eliminação | "Tóim" de mola + "Ohhh!" da plateia |
| Chegada | "Tchan!" + aplausos |
| Gongo | Gongo grave e longo |
| Rodada fácil | Vaia + "fiu-fiu" de trombone descendo |
| Momento Viral | Plateia gritando + buzina |
| Pontos no medidor | "Plim" subindo de tom a cada segmento |
| Botão (hover / clique) | Clique de interruptor de estúdio / "ploc" |
| Erro | Buzina curta "fom-fom" |

### 20.3 Voz

- **Waldo Ribalta:** blablablá sintetizado com 3 timbres (normal, empolgado, decepcionado).
- **Personagens:** apenas interjeições curtas e não verbais, que funcionam em qualquer idioma.
- **Plateia:** risadas enlatadas, "ôôôô", aplausos, vaias e "uhuul".

---

## 21. Voz, textos e bordões

### 21.1 Tom

O jogo fala como um **apresentador exagerado e brincalhão**, nunca como um sistema. Os textos são curtos, animados e um pouco debochados, sem ofender ninguém.

| Em vez de | Escreva |
|---|---|
| "Conexão perdida." | "Saímos do ar! Tentando voltar…" |
| "Aguardando jogadores." | "Esperando o resto do elenco…" |
| "Partida encerrada." | "E o programa de hoje termina aqui!" |
| "Você morreu." | "Caiu, perdeu!" |
| "Código inválido." | "Essa sala não existe (ou o programa já acabou)." |
| "Pausado." | "Voltamos já!" |

### 21.2 Regras de escrita

- **Botões e rótulos:** caixa alta, verbo primeiro e no máximo 3 palavras ("CRIAR SALA", "COPIAR CÓDIGO").
- **Frases do apresentador:** caixa normal, no máximo 70 caracteres, com exclamação à vontade.
- **Descrições e opções:** caixa normal e frases curtas e diretas, sem piada.
- **Tratamento:** "você" no texto do sistema; o apresentador fala com a plateia ("Olha só o que esse participante aprontou!").
- **Sem emoji** em textos do jogo. Os ícones fazem esse papel.
- **Localização:** todo texto fica em arquivos de tradução (PT e EN desde o início). Dê 30% de folga de largura nos componentes, porque o português costuma ser mais longo.

### 21.3 Frases do apresentador (exemplos)

**Entrada da rodada:** "Mais uma rodada, meu povo!" · "Roda a roleta!" · "Vamos ver o que a produção preparou!"

**Montagem:** "Monta direitinho, hein!" · "Dez segundos, contrarregras!"

**Corrida:** "Tá no ar!" · "Olha o tombo!" · "Quase, quase!"

**Resultados:** "A audiência despencou!" · "Exclusiva! Só um chegou!" · "Isso vai viralizar!" · "Programa sem vencedor! Que vergonha!"

**Provocações (quem está em último):** "O J3 tá precisando de uma ajudinha da plateia!" · "Ainda dá tempo de virar, viu?"

---

## 22. Acessibilidade

- **Daltonismo:** cor de jogador sempre acompanhada de forma; perigos com padrão listrado (não só cor); estados com ícone e texto.
- **Contraste:** texto sempre com no mínimo 4,5:1; contornos e ícones com 3:1. A tabela da seção 3 já respeita isso.
- **Movimento:** opção de reduzir a tremida de tela (0–100%), desligar o filtro de TV de tubo e desligar flashes (o clarão da dinamite vira um escurecimento rápido).
- **Leitura:** escala de interface até 125% e velocidade da legenda do apresentador ajustável (ou exibição instantânea).
- **Áudio:** legendas para os sons importantes ("[GONGO]", "[PLATEIA VAIANDO]") e indicadores visuais na tela para todos os avisos sonoros dos perigos.
- **Controles:** remapeamento completo, suporte a controle e teclado, e todos os menus navegáveis sem mouse, com o anel de foco sempre visível.
- **Daltonismo extra:** opção que troca as listras de perigo por um padrão xadrez preto e branco de alto contraste.

---

## 23. Especificações técnicas para web

### 23.1 Resolução e escala

- **Resolução de referência:** 1280 × 720, escalada para ocupar a janela mantendo 16:9, com barras pretas quando necessário.
- **Arte:** desenhada a 2× (64px por tile) e reduzida pelo motor. Exporte também em 1× para máquinas fracas.
- **Escala mínima suportada:** 960 × 540.

### 23.2 Formatos

| Tipo | Formato de trabalho | Formato no jogo |
|---|---|---|
| Sprites estáticos | SVG | PNG em atlas (texture atlas), 2× e 1× |
| Animações | SVG por quadro ou arquivo do Aseprite | Folha de sprites em PNG + JSON do atlas |
| Ícones de interface | SVG | SVG (aplicados como máscara CSS) ou atlas PNG |
| Logo | SVG | SVG no site, PNG no jogo |
| Fontes | woff2 | woff2, carregadas antes da tela de título |
| Música e efeitos | WAV | OGG (com MP3 de reserva para o Safari) |

### 23.3 Desempenho

- **Atlas:** no máximo 2048 × 2048 por folha. Um atlas para personagens, um para itens e cenário e um para a interface.
- **Peso total do primeiro carregamento:** meta de até 8 MB, com a música carregada depois do menu.
- **Partículas:** limite de 200 na tela ao mesmo tempo. Em máquinas fracas, o limite cai para 80 automaticamente.
- **Filtro de TV de tubo:** feito em shader, desligado por padrão em dispositivos com GPU fraca.

### 23.4 Cores no código

As cores e medidas desta documentação devem existir como constantes em um único arquivo (por exemplo `tokens.ts` ou `tokens.json`), usado tanto pelo jogo quanto pelo site. Nenhum hex fica solto no código.

---

## 24. Nomenclatura e organização de arquivos

- **Nomes:** minúsculas, palavras separadas por hífen e sem acentos (`tia-da-excursao`, `canhao-de-confete`).
- **Animações:** `<personagem>_<animacao>_<quadro>.png` (ex.: `calouro_correndo_03.png`).
- **Variações:** sufixo depois do nome (`logo-on-air_apagada.svg`, `cursor_invalido.svg`).

```
assets/
├── logos/          logo-on-air, logo-no-ar, app-icon
├── personagens/    tia-da-excursao, calouro, vovo-da-plateia, mascote-paozinho, mini-heroi
├── npcs/           apresentador-waldo-ribalta, contrarregra-ze, jurada-odete, plateia
├── estruturas/     praticavel, praticavel-longo, palco-giratorio, escadaria, trilho-camera, elevador-de-palco
├── perigos/        alcapao, holofote, lanca-torta, dinamite-cenografica
├── efeitos/        canhao-de-confete, microfone-com-fio, maquina-de-espuma
├── bonus/          refri-tchan, estrela-audiencia
├── palco/          largada, microfone-de-ouro, piso-do-palco, cortina, telao
├── interface/      icone-*.svg, cursores, molduras
├── particulas/     confete, espuma, migalhas, faisca, fumaca
├── fontes/         Bungee, Barlow, Barlow Condensed (woff2)
└── audio/
    ├── musica/
    ├── efeitos/
    └── vozes/
```

---

## 25. Checklist de um asset novo

Antes de colocar qualquer arte nova no jogo:

- [ ] Usa só cores da paleta de sprites (seção 3.2)?
- [ ] Tem contorno de 3px em `#1B1418` e cores chapadas, sem degradê?
- [ ] Respeita o código de categorias: listras só em perigos, rosa só em efeitos, nada de listras em estruturas?
- [ ] A silhueta é reconhecível reduzida a 32px?
- [ ] Ocupa um número inteiro de tiles e encaixa no grid?
- [ ] Se é perigo, tem aviso visual de pelo menos 0,4s antes de agir?
- [ ] Se se move, mostra setas no desenho e o caminho pontilhado na montagem?
- [ ] Está livre de texto embutido e de referências a marcas, programas ou pessoas reais?
- [ ] Segue a nomenclatura de arquivos?
- [ ] Passou no teste dos três segundos (seção 7)?
