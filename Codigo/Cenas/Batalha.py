import pygame, random, time

from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Modulos.Paineis import PainelPokemonBatalha, CriarSurfacePainelAtaque, PAINEL_ATAQUE_CACHE
from Codigo.Prefabs.BotoesPrefab import Botao_Selecao, Botao, Botao_invisivel
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda, Animar, caixa_de_texto, Fluxo
from Codigo.Prefabs.Animações import Animação
from Codigo.Prefabs.Sonoridade import Musica, AtualizarMusica, tocar
from Codigo.Geradores.GeradorPokemon import GerarMatilha, CarregarAnimacaoPokemon, GeraPokemonBatalha, CarregarPokemon
# REMOVIDO: CameraBatalha e qualquer coisa de “mundo/zoom”

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

# estado simples para slots, animações e skins
_slots_esquerda = None
_slots_direita  = None
_anim_inimigos  = None
_anim_aliados   = None
_slot_skin_aliado = None
_slot_skin_inimigo = None

EstadoArenaBotoesAliado = {}
EstadoArenaBotoesInimigo = {}
EstadoArenaFalso = {}

BG = {}

# animações de entrada (deslizarem para a tela)
_anima_t0 = None
_anima_dur_ms = 480
anima = {
    "_anima_painel_aliado": None,
    "_anima_painel_inimigo": None,
    "_anima_painel_conteudo": None,
    "Y1": 895, "Y2": 1080,
    "Y3": -200, "Y4": 0,
    "Y5": 895, "Y6": 1080
}

def definir_ativos(equipe):
    for poke in equipe:
        poke["Ativo"] = False
        poke["Pos"] = None
    qtd = min(3, len(equipe))
    ativos = random.sample(equipe, qtd)
    posicoes = random.sample(range(1, 10), qtd)
    for poke, pos in zip(ativos, posicoes):
        poke["Ativo"] = True
        poke["Pos"] = pos
    return ativos

def Arenas(tela, parametros, Fontes, eventos, dx_esq, dx_dir):
    """
    Desenha as arenas (aliados à esquerda, inimigos à direita).
    - Quando parametros['ModoAlvificando'] == False: comportamento normal (seleção, animações).
    - Quando True: VISUAL com borda piscante nas casas-alvo válidas (amarelo)
      + Botao_invisivel por casa válida que adiciona 'A#' ou 'I#' (ou linha inteira no caso de 'linha').
    """

    fonte = Fontes[16]
    modo_alvo = bool(parametros.get("ModoAlvificando"))

    aliado_sel = parametros.get("AliadoSelecionado")
    atk_sel    = parametros.get("AtaqueAliadoSelecionado")
    mov_sel    = parametros.get("MovimentoSelecionado")  # 0/1/2 ou str

    def _attack_name(a):
        if not a: return None
        return a.get("Nome") or a.get("nome") or a.get("Ataque") or None

    # alvo do ataque (só interessa no modo alvo)
    alvo_info = {'lado': None, 'tipo': 'none', 'qtd': 0}
    if modo_alvo and atk_sel:
        alvo_info = _parse_alvo_str(atk_sel.get("Alvo") or atk_sel.get("alvo"))

    # decidir quais casas piscam
    highlight_A = set()
    highlight_I = set()
    if modo_alvo:
        if atk_sel:
            t = alvo_info.get('tipo')
            lado = alvo_info.get('lado')
            if t == 'celula':
                if lado == 'I':
                    highlight_I = set(range(9))
                elif lado == 'A':
                    highlight_A = set(range(9))
            elif t == 'linha':
                firsts = {0, 3, 6}
                if lado == 'I':
                    highlight_I = firsts
                elif lado == 'A':
                    highlight_A = firsts
            # qualquer outro tipo => não pisca nada
        else:
            # sem ataque: se está tentando mover (mov 1), pisca aliados (exceto a própria casa)
            if mov_sel == 1:
                highlight_A = set(range(9))

    # remover a casa do próprio aliado quando for highlight de aliados
    if highlight_A and aliado_sel:
        try:
            pos_ali = max(1, min(9, int(aliado_sel.get("Pos", 1))))
            highlight_A.discard(pos_ali - 1)
        except Exception:
            pass

    cor_amarelo = Cores["amarelo"]

    # ======== helpers para ações invisíveis ========
    def _add_codes_line(prefix, idx0based, p):
        """Adiciona os 3 códigos da linha do índice 0-based."""
        base = (idx0based // 3) * 3
        for k in (base + 1, base + 2, base + 3):
            code = f"{prefix}{k}"
            lst = p.setdefault("AlvosSelecionados", [])
            if code not in lst:
                lst.append(code)

    def _add_code_single(prefix, idx0based, p):
        code = f"{prefix}{idx0based + 1}"
        lst = p.setdefault("AlvosSelecionados", [])
        if code not in lst:
            lst.append(code)

    # ======== Aliados (esquerda) ========
    for i, rect in enumerate(_slots_esquerda):
        poke = next((p for p in parametros.get("AliadosAtivos", []) if p.get("Pos") == i + 1), None)
        rect_anim = rect.move(dx_esq, 0)

        if modo_alvo:
            pisc = (i in highlight_A)
            cor_borda_base = cor_amarelo if pisc else (0, 0, 0)

            # VISUAL somente (piscar onde pode clicar)
            Botao_Selecao(
                tela=tela, texto="", espaço=rect_anim, Fonte=fonte,
                cor_fundo=_slot_skin_aliado, cor_borda_normal=cor_borda_base,
                cor_borda_esquerda=None, cor_borda_direita=None, cor_passagem=None,
                id_botao=f"ali-{i}",
                estado_global=EstadoArenaFalso, eventos=None,
                funcao_esquerdo=None, desfazer_esquerdo=None,
                Piscante=pisc
            )

            if pisc:
                # clique válido em aliados
                if atk_sel:
                    nome = _attack_name(atk_sel)
                    if alvo_info.get('tipo') == 'linha':
                        def _acao_A_linha(ii=i, p=parametros, nm=nome):
                            _add_codes_line('A', ii, p)
                            if nm: p["MovimentoSelecionado"] = nm
                        Botao_invisivel(rect_anim, _acao_A_linha)
                    elif alvo_info.get('tipo') == 'celula':
                        def _acao_A_casa(ii=i, p=parametros, nm=nome):
                            _add_code_single('A', ii, p)
                            if nm: p["MovimentoSelecionado"] = nm
                        Botao_invisivel(rect_anim, _acao_A_casa)
                    else:
                        # tipos não suportados: não cria invisível
                        pass
                else:
                    # movimento 1 (mover) — só adicionar A#, não mexe no movimento
                    if mov_sel == 1:
                        def _acao_A_move(ii=i, p=parametros):
                            _add_code_single('A', ii, p)
                        Botao_invisivel(rect_anim, _acao_A_move)

        else:
            # comportamento normal
            func_esq_ali = [
                (lambda p=poke: parametros.update({"AliadoSelecionado": p})),
                (lambda a=anima: a.update({
                    "_anima_painel_aliado": pygame.time.get_ticks(),
                    "Y1": 1080, "Y2": 895
                })),
            ]
            desf_esq_ali = [
                (lambda: parametros.update({"AliadoSelecionado": None})),
                (lambda a=anima: a.update({
                    "_anima_painel_aliado": pygame.time.get_ticks(),
                    "Y1": 895, "Y2": 1080
                })),
            ]
            Botao_Selecao(
                tela=tela, texto="", espaço=rect_anim, Fonte=fonte,
                cor_fundo=_slot_skin_aliado, cor_borda_normal=(0, 0, 0),
                cor_passagem=(200, 200, 200), cor_borda_esquerda=Cores["azul"],
                id_botao=f"ali-{i}",
                eventos=eventos, estado_global=EstadoArenaBotoesAliado,
                funcao_esquerdo=func_esq_ali,
                desfazer_esquerdo=desf_esq_ali
            )

    # ======== Inimigos (direita) ========
    for i, rect in enumerate(_slots_direita):
        poke = next((p for p in parametros.get("InimigosAtivos", []) if p.get("Pos") == i + 1), None)
        rect_anim = rect.move(dx_dir, 0)

        if modo_alvo:
            pisc = (i in highlight_I)
            cor_borda_base = cor_amarelo if pisc else (0, 0, 0)

            Botao_Selecao(
                tela=tela, texto="", espaço=rect_anim, Fonte=fonte,
                cor_fundo=_slot_skin_inimigo, cor_borda_normal=cor_borda_base,
                cor_borda_esquerda=None, cor_borda_direita=None, cor_passagem=None,
                id_botao=f"ini-{i}",
                estado_global=EstadoArenaFalso, eventos=None,
                funcao_esquerdo=None, desfazer_esquerdo=None,
                Piscante=pisc
            )

            if pisc and atk_sel:
                nome = _attack_name(atk_sel)
                if alvo_info.get('tipo') == 'linha':
                    def _acao_I_linha(ii=i, p=parametros, nm=nome):
                        _add_codes_line('I', ii, p)
                        if nm: p["MovimentoSelecionado"] = nm
                    Botao_invisivel(rect_anim, _acao_I_linha)
                elif alvo_info.get('tipo') == 'celula':
                    def _acao_I_casa(ii=i, p=parametros, nm=nome):
                        _add_code_single('I', ii, p)
                        if nm: p["MovimentoSelecionado"] = nm
                    Botao_invisivel(rect_anim, _acao_I_casa)
                else:
                    pass  # outros tipos: não cria invisível

        else:
            func_esq_ini = [
                (lambda p=poke: parametros.update({"InimigoSelecionado": p})),
                (lambda a=anima: a.update({
                    "_anima_painel_inimigo": pygame.time.get_ticks(),
                    "Y3": -200, "Y4": 0
                })),
            ]
            desf_esq_ini = [
                (lambda: parametros.update({"InimigoSelecionado": None})),
                (lambda a=anima: a.update({
                    "_anima_painel_inimigo": pygame.time.get_ticks(),
                    "Y3": 0, "Y4": -200
                })),
            ]
            Botao_Selecao(
                tela=tela, texto="", espaço=rect_anim, Fonte=fonte,
                cor_fundo=_slot_skin_inimigo, cor_borda_normal=(0, 0, 0),
                cor_passagem=(200, 200, 200), cor_borda_esquerda=Cores["vermelho"],
                id_botao=f"ini-{i}",
                eventos=eventos, estado_global=EstadoArenaBotoesInimigo,
                funcao_esquerdo=func_esq_ini,
                desfazer_esquerdo=desf_esq_ini
            )

def Desenhar_Botoes_Combate(tela, parametros):
    BTN = 70
    BORDER = 3
    SW, SH = 1920, 1080  # layout fixo

    # recursos globais esperados: Fontes, Icones, Pokemons, CarregarPokemon, pygame
    fonte = Fontes[30]

    # eventos/estado para Botao (normal)
    eventos = parametros.get("Eventos") or parametros.get("eventos") or []
    estado_clique = parametros.setdefault("EstadoBotoesCombateSimples", {})

    # ---------- helpers ----------
    def _blit_center_scaled(rect_tuple, surf, pad=6):
        if not isinstance(surf, pygame.Surface):
            return
        rx, ry, rw, rh = rect_tuple
        max_w = max(1, rw - pad * 2)
        max_h = max(1, rh - pad * 2)
        iw, ih = surf.get_size()
        if iw <= 0 or ih <= 0:
            return
        esc = min(max_w / iw, max_h / ih)
        nw = max(1, int(iw * esc))
        nh = max(1, int(ih * esc))
        img = pygame.transform.smoothscale(surf, (nw, nh))
        dst = img.get_rect(center=(rx + rw // 2, ry + rh // 2))
        tela.blit(img, dst)

    def _sprite_por_nome(nome_key):
        if not nome_key:
            return None
        spr = Pokemons.get(nome_key)
        if spr is None:
            spr = CarregarPokemon(nome_key, Pokemons)
        return spr

    # ---------- dados ----------
    equipe_a = parametros.get("EquipeAliada", [])
    reserva_a = [p for p in equipe_a if not p.get("Ativo", True)]

    equipe_i = (parametros.get("EquipeInimiga")
                or parametros.get("EquipeInimigos")
                or [])
    reserva_i = [p for p in equipe_i if not p.get("Ativo", True)]

    # ---------- grupo ALIADOS (inferior esquerdo) ----------
    base_ax = 0
    base_ay = SH - BTN

    rects_a = [
        (base_ax + BTN * 0, base_ay, BTN, BTN),  # Fugir (normal)
        (base_ax + BTN * 1, base_ay, BTN, BTN),  # Sel 0
        (base_ax + BTN * 2, base_ay, BTN, BTN),  # Sel 1
        (base_ax + BTN * 3, base_ay, BTN, BTN),  # Sel 2
    ]

    # 0) Fugir — BOTAO (normal)  [FIX: sem += dentro do update]
    Botao(
        tela, "", rects_a[0],
        cor_normal=(200, 200, 200), cor_borda=(0, 0, 0), cor_passagem=(255, 255, 255),
        acao=lambda: parametros.__setitem__("Fuga", parametros.get("Fuga", 0) + 20),
        Fonte=fonte, estado_clique=estado_clique, eventos=eventos,
        grossura=BORDER, cor_texto=(0, 0, 0)
    )
    ic_fugir = Icones.get("fugir")
    _blit_center_scaled(rects_a[0], ic_fugir, pad=6)

    # 1..3) Seleções aliados — BOTOES DE SELEÇÃO (sprites por cima ou "-" se vazio)
    for i in range(3):
        r = rects_a[i + 1]
        tem_poke = i < len(reserva_a)
        Botao_Selecao(
            tela, "-" if not tem_poke else "", r, fonte,
            cor_fundo=(200, 200, 200), cor_borda_normal=(0, 0, 0),
            cor_passagem=(255, 255, 255),
            grossura=BORDER
        )
        if tem_poke:
            nome_key = reserva_a[i].get("Nome", "")
            spr = _sprite_por_nome(nome_key)
            _blit_center_scaled(r, spr, pad=4)

    # ---------- grupo INIMIGOS (superior direito) ----------
    base_ix = SW - BTN * 4
    base_iy = 0

    rects_i = [
        (base_ix + BTN * 0, base_iy, BTN, BTN),  # Sel 0
        (base_ix + BTN * 1, base_iy, BTN, BTN),  # Sel 1
        (base_ix + BTN * 2, base_iy, BTN, BTN),  # Sel 2
        (base_ix + BTN * 3, base_iy, BTN, BTN),  # Trégua (normal)
    ]

    # 0..2) Seleções inimigos — BOTOES DE SELEÇÃO (sprites por cima ou "-")
    for i in range(3):
        r = rects_i[i]
        tem_poke = i < len(reserva_i)
        Botao_Selecao(
            tela, "-" if not tem_poke else "", r, fonte,
            cor_fundo=(200, 200, 200), cor_borda_normal=(0, 0, 0),
            cor_passagem=(255, 255, 255),
            grossura=BORDER
        )
        if tem_poke:
            nome_key = reserva_i[i].get("Nome", "")
            spr = _sprite_por_nome(nome_key)
            _blit_center_scaled(r, spr, pad=4)

    # 3) Trégua — BOTAO (normal)
    Botao(
        tela, "", rects_i[3],
        cor_normal=(200, 200, 200), cor_borda=(0, 0, 0), cor_passagem=(255, 255, 255),
        acao=(lambda: None), Fonte=fonte, estado_clique=estado_clique, eventos=eventos,
        grossura=BORDER, cor_texto=(0, 0, 0)
    )
    ic_tregua = Icones.get("tregua")
    _blit_center_scaled(rects_i[3], ic_tregua, pad=6)

# ===================== HELPERS (cole no topo do arquivo) =====================
def _parse_alvo_str(alvo_raw):
    """
    -> { 'lado': 'I'|'A'|None, 'tipo': 'celula'|'linha'|'none', 'qtd': int }
    """
    if not alvo_raw:
        return {'lado': None, 'tipo': 'none', 'qtd': 0}
    s = str(alvo_raw).strip().lower()

    # quantidade (ex.: "inimigo x2")
    qtd = 1
    if "x" in s:
        try:
            qtd = int(s.split("x")[-1].strip())
        except Exception:
            qtd = 1
        s = s.split("x")[0].strip()

    if s in ("aleatorio", "sem alvo", "semalvo", "all", "todos"):
        return {'lado': None, 'tipo': 'none', 'qtd': 0}

    if s.startswith("linha"):
        lado = 'A' if "aliado" in s else 'I'
        return {'lado': lado, 'tipo': 'linha', 'qtd': qtd}

    if "inimigo" in s:
        return {'lado': 'I', 'tipo': 'celula', 'qtd': qtd}

    if "aliado" in s:
        return {'lado': 'A', 'tipo': 'celula', 'qtd': qtd}

    return {'lado': None, 'tipo': 'none', 'qtd': 0}

def _reserva_btn_rects(parametros):
    """
    Retângulos dos 3 botões de reserva usados em Desenhar_Botoes_Combate.
    Se não houver base salva em parametros, usa (0,990,220,90) como padrão.
    """
    import pygame
    pos_base = parametros.get("PosBaseBotoesCombate", (0, 990, 220, 90))
    x, y, w, h = pos_base
    tamanho_botao = h
    espacamento = 10
    bx = x
    by = y - tamanho_botao - 10
    rects = []
    for i in range(3):
        rx = bx + (i+1)*(tamanho_botao+espacamento)
        rects.append(pygame.Rect(rx, by, tamanho_botao, tamanho_botao))
    return rects  # R1, R2, R3
# ============================================================================

def TelaAlvoBatalha(tela, estados, eventos, parametros):
    import pygame
    global _slots_esquerda, _slots_direita, _anima_t0, _anima_dur_ms

    if _slots_esquerda is None or _slots_direita is None:
        return

    sw, sh = tela.get_size()

    # ===== animação (mesma da TelaFundoBatalha) =====
    esq_first = _slots_esquerda[0]; esq_lastc = _slots_esquerda[2]
    painel_w  = esq_lastc.right - esq_first.left
    if _anima_t0 is None:
        _anima_t0 = pygame.time.get_ticks()
    dx_esq = Animar(-(esq_first.left + painel_w), 0, _anima_t0, tempo=_anima_dur_ms)
    dir_first = _slots_direita[0]
    dx_dir = Animar((sw - dir_first.left), 0, _anima_t0, tempo=_anima_dur_ms)

    # ===== helpers =====
    def _attack_name(a):
        if not a: return None
        return a.get("Nome") or a.get("nome") or a.get("Ataque") or str(a)

    def _idx_atacante(equipe, aliado_sel):
        if not equipe or not aliado_sel: 
            return None
        for i, p in enumerate(equipe):
            if p is aliado_sel:  # identidade
                return i
        pos = aliado_sel.get("Pos", None)
        if pos is not None:
            for i, p in enumerate(equipe):
                if p.get("Pos", None) == pos:
                    return i
        nome = aliado_sel.get("Nome", None)
        if nome is not None:
            for i, p in enumerate(equipe):
                if p.get("Nome", None) == nome:
                    return i
        return None

    def _centro_slot_aliado_por_idxEquipe(idxEquipe):
        equipe = parametros.get("EquipeAliada", [])
        if not isinstance(idxEquipe, int) or idxEquipe < 0 or idxEquipe >= len(equipe):
            return None
        pos = equipe[idxEquipe].get("Pos", 1)
        i = max(0, min(8, int(pos) - 1))
        return _slots_esquerda[i].move(dx_esq, 0).center

    def _destinos_por_codes(codes):
        """Suporta A#, I#, R#. (Sem AL/IL)."""
        pts = []
        # reserva rects (R1..R3)
        rects_R = _reserva_btn_rects(parametros)
        for code in (codes or []):
            if isinstance(code, str) and len(code) >= 2:
                prefix, n = code[0].upper(), code[1:]
                if n.isdigit():
                    j = max(1, min(9, int(n)))
                    if prefix == 'I':  # inimigo
                        i = j - 1
                        pts.append(_slots_direita[i].move(dx_dir, 0).center)
                    elif prefix == 'A':  # aliado
                        i = j - 1
                        pts.append(_slots_esquerda[i].move(dx_esq, 0).center)
                    elif prefix == 'R' and 1 <= j <= 3:  # reserva
                        pts.append(rects_R[j-1].center)
        return pts

    # ===== estado atual =====
    equipe         = parametros.get("EquipeAliada", [])
    aliado_sel     = parametros.get("AliadoSelecionado")
    atk_sel        = parametros.get("AtaqueAliadoSelecionado")
    mov_sel        = parametros.get("MovimentoSelecionado")  # 0/1/2 ou str
    alvo_unitario  = parametros.get("AlvoSelecionado")       # pode existir p/ movimentos
    alvos_now      = list(parametros.get("AlvosSelecionados", []))
    alvos_prev     = list(parametros.get("_alvos_snapshot", alvos_now))
    clicked_now    = any(e.type == pygame.MOUSEBUTTONDOWN and e.button in (1,3) for e in eventos)

    # ===== detectar mudança de ataque (regras de reset específicas) =====
    curr_aliado_id = (aliado_sel or {}).get("Nome")
    curr_atk_id    = (atk_sel or {}).get("Ataque") or (atk_sel or {}).get("nome") or (atk_sel or {}).get("Nome")
    last_atk_id    = parametros.get("_last_ataque_id")
    if last_atk_id != curr_atk_id:
        # atualiza marcadores
        parametros["_last_ataque_id"] = curr_atk_id
        parametros["_last_aliado_id"] = curr_aliado_id
        # se mudou para OUTRO ataque (não None) => reset total dos 3
        if curr_atk_id is not None:
            parametros["Atacante"] = None
            parametros["AlvosSelecionados"] = []
            parametros["MovimentoSelecionado"] = None
            parametros["_alvo_ready"] = False
            alvos_now = []
            alvos_prev = []
            parametros["ModoAlvificando"] = True  # entra no alvo p/ novo ataque
        # se mudou para None => não reseta nada

    # ===== origem do fluxo (preferir AliadoSelecionado; fallback Atacante) =====
    x1 = y1 = None
    if aliado_sel is not None:
        try:
            idx_ali = max(0, min(8, int(aliado_sel.get("Pos", 1)) - 1))
        except (TypeError, ValueError):
            idx_ali = 0
        start_rect = _slots_esquerda[idx_ali].move(dx_esq, 0)
        x1, y1 = start_rect.center
    elif isinstance(parametros.get("Atacante"), int):
        origem = _centro_slot_aliado_por_idxEquipe(parametros["Atacante"])
        if origem: x1, y1 = origem

    # ====== Parte 1: ATAQUE (fluxo até mouse enquanto seleciona) ======
    # Entrar no modo se tiver aliado + ataque
    if aliado_sel is not None and atk_sel is not None:
        if not parametros.get("ModoAlvificando"):
            parametros["ModoAlvificando"] = True

        # qtd de alvos necessários
        alvo_info = _parse_alvo_str(atk_sel.get("Alvo") or atk_sel.get("alvo"))
        qtd_need  = max(0, int(alvo_info.get('qtd') or 0))

        # desenha fluxo até o mouse enquanto não completou
        if x1 is not None and qtd_need > 0 and parametros.get("ModoAlvificando"):
            done = (len(alvos_now) >= qtd_need)
            if not done:
                mx, my = pygame.mouse.get_pos()
                Fluxo(tela, x1, y1, mx, my, forma="seta",
                      pontos_por_100px=15, frequencia=4, velocidade=4, cor_base=(0,255,120), raio=6)

            # sair do modo: completou ou clique inútil
            if done or (clicked_now and len(alvos_now) == len(alvos_prev)):
                parametros["ModoAlvificando"] = False
                # define Atacante ao sair (se ainda não definido)
                if parametros.get("Atacante") is None:
                    parametros["Atacante"] = _idx_atacante(equipe, aliado_sel)
                # NÃO resetar nada aqui (conforme pedido)

    # ====== Parte 2: MOVIMENTO 0/1/2 (fluxo até mouse; sair em clique inútil) ======
    if (isinstance(mov_sel, int) and mov_sel in (0,1,2)
        and aliado_sel is not None
        and not alvo_unitario):  # "alvo selecionado não exista"
        if not parametros.get("ModoAlvificando"):
            parametros["ModoAlvificando"] = True

        if x1 is not None and parametros.get("ModoAlvificando"):
            mx, my = pygame.mouse.get_pos()
            Fluxo(tela, x1, y1, mx, my, forma="seta",
                  pontos_por_100px=15, frequencia=4, velocidade=4, cor_base=(255,220,90), raio=6)

        if clicked_now:
            if len(alvos_now) == len(alvos_prev):
                # clique inútil => sai do modo + limpa ataque sel + estado painel
                parametros["ModoAlvificando"] = False
                parametros["AtaqueAliadoSelecionado"] = None
                parametros["EstadoBotoesPainelPokemonBatalha"] = {}
            else:
                # houve adição de alvo; pegar o alvo recém-adicionado
                added = None
                prev_set = set(alvos_prev)
                for code in alvos_now:
                    if code not in prev_set:
                        added = code
                if added:
                    if isinstance(added, str):
                        up = added.upper()
                        if up.startswith('A'):
                            parametros["MovimentoSelecionado"] = 1
                        elif up.startswith('R'):
                            parametros["MovimentoSelecionado"] = 2
                    # define Atacante e sai do modo
                    if parametros.get("Atacante") is None:
                        parametros["Atacante"] = _idx_atacante(equipe, aliado_sel)
                    parametros["ModoAlvificando"] = False

    # ====== Parte 3: Fluxos finais (quando tudo definido) ======
    mov_final = parametros.get("MovimentoSelecionado")
    atk_idx   = parametros.get("Atacante")
    tem_fluxo_final = (mov_final is not None and isinstance(atk_idx, int) and len(alvos_now) > 0)

    if tem_fluxo_final:
        origem = _centro_slot_aliado_por_idxEquipe(atk_idx)
        if origem:
            x0, y0 = origem
            for (dx_, dy_) in _destinos_por_codes(alvos_now):
                Fluxo(tela, x0, y0, dx_, dy_, forma="seta",
                      pontos_por_100px=15, frequencia=4, velocidade=4, cor_base=(100,200,255), raio=6)

    # ===== DEBUG overlay =====
    try:
        fonte_dbg = pygame.font.SysFont(None, 20)
        linhas = [
            f"MOV: {mov_final!r}",
            f"ATACANTE(idx): {atk_idx}",
            f"ALVOS: {alvos_now}",
            f"MODO_ALV: {parametros.get('ModoAlvificando')}",
            f"CLICK: {clicked_now}, PREV_Len={len(alvos_prev)} -> NOW_Len={len(alvos_now)}",
        ]
        pad = 6
        surfs = [fonte_dbg.render(s, True, (230,230,230)) for s in linhas]
        box_w = max(s.get_width() for s in surfs) + pad*2
        box_h = sum(s.get_height() for s in surfs) + pad*2 + 2*(len(surfs)-1)
        rect = pygame.Rect(10, 10, box_w, box_h)
        overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        tela.blit(overlay, rect.topleft)
        y = rect.top + pad
        for s in surfs:
            tela.blit(s, (rect.left + pad, y)); y += s.get_height() + 2
    except Exception:
        pass

    # ===== atualizar snapshot para detectar clique inútil no próximo frame =====
    parametros["_alvos_snapshot"] = list(alvos_now)

# ==================== FUNDO/GRIDS/POKÉMONS (SEM CÂMERA) ====================
def TelaFundoBatalha(tela, estados, eventos, parametros):
    global _slots_esquerda, _slots_direita, _anim_inimigos, _anim_aliados
    global _slot_skin_aliado, _slot_skin_inimigo, _anima_t0

    sw, sh = tela.get_size()

    # Layout fixo em tela
    margem = 260
    gap    = 16
    tile   = 170

    # Inicialização 1x: slots e skins
    if _slots_esquerda is None or _slots_direita is None:
        painel_w = tile * 3 + gap * 2
        painel_h = tile * 3 + gap * 2
        top_y    = sh // 2 - painel_h // 2
        origem_esq_x = margem
        origem_dir_x = sw - margem - painel_w

        _slots_esquerda = []
        _slots_direita  = []
        for r in range(3):
            for c in range(3):
                x  = origem_esq_x + c * (tile + gap)
                y  = top_y       + r * (tile + gap)
                x2 = origem_dir_x + c * (tile + gap)
                _slots_esquerda.append(pygame.Rect(x,  y,  tile, tile))
                _slots_direita.append(pygame.Rect(x2, y,  tile, tile))

        # skins dos slots (escala única)
        _slot_skin_aliado  = pygame.transform.scale(Fundos["FundoPokemonAliado"],  (tile, tile))
        _slot_skin_inimigo = pygame.transform.scale(Fundos["FundoPokemonInimigo"], (tile, tile))

    # tick inicial para animação de entrada
    if _anima_t0 is None:
        _anima_t0 = pygame.time.get_ticks()

    # deslocamentos horizontais animados
    esq_first = _slots_esquerda[0]; esq_lastc = _slots_esquerda[2]
    painel_w  = esq_lastc.right - esq_first.left
    dx_esq = Animar(-(esq_first.left + painel_w), 0, _anima_t0, tempo=_anima_dur_ms)

    dir_first = _slots_direita[0]
    dx_dir = Animar((sw - dir_first.left), 0, _anima_t0, tempo=_anima_dur_ms)

    Arenas(tela, parametros, Fontes, eventos, dx_esq, dx_dir)

    # Sprites animados (1x para criar; depois só atualizar posição)
    if _anim_inimigos is None or _anim_aliados is None:
        _anim_inimigos, _anim_aliados = [], []
        equipe_inimiga = [p for p in parametros.get("InimigosAtivos", []) if p and p.get("Ativo")]
        equipe_aliada  = [p for p in parametros.get("AliadosAtivos",  []) if p and p.get("Ativo")]

        for pkm in equipe_inimiga:
            idx = max(0, min(8, int(pkm.get("Pos", 1)) - 1))
            nome = pkm["Nome"]
            cx, cy = _slots_direita[idx].center
            anim = Animação(Animaçoes.get(nome, CarregarAnimacaoPokemon(nome, Animaçoes)),
                            (cx, cy), tamanho=1.1, intervalo=30)
            _anim_inimigos.append((anim, (cx, cy)))

        for pkm in equipe_aliada:
            idx = max(0, min(8, int(pkm.get("Pos", 1)) - 1))
            nome = pkm["Nome"]
            cx, cy = _slots_esquerda[idx].center
            anim = Animação(Animaçoes.get(nome, CarregarAnimacaoPokemon(nome, Animaçoes)),
                            (cx, cy), tamanho=1.1, intervalo=30, inverted=True)
            _anim_aliados.append((anim, (cx, cy)))

    # atualiza posição por frame (deslocamento horizontal)
    for anim_obj, (cx, cy) in _anim_inimigos:
        anim_obj.atualizar(tela, nova_pos=(int(cx + dx_dir), int(cy)), multiplicador=1.0)
    for anim_obj, (cx, cy) in _anim_aliados:
        anim_obj.atualizar(tela, nova_pos=(int(cx + dx_esq), int(cy)), multiplicador=1.0)

# ==================== HUD ====================
def TelaHudBatalha(tela, estados, eventos, parametros):
    YA = Animar(anima["Y1"], anima["Y2"], anima["_anima_painel_aliado"])
    PainelPokemonBatalha(parametros["AliadoSelecionado"], tela, (360, YA), eventos, parametros, anima)

    YI = Animar(anima["Y3"], anima["Y4"], anima["_anima_painel_inimigo"])
    PainelPokemonBatalha(parametros["InimigoSelecionado"], tela, (360, YI), eventos, parametros, anima)

    Conteudo = None; atk = False
    if parametros["AtaqueAliadoSelecionado"] is not None:
        Conteudo = parametros["AtaqueAliadoSelecionado"]; atk = True
    elif parametros["AtaqueInimigoSelecionado"] is not None:
        Conteudo = parametros["AtaqueInimigoSelecionado"]; atk = True
    elif parametros["ItemSelecionado"] is not None:
        Conteudo = parametros["ItemSelecionado"]; atk = False

    YC = Animar(anima["Y5"], anima["Y6"], anima["_anima_painel_conteudo"])

    if Conteudo is not None and atk:
        nome_atk = Conteudo.get("Ataque") or Conteudo.get("nome") or Conteudo.get("Nome") or ""
        surf = PAINEL_ATAQUE_CACHE.get(nome_atk)
        if surf is None:
            surf = CriarSurfacePainelAtaque(Conteudo, tamanho=(360, 180))
            PAINEL_ATAQUE_CACHE[nome_atk] = surf
        tela.blit(surf, (1280, YC))
    
    if parametros["LogAtual"] == []:
        txt = "Passar Turno"
    else:
        txt = "Pronto!"

    Botao(tela, txt, (1660,1020,260,60),Texturas["amarelo"],(0,0,0),(240,240,240),lambda: parametros.update({"Pronto": True}), Fontes[35], BG, eventos)

    if parametros["Atacante"] == None or parametros["MovimentoSelecionado"] == None or parametros["AlvosSelecionados"] == []:     
        Botao(tela, "Preparar", (1660,960,260,60),Cores["vermelho"],(0,0,0),(240,240,240),lambda: tocar("Bloq"), Fontes[35], BG, eventos)
    
    else:
        Botao(tela, "Preparar", (1660,960,260,60),Texturas["vermelho"],(0,0,0),(240,240,240),lambda: parametros["LogAtual"].append({"Atacante":parametros["Atacante"], "Movimento": parametros["MovimentoSelecionado"], "Alvo": parametros["AlvosSelecionados"]}), Fontes[35], BG, eventos)
    
    Desenhar_Botoes_Combate(tela,parametros)

def TelaBatalha(tela, estados, eventos, parametros):

    TelaFundoBatalha(tela, estados, eventos, parametros)
    TelaAlvoBatalha(tela, estados, eventos, parametros)
    TelaHudBatalha(tela, estados, eventos, parametros)

def BatalhaLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes, Icones, Player
    from Codigo.Cenas.Mundo import player

    Player = player

    if Cores is None:
        Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Consumiveis, Equipaveis, Estruturas, Animaçoes, Icones = info["Conteudo"]

    parametros = info["ParametrosConfronto"]

    # montar equipes simples
    if parametros.get("BatalhaSimples"):
        Equipe = None
        Membros = 0
        for equipe in Player.Equipes:
            for membro in equipe:
                if membro is not None:
                    Equipe = equipe
                Membros += 1
            if Equipe is not None:
                break
        if Equipe is None:
            filtrada = [x for x in Player.Pokemons if x is not None]
            Equipe = filtrada[:6]

        parametros.update({
            "EquipeInimiga": [GeraPokemonBatalha(p) for p in GerarMatilha(parametros["AlvoConfronto"].Dados, Membros)],
            "EquipeAliada":  [GeraPokemonBatalha(p) for p in Equipe],
            "AliadoSelecionado": None,
            "InimigoSelecionado": None,
            "AtaqueAliadoSelecionado": None,
            "AtaqueInimigoSelecionado": None,
            "ItemSelecionado": None,
            "Atacante": None,
            "AlvosSelecionados": [],
            "MovimentoSelecionado": None,
            "ModoAlvificando": False,
            "Pronto": False,
            "Fuga": 0,
            "LogAtual": [],
            "EstadoBotoesPainelPokemonBatalha": {},
        })
        parametros["AliadosAtivos"]  = definir_ativos(parametros["EquipeAliada"])
        parametros["InimigosAtivos"] = definir_ativos(parametros["EquipeInimiga"])

    # controle do tempo para decaimento da Fuga
    tempo_acumulado = 0.0

    while estados["Batalha"]:
        dt = relogio.get_time() / 1000.0  # delta time em segundos
        tempo_acumulado += dt

        # reduzir Fuga a cada 1s, -10 até o mínimo 0
        if parametros["Fuga"] < 100 and tempo_acumulado >= 1.0:
            parametros["Fuga"] = max(0, parametros["Fuga"] - 10)
            tempo_acumulado = 0.0

        # se Fuga atingir 100, encerrar batalha e voltar ao Mundo
        if parametros["Fuga"] >= 100:
            estados["Batalha"] = False
            estados["Mundo"] = True
            break

        tela.blit(Fundos["FundoBatalha"], (0, 0))
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Batalha"] = False
                estados["Rodando"] = False

        TelaBatalha(tela, estados, eventos, parametros)

        # filtro preto proporcional à Fuga
        if parametros["Fuga"] > 0:
            alpha = int((parametros["Fuga"] / 100) * 255)
            filtro = pygame.Surface(tela.get_size())
            filtro.fill((0, 0, 0))
            filtro.set_alpha(alpha)
            tela.blit(filtro, (0, 0))

        if config["FPS Visivel"]:
            fps_atual = relogio.get_fps()
            texto = f"FPS: {fps_atual:.1f}"
            x = tela.get_width() - Fontes[25].size(texto)[0] - 10
            texto_com_borda(tela, texto, Fontes[25], (x, 0), (255, 255, 255), (0, 0, 0))

        AtualizarMusica()
        Clarear(tela, info)
        pygame.display.update()
        relogio.tick(config["FPS"])

    Escurecer(tela, info)
