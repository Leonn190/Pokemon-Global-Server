import pygame, random, time

from pygame.math import Vector2

from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Prefabs.BotoesPrefab import Botao_Selecao
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda
from Codigo.Prefabs.Animações import Animação
from Codigo.Prefabs.Sonoridade import Musica, AtualizarMusica
from Codigo.Geradores.GeradorPokemon import GerarMatilha, CarregarAnimacaoPokemon
from Codigo.Geradores.GeradorMapa import CameraBatalha

Cores = None
Fontes = None
Texturas = None
Fundos = None
Outros = None
Pokemons = None
Estruturas = None
Equipaveis = None
Consumiveis = None
Animaçoes = None
Icones = None
Particulas = None

Player = None
camera = None

# estado simples para manter slots e animações (sem guardar em parametros)
_slots_esquerda = None
_slots_direita  = None
_anim_inimigos  = None
_anim_aliados   = None

EstadoArenaBotoes = {}

# ================= FUNÇÕES AUX =================
# cache para skins de botão redimensionadas por zoom
__slot_skin_size = None           # (w_screen, h_screen)
__slot_skin_aliado = None         # pygame.Surface
__slot_skin_inimigo = None        # pygame.Surface

def _prepare_slot_skins(tela, cam):
    """Cria/atualiza as skins redimensionadas para o tamanho de tela atual."""
    global __slot_skin_size, __slot_skin_aliado, __slot_skin_inimigo
    if not _slots_esquerda:  # ainda não temos slots
        return

    # tamanho do slot em TELA = tamanho do mundo * zoom
    tile_w_world = _slots_esquerda[0].w
    tile_h_world = _slots_esquerda[0].h
    w_screen = max(1, int(round(tile_w_world * cam.Zoom)))
    h_screen = max(1, int(round(tile_h_world * cam.Zoom)))
    new_size = (w_screen, h_screen)

    if __slot_skin_size != new_size:
        # pegue as fontes e garanta formato rápido p/ blit
        srcA = Fundos["FundoPokemonAliado"]
        srcI = Fundos["FundoPokemonInimigo"]
        # convert_alpha usa o formato do display -> blits mais rápidos
        if hasattr(srcA, "convert_alpha"): srcA = srcA.convert_alpha()
        if hasattr(srcI, "convert_alpha"): srcI = srcI.convert_alpha()
        # use scale (mais leve que smoothscale em tempo real)
        __slot_skin_aliado  = pygame.transform.scale(srcA, new_size)
        __slot_skin_inimigo = pygame.transform.scale(srcI, new_size)
        __slot_skin_size = new_size

def _world_rect_to_screen_rect(rect_world, cam):
    tl = cam.TelaAPartirDoMundo((rect_world.x, rect_world.y))
    w  = int(round(rect_world.w * cam.Zoom))
    h  = int(round(rect_world.h * cam.Zoom))
    return pygame.Rect(int(tl.x), int(tl.y), max(1, w), max(1, h))

def _build_world_slots_once(sw, sh, cam, margem, gap, tile_screen):
    """
    Centraliza um grid 3x3 em cada metade do MUNDO (fundo):
      - ESQUERDA  => aliados (AZUL)
      - DIREITA   => inimigos (VERMELHO)
    Tamanho do tile e gap são em PIXELS DO MUNDO (zoom=1).
    """
    # Agora o tamanho é fixo no MUNDO; o zoom só escala na tela:
    tile_world = int(round(tile_screen))
    gap_world  = int(round(gap))

    painel_w_world = tile_world * 3 + gap_world * 2
    painel_h_world = tile_world * 3 + gap_world * 2

    # centros das metades do MUNDO (imagem de fundo)
    cx_esq = cam.BgW * 0.25   # metade esquerda, centro horizontal
    cx_dir = cam.BgW * 0.75   # metade direita, centro horizontal
    cy     = cam.BgH * 0.50   # centro vertical do mundo

    # origens (top-left) em MUNDO para cada painel
    origem_esq_world = Vector2(cx_esq - painel_w_world/2.0, cy - painel_h_world/2.0)
    origem_dir_world = Vector2(cx_dir - painel_w_world/2.0, cy - painel_h_world/2.0)

    slots_esq, slots_dir = [], []
    for r in range(3):
        for c in range(3):
            xw = int(origem_esq_world.x + c * (tile_world + gap_world))
            yw = int(origem_esq_world.y + r * (tile_world + gap_world))
            slots_esq.append(pygame.Rect(xw, yw, tile_world, tile_world))

            xw2 = int(origem_dir_world.x + c * (tile_world + gap_world))
            yw2 = int(origem_dir_world.y + r * (tile_world + gap_world))
            slots_dir.append(pygame.Rect(xw2, yw2, tile_world, tile_world))

    return slots_esq, slots_dir

# ================= TELA FUNDO BATALHA =================
def TelaFundoBatalha(tela, estados, eventos, parametros):
    global camera, _slots_esquerda, _slots_direita, _anim_inimigos, _anim_aliados
    global __dbg_count
    try:
        __dbg_count += 1
    except NameError:
        __dbg_count = 1

    # ---- fundo + câmera ----
    fundo = Fundos["FundoBatalha"]          # imagem 1920x1080 (mundo)
    if camera is None:
        camera = CameraBatalha(fundo, tela.get_size())

    camera.Atualizar(eventos)

    t0 = time.perf_counter()
    camera.Desenhar(tela)  # SUSPEITO #1: draw do fundo (escala/crop)
    t1 = time.perf_counter()

    # ---- layout ACOPLADO AO FUNDO (em MUNDO) ----
    sw, sh = tela.get_size()

    # EDITÁVEIS:
    margem = 18                   # hoje não afeta o centro (mantido p/ compat)
    gap    = 12                   # GAP entre slots, em PX DO MUNDO (zoom=1)
    tile_screen = 160             # TAMANHO DO SLOT em PX DO MUNDO (zoom=1)

    # Constrói UMA VEZ, ancorando no mundo (não reconstrói em zoom/pan)
    if _slots_esquerda is None or _slots_direita is None:
        _slots_esquerda, _slots_direita = _build_world_slots_once(
            sw, sh, camera, margem, gap, tile_screen
        )

    # ---- animações (uma vez, guardando centros em MUNDO) ----
    if _anim_inimigos is None or _anim_aliados is None:
        _anim_inimigos = []
        _anim_aliados  = []

        equipe_inimiga = parametros["EquipeInimiga"]
        equipe_aliada  = parametros["EquipeAliada"]

        inimigos_validos = [p for p in equipe_inimiga if p]
        aliados_validos  = [p for p in equipe_aliada  if p]

        inimigos_escolhidos = (random.sample(inimigos_validos, 3)
                               if len(inimigos_validos) > 3 else inimigos_validos)
        aliados_escolhidos  = (random.sample(aliados_validos, 3)
                               if len(aliados_validos)  > 3 else aliados_validos)

        idxs_centrais = [1, 4, 7]  # coluna central do 3x3

        # DIREITA = INIMIGOS (vermelho)
        for pkm, idx in zip(inimigos_escolhidos, idxs_centrais):
            nome = pkm["Nome"]
            cx, cy = _slots_direita[idx].center   # <- direita
            anim = Animação(Animaçoes.get(nome, CarregarAnimacaoPokemon(nome, Animaçoes)), (cx, cy), tamanho=1.15, intervalo=30)
            _anim_inimigos.append((anim, (cx, cy)))

        # ESQUERDA = ALIADOS (azul)
        for pkm, idx in zip(aliados_escolhidos, idxs_centrais):
            nome = pkm["Nome"]
            cx, cy = _slots_esquerda[idx].center  # <- esquerda
            anim = Animação(Animaçoes.get(nome, CarregarAnimacaoPokemon(nome, Animaçoes)), (cx, cy), tamanho=1.15, intervalo=30, inverted=True)
            _anim_aliados.append((anim, (cx, cy)))

        # ---- botões (HUD acoplado ao mundo) ----
    fonte = Fontes[16]

    # prepara as skins redimensionadas para o zoom atual (uma vez)
    _prepare_slot_skins(tela, camera)
    screen_rect = pygame.Rect(0, 0, sw, sh)

    # ESQUERDA = aliados (AZUL / usa skin já no tamanho certo)
    for rect_world in _slots_esquerda:
        rect_screen = _world_rect_to_screen_rect(rect_world, camera)
        if not rect_screen.colliderect(screen_rect):
            continue
        Botao_Selecao(
            tela, "", rect_screen, fonte,
            __slot_skin_aliado, (0, 0, 0),
            eventos=eventos, estado_global=EstadoArenaBotoes
        )

    # DIREITA = inimigos (VERMELHO / usa skin já no tamanho certo)
    for rect_world in _slots_direita:
        rect_screen = _world_rect_to_screen_rect(rect_world, camera)
        if not rect_screen.colliderect(screen_rect):
            continue
        Botao_Selecao(
            tela, "", rect_screen, fonte,
            __slot_skin_inimigo, (0, 0, 0),
            eventos=eventos, estado_global=EstadoArenaBotoes
        )

    t2 = time.perf_counter()  # SUSPEITO #2: desenho dos botões (ambos os lados)

    # ---- animações: posiciona pelo centro em MUNDO -> TELA a cada frame ----
    # usa a sua API: atualizar(tela, nova_pos=None, multiplicador=1)
    for anim, world_center in _anim_inimigos:
        scr = camera.TelaAPartirDoMundo(world_center)
        anim.atualizar(tela, nova_pos=(int(scr.x), int(scr.y)), multiplicador=camera.Zoom)

    t3 = time.perf_counter()  # SUSPEITO #3: animações dos INIMIGOS

    for anim, world_center in _anim_aliados:
        scr = camera.TelaAPartirDoMundo(world_center)
        anim.atualizar(tela, nova_pos=(int(scr.x), int(scr.y)), multiplicador=camera.Zoom)

    t4 = time.perf_counter()  # SUSPEITO #4: animações dos ALIADOS

    # ---- log (imprime de tempos em tempos para não matar o FPS) ----
    if __dbg_count % 15 == 0:
        bg_ms    = (t1 - t0) * 1000.0
        btn_ms   = (t2 - t1) * 1000.0
        inim_ms  = (t3 - t2) * 1000.0
        aliado_ms= (t4 - t3) * 1000.0
        total_ms = (t4 - t0) * 1000.0
        print(f"[DBG] BG:{bg_ms:6.2f} ms | Botoes:{btn_ms:6.2f} ms | "
              f"Anim Inim:{inim_ms:6.2f} ms | Anim Ali:{aliado_ms:6.2f} ms | "
              f"TOTAL:{total_ms:6.2f} ms | zoom={camera.Zoom:.2f}")

def BatalhaLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes, Icones, Player
    from Codigo.Cenas.Mundo import player

    if Cores is None:
        Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Consumiveis, Equipaveis, Estruturas, Animaçoes, Icones = info["Conteudo"]

    parametros = info["ParametrosConfronto"]

    # mantém sua lógica existente para montar as equipes
    if parametros.get("BatalhaSimples"):
        Equipe = None
        Membros = 0
        for equipe in player.Equipes:
            for membro in equipe:
                if membro is not None:
                    Equipe = equipe
                Membros += 1
            if Equipe is not None:
                break

        if Equipe is None:
            filtrada = [x for x in player.Pokemons if x is not None]
            Equipe = filtrada[:6]

        parametros.update({
            "EquipeInimiga": GerarMatilha(parametros["AlvoConfronto"].Dados, Membros),
            "EquipeAliada": Equipe
        })

    while estados["Batalha"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Batalha"] = False
                estados["Rodando"] = False

        TelaFundoBatalha(tela, estados, eventos, parametros)

        if config["FPS Visivel"]:
            fps_atual = relogio.get_fps()
            texto = f"FPS: {fps_atual:.1f}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x, 0), (255, 255, 255), (0, 0, 0))

        AtualizarMusica()
        Clarear(tela, info)
        pygame.display.update()
        relogio.tick(config["FPS"])

    Escurecer(tela, info)
