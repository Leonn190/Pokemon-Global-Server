import pygame, random, time, re

from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Modulos.Paineis import PainelPokemonBatalha, CriarSurfacePainelAtaque, PainelAcao, PAINEL_ATAQUE_CACHE
from Codigo.Prefabs.BotoesPrefab import Botao_Selecao, Botao, Botao_invisivel, Botao_Tecla
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda, Animar, caixa_de_texto, Fluxo
from Codigo.Prefabs.Animações import Animação
from Codigo.Prefabs.Sonoridade import Musica, AtualizarMusica, tocar
from Codigo.Geradores.GeradorPokemon import GerarMatilha, CarregarAnimacaoPokemon, GeraPokemonBatalha, CarregarPokemon
from Codigo.Modulos.Config import TelaConfigurações
from Codigo.Modulos.DesenhoPlayer import DesenharPlayer
from Codigo.Server.ServerMundo import SairConta, SalvarConta

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
_anima_dur_ms = 450
anima = {
    "_anima_painel_aliado": None,
    "_anima_painel_inimigo": None,
    "_anima_painel_conteudo": None,
    "Y1": 895, "Y2": 1080,
    "Y3": -200, "Y4": 0,
    "Y5": 895, "Y6": 1080,

    "_anima_painel_acao": None,
    "X1": -155, "X2": 40,
}

Acao_surface_cache = []

# ======== ESTADOS GLOBAIS ========
EstadoEditorLog = {}            # estados genéricos (hover/click, etc. — se precisar)
EstadoBotoesAcao = {}           # estados por botão principal (seleção de ação)
EstadoBotoesApagar = {}         # estados por botão X (apagar ação)

def definir_ativos(equipe):
    # Filtra apenas os Pokémon válidos (não None)
    validos = [poke for poke in equipe if poke is not None]

    # Reseta status de todos os Pokémon válidos
    for poke in validos:
        poke["Ativo"] = False
        poke["Pos"] = None

    # Define até 3 ativos aleatoriamente
    qtd = min(3, len(validos))
    ativos = random.sample(validos, qtd)
    posicoes = random.sample(range(1, 10), qtd)

    for poke, pos in zip(ativos, posicoes):
        poke["Ativo"] = True
        poke["Pos"] = pos

    return ativos

# --- util interno: interpreta "inimigo", "aliado", "linha", "linha aliado", "inimigo x2" etc.
def _parse_alvo_str(s):
    """
    Retorna dict: {'tipo': 'celula'|'linha', 'lado': 'I'|'A'|None, 'qtd': int}
    Exemplos aceitos:
      "inimigo" / "inimigo x3"
      "aliado"  / "aliado x2"
      "linha" (implica inimigo) / "linha aliado" / "linha inimigo"
    """
    if not s:
        return {'tipo': 'none', 'lado': None, 'qtd': 1}

    s = str(s).strip().lower()
    qtd = 1
    m = re.search(r"x\s*(\d+)", s)
    if m:
        qtd = max(1, int(m.group(1)))

    tipo = 'celula'
    lado = None

    if "linha" in s:
        tipo = 'linha'
        if "aliad" in s:
            lado = 'A'
        elif "inimig" in s:
            lado = 'I'
        else:
            # padrão "linha" sozinho: nas regras, 1ª casa dos INIMIGOS
            lado = 'I'
    else:
        if "aliad" in s:
            lado = 'A'
        elif "inimig" in s:
            lado = 'I'

    return {'tipo': tipo, 'lado': lado, 'qtd': qtd}

# Guarda de energia para botões invisíveis
def _wrap_energy_guard(callback, parametros):
    def _cb():
        ali = parametros.get("AliadoSelecionado")
        if ali is not None:
            ene = int(ali.get("Energia", ali.get("EneAtual", 0)) or 0)
            custo = int(parametros.get("CustoAtualEnergia", 0) or 0)
            # bloqueia se Energia - Custo < -5
            if (ene - custo) < -5:
                try: tocar("Bloq")
                except Exception: pass
                return
        callback()
    return _cb

def Arenas(tela, parametros, Fontes, eventos, dx_esq, dx_dir):
    fonte = Fontes[16]
    modo_alvo = bool(parametros.get("ModoAlvificando"))

    aliado_sel = parametros.get("AliadoSelecionado")
    atk_sel    = parametros.get("AtaqueAliadoSelecionado")

    slots_rects = parametros.setdefault("SlotsRects", {"A": [None]*9, "I": [None]*9})
    slots_high  = parametros.setdefault("SlotsDestaque", {"A": set(), "I": set()})
    slots_rects["A"] = [None]*9
    slots_rects["I"] = [None]*9
    slots_high["A"]  = set()
    slots_high["I"]  = set()

    parametros.setdefault("AlvosSelecionados", [])

    # --- controle de reset (preserva quando finalizado ok) ---
    if not modo_alvo:
        if parametros.pop("__alvo_finalizado_ok", False):
            slots_high["A"].clear()
            slots_high["I"].clear()
            parametros["__ja_limpei_estado"] = True
        else:
            if parametros.get("__ja_limpei_estado", False) is False:
                parametros["AlvosSelecionados"]   = []
                parametros["AtacanteSelecionado"] = None
                parametros["MovimentoSelecionado"]= None
                parametros["__ja_limpei_estado"]  = True
            slots_high["A"].clear()
            slots_high["I"].clear()
    else:
        parametros["__ja_limpei_estado"] = False

    # ===== alvo/quantidade =====
    alvo_info = {'lado': None, 'tipo': 'none', 'qtd': 1}
    mov_especial = None
    if isinstance(atk_sel, int):
        mov_especial = atk_sel
    elif isinstance(atk_sel, dict):
        alvo_info = _parse_alvo_str(atk_sel.get("Alvo") or atk_sel.get("alvo"))
    elif isinstance(atk_sel, str):
        alvo_info = _parse_alvo_str(atk_sel)

    highlight_A, highlight_I = set(), set()
    if modo_alvo:
        if mov_especial == 1:
            highlight_A = set(range(9))
        elif mov_especial == 2:
            pass
        else:
            t = alvo_info['tipo']
            lado = alvo_info['lado']
            if t == 'celula':
                if lado == 'I': highlight_I = set(range(9))
                elif lado == 'A': highlight_A = set(range(9))
            elif t == 'linha':
                firsts = {0, 3, 6}
                if lado == 'I': highlight_I = firsts
                elif lado == 'A': highlight_A = firsts

    if modo_alvo and highlight_A and aliado_sel:
        try:
            pos_ali = max(1, min(9, int(aliado_sel.get("Pos", 1))))
            highlight_A.discard(pos_ali - 1)
        except Exception:
            pass

    slots_high["A"] = set(highlight_A)
    slots_high["I"] = set(highlight_I)

    cor_amarelo = Cores["amarelo"]

    # ==== helpers ====
    def _add_codes_line(prefix, idx0):
        base = (idx0 // 3) * 3
        for k in (base + 1, base + 2, base + 3):
            code = f"{prefix}{k}"
            if code not in parametros["AlvosSelecionados"]:
                parametros["AlvosSelecionados"].append(code)

    def _add_code_single(prefix, idx0):
        code = f"{prefix}{idx0 + 1}"
        if code not in parametros["AlvosSelecionados"]:
            parametros["AlvosSelecionados"].append(code)

    def _indice_do_aliado(aliado_dict):
        equipe = parametros.get("EquipeAliada") or []
        try:
            pos = int(aliado_dict.get("Pos", -1))
            for i, p in enumerate(equipe):
                if int(p.get("Pos", -2)) == pos:
                    return i
        except Exception:
            pass
        for i, p in enumerate(equipe):
            if p is aliado_dict or p == aliado_dict:
                return i
        return None

    def _apos_primeiro_alvo():
        if parametros.get("AtacanteSelecionado") is None and aliado_sel:
            parametros["AtacanteSelecionado"] = _indice_do_aliado(aliado_sel)
        if parametros.get("MovimentoSelecionado") is None:
            parametros["MovimentoSelecionado"] = atk_sel

    def _checar_finalizacao():
        if mov_especial == 1:
            qtd = 1
        elif mov_especial == 2:
            qtd = 1
        else:
            qtd = max(1, int(alvo_info.get('qtd', 1)))
        if len(parametros["AlvosSelecionados"]) >= qtd:
            parametros["__alvo_finalizado_ok"] = True
            parametros["__ja_limpei_estado"] = True
            parametros["ModoAlvificando"] = False
            slots_high["A"].clear()
            slots_high["I"].clear()

    # ======== Aliados (esquerda) ========
    for i, rect in enumerate(_slots_esquerda):
        poke = next((p for p in parametros.get("AliadosAtivos", []) if p.get("Pos") == i + 1), None)
        rect_anim = rect.move(dx_esq, 0)
        slots_rects["A"][i] = rect_anim.copy()

        if modo_alvo:
            pisc = (i in highlight_A)
            Botao_Selecao(
                tela=tela, texto="", espaço=rect_anim, Fonte=fonte,
                cor_fundo=_slot_skin_aliado, cor_borda_normal=(cor_amarelo if pisc else (0, 0, 0)),
                cor_borda_esquerda=None, cor_borda_direita=None, cor_passagem=None,
                id_botao=f"ali-{i}",
                estado_global=EstadoArenaFalso, eventos=None,
                funcao_esquerdo=None, desfazer_esquerdo=None,
                Piscante=pisc
            )
            if pisc:
                if mov_especial == 1:
                    def _acao_A_move(ii=i):
                        _add_code_single('A', ii)
                        _apos_primeiro_alvo()
                        _checar_finalizacao()
                    Botao_invisivel(rect_anim, _wrap_energy_guard(_acao_A_move, parametros))
                elif alvo_info['tipo'] == 'linha':
                    def _acao_A_linha(ii=i):
                        _add_codes_line('A', ii)
                        _apos_primeiro_alvo()
                        _checar_finalizacao()
                    Botao_invisivel(rect_anim, _wrap_energy_guard(_acao_A_linha, parametros))
                elif alvo_info['tipo'] == 'celula':
                    def _acao_A_cel(ii=i):
                        _add_code_single('A', ii)
                        _apos_primeiro_alvo()
                        _checar_finalizacao()
                    Botao_invisivel(rect_anim, _wrap_energy_guard(_acao_A_cel, parametros))
        else:
            # modo normal: seleção/deseleção COM animação do painel aliado
            func_esq_ali = [
                (lambda p=poke: parametros.update({"AliadoSelecionado": p})),
                (lambda a=anima: a.update({
                    "_anima_painel_aliado": pygame.time.get_ticks(),
                    "Y1": 1080,  # de onde sai
                    "Y2": 895,   # alvo (par)
                })),
            ]
            desf_esq_ali = [
                (lambda: parametros.update({"AliadoSelecionado": None})),
                (lambda a=anima: a.update({
                    "_anima_painel_aliado": pygame.time.get_ticks(),
                    "Y1": 895,   # de onde sai
                    "Y2": 1080,  # alvo (par)
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
        slots_rects["I"][i] = rect_anim.copy()

        if modo_alvo:
            pisc = (i in highlight_I)
            Botao_Selecao(
                tela=tela, texto="", espaço=rect_anim, Fonte=fonte,
                cor_fundo=_slot_skin_inimigo, cor_borda_normal=(cor_amarelo if pisc else (0, 0, 0)),
                cor_borda_esquerda=None, cor_borda_direita=None, cor_passagem=None,
                id_botao=f"ini-{i}",
                estado_global=EstadoArenaFalso, eventos=None,
                funcao_esquerdo=None, desfazer_esquerdo=None,
                Piscante=pisc
            )
            if pisc and mov_especial != 1:
                if alvo_info['tipo'] == 'linha':
                    def _acao_I_linha(ii=i):
                        _add_codes_line('I', ii)
                        _apos_primeiro_alvo()
                        _checar_finalizacao()
                    Botao_invisivel(rect_anim, _wrap_energy_guard(_acao_I_linha, parametros))
                elif alvo_info['tipo'] == 'celula':
                    def _acao_I_cel(ii=i):
                        _add_code_single('I', ii)
                        _apos_primeiro_alvo()
                        _checar_finalizacao()
                    Botao_invisivel(rect_anim, _wrap_energy_guard(_acao_I_cel, parametros))
        else:
            # modo normal: seleção/deseleção COM animação do painel inimigo
            func_esq_ini = [
                (lambda p=poke: parametros.update({"InimigoSelecionado": p})),
                (lambda a=anima: a.update({
                    "_anima_painel_inimigo": pygame.time.get_ticks(),
                    "Y3": -200,  # de onde sai
                    "Y4": 0,     # alvo (par)
                })),
            ]
            desf_esq_ini = [
                (lambda: parametros.update({"InimigoSelecionado": None})),
                (lambda a=anima: a.update({
                    "_anima_painel_inimigo": pygame.time.get_ticks(),
                    "Y3": 0,     # de onde sai
                    "Y4": -200,  # alvo (par)
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

    # ---------- helpers locais ----------
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

    # controle de alvo/estado
    modo_alvo = bool(parametros.get("ModoAlvificando"))
    atk_sel   = parametros.get("AtaqueAliadoSelecionado")
    troca_ativa = (atk_sel == 2)

    # para finalizar igual Arena quando clica no alvo de troca
    def _finaliza_alvo_reserva():
        parametros["__alvo_finalizado_ok"] = True
        parametros["__ja_limpei_estado"]   = True
        parametros["ModoAlvificando"]      = False

    def _indice_do_aliado(aliado_dict):
        equipe = parametros.get("EquipeAliada") or []
        try:
            pos = int(aliado_dict.get("Pos", -1))
            for i, p in enumerate(equipe):
                if int(p.get("Pos", -2)) == pos:
                    return i
        except Exception:
            pass
        for i, p in enumerate(equipe):
            if p is aliado_dict or p == aliado_dict:
                return i
        return None

    # ======== GRUPO ALIADOS (inferior esquerdo) ========
    base_ax = 0
    base_ay = SH - BTN
    rects_a = [
        (base_ax + BTN * 0, base_ay, BTN, BTN),  # Fugir (normal)
        (base_ax + BTN * 1, base_ay, BTN, BTN),  # Reserva A0
        (base_ax + BTN * 2, base_ay, BTN, BTN),  # Reserva A1
        (base_ax + BTN * 3, base_ay, BTN, BTN),  # Reserva A2
    ]

    # 0) Fugir — BOTAO (normal)
    Botao(
        tela, "", rects_a[0],
        cor_normal=(200, 200, 200), cor_borda=(0, 0, 0), cor_passagem=(255, 255, 255),
        acao=lambda: parametros.__setitem__("Fuga", parametros.get("Fuga", 0) + 10),
        Fonte=fonte, estado_clique=estado_clique, eventos=eventos,
        grossura=BORDER, cor_texto=(0, 0, 0)
    )
    ic_fugir = Icones.get("fugir")
    _blit_center_scaled(rects_a[0], ic_fugir, pad=6)

    # 1..3) Reservas Aliadas
    for i in range(3):
        r = rects_a[i + 1]
        tem_poke = i < len(reserva_a)
        pisc = (modo_alvo and troca_ativa and tem_poke)  # só Troca, só aliados

        if modo_alvo and troca_ativa:
            # igual Arena: botão falso + piscância + invisível com guarda de energia
            Botao_Selecao(
                tela=tela, texto=("-" if not tem_poke else ""), espaço=r, Fonte=fonte,
                cor_fundo=(200, 200, 200),
                cor_borda_normal=(Cores["amarelo"] if pisc else (0, 0, 0)),
                cor_passagem=None, grossura=BORDER,
                id_botao=f"resA-{i}",
                estado_global=EstadoArenaFalso, eventos=None,
                Piscante=pisc
            )
            if tem_poke and pisc:
                def _acao_resA(ii=i):
                    alvos = parametros.setdefault("AlvosSelecionados", [])
                    code = f"RA{ii+1}"  # reserva aliada
                    if code not in alvos:
                        alvos.append(code)

                    # setar atacante e movimento (mesma lógica da Arena)
                    if parametros.get("MovimentoSelecionado") is None:
                        parametros["MovimentoSelecionado"] = 2
                    ali = parametros.get("AliadoSelecionado")
                    if ali is not None and parametros.get("AtacanteSelecionado") is None:
                        idx = _indice_do_aliado(ali)
                        if idx is not None:
                            parametros["AtacanteSelecionado"] = idx

                    _finaliza_alvo_reserva()

                Botao_invisivel(r, _wrap_energy_guard(_acao_resA, parametros))

        else:
            # modo normal: usa AliadoSelecionado (sem var reserva separada) + anima igual Arena
            selecionado = (parametros.get("AliadoSelecionado") is reserva_a[i]) if tem_poke else False
            cor_borda = (Cores["azul"] if selecionado else (0, 0, 0))

            def _seleciona_resA(ii=i):
                if ii >= len(reserva_a):
                    return
                atual = parametros.get("AliadoSelecionado")
                novo  = reserva_a[ii]
                if atual is novo:
                    # desseleciona + anima saída
                    parametros["AliadoSelecionado"] = None
                    anima.update({
                        "_anima_painel_aliado": pygame.time.get_ticks(),
                        "Y1": 895,   # onde está
                        "Y2": 1080,  # sai
                    })
                else:
                    # seleciona + anima entrada
                    parametros["AliadoSelecionado"] = novo
                    anima.update({
                        "_anima_painel_aliado": pygame.time.get_ticks(),
                        "Y1": 1080,  # entra de baixo
                        "Y2": 895,   # alvo
                    })

            Botao_Selecao(
                tela=tela, texto=("-" if not tem_poke else ""), espaço=r, Fonte=fonte,
                cor_fundo=(200, 200, 200), cor_borda_normal=cor_borda,
                cor_passagem=(255, 255, 255), grossura=BORDER,
                id_botao=f"resA-{i}",
                eventos=eventos, estado_global=EstadoArenaBotoesAliado,
                funcao_esquerdo=[_wrap_energy_guard(_seleciona_resA, parametros)],  # guarda de energia tb aqui
                desfazer_esquerdo=None
            )

        if tem_poke:
            nome_key = reserva_a[i].get("Nome", "")
            spr = _sprite_por_nome(nome_key)
            _blit_center_scaled(r, spr, pad=4)

    # ======== GRUPO INIMIGOS (superior direito) ========
    base_ix = SW - BTN * 4
    base_iy = 0
    rects_i = [
        (base_ix + BTN * 0, base_iy, BTN, BTN),  # Inimigo reserva(?) 0 (visual idêntico)
        (base_ix + BTN * 1, base_iy, BTN, BTN),  # Inimigo reserva 1
        (base_ix + BTN * 2, base_iy, BTN, BTN),  # Inimigo reserva 2
        (base_ix + BTN * 3, base_iy, BTN, BTN),  # Trégua (normal)
    ]

    # 0..2) Seleções inimigos — MODO NORMAL apenas (você pediu destaque só nas aliadas)
    for i in range(3):
        r = rects_i[i]
        tem_poke = i < len(reserva_i)

        # usar InimigoSelecionado (sem “reserva” separado) + anima igual Arena
        selecionado = (parametros.get("InimigoSelecionado") is reserva_i[i]) if tem_poke else False
        cor_borda = (Cores["vermelho"] if selecionado else (0, 0, 0))

        def _seleciona_resI(ii=i):
            if ii >= len(reserva_i):
                return
            atual = parametros.get("InimigoSelecionado")
            novo  = reserva_i[ii]
            if atual is novo:
                # desseleciona + anima saída inimigo
                parametros["InimigoSelecionado"] = None
                anima.update({
                    "_anima_painel_inimigo": pygame.time.get_ticks(),
                    "Y3": 0,     # onde está
                    "Y4": -200,  # sai para cima
                })
            else:
                # seleciona + anima entrada inimigo
                parametros["InimigoSelecionado"] = novo
                anima.update({
                    "_anima_painel_inimigo": pygame.time.get_ticks(),
                    "Y3": -200,  # entra de cima
                    "Y4": 0,     # alvo
                })

        # quando Troca ativa, NÃO há destaque em inimigos e continuam clicáveis normais
        Botao_Selecao(
            tela=tela, texto=("-" if not tem_poke else ""), espaço=r, Fonte=fonte,
            cor_fundo=(200, 200, 200), cor_borda_normal=cor_borda,
            cor_passagem=(255, 255, 255), grossura=BORDER,
            id_botao=f"resI-{i}",
            eventos=eventos, estado_global=EstadoArenaBotoesInimigo,
            funcao_esquerdo=[_wrap_energy_guard(_seleciona_resI, parametros)],
            desfazer_esquerdo=None
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

def TelaAlvoBatalha(tela, estados, eventos, parametros):

    # ===== helpers gerais =====
    def _slot_center(lado, idx1based):
        """Retorna (cx,cy) do centro da casa lado 'A'/'I' índice 1..9. Usa parametros['SlotsRects']"""
        slots = parametros.get("SlotsRects", {})
        arr = slots.get(lado) or []
        i0 = max(1, min(9, int(idx1based))) - 1
        if 0 <= i0 < len(arr) and isinstance(arr[i0], pygame.Rect):
            r = arr[i0]
            return (r.centerx, r.centery)
        return None

    def _mouse_over_highlight():
        """Se mouse está sobre um slot destacado, retorna ('A'|'I', idx1based, (cx,cy)); senão None."""
        mx, my = pygame.mouse.get_pos()
        slots = parametros.get("SlotsRects", {})
        hi    = parametros.get("SlotsDestaque", {"A": set(), "I": set()})
        for lado in ("A", "I"):
            arr = slots.get(lado) or []
            for i0, r in enumerate(arr):
                if i0 in (hi.get(lado) or set()) and isinstance(r, pygame.Rect) and r.collidepoint(mx, my):
                    return lado, (i0 + 1), (r.centerx, r.centery)
        return None

    def _cor_por_mov(mov):
        """Define cor conforme estilo/tipo de movimento."""
        # Mapas de cor
        ROXO   = (160, 90, 255)
        LARAN  = (255, 150, 40)
        AZUL   = (60, 160, 255)
        VERDE  = (70, 220, 120)
        ROSA   = (255, 110, 200)

        if isinstance(mov, int):
            if mov == 1:  # mover
                return VERDE
            if mov == 2:  # trocar (R) — não usamos alvos R agora, mas cor reservada
                return ROSA
            return (255,255,255)

        if isinstance(mov, dict):
            est = (mov.get("Estilo") or mov.get("estilo") or "").strip().lower()
            if est == "e":  # especial
                return ROXO
            if est == "n":  # normal/físico (pela sua nomenclatura)
                return LARAN
            if est == "s":  # suporte/status
                return AZUL
        # fallback
        return (255,255,255)

    def _parse_code(code):
        """'A4' -> ('A', 4). Retorna None se inválido."""
        if not code or not isinstance(code, str):
            return None
        code = code.strip().upper()
        if len(code) < 2:
            return None
        lado = code[0]
        try:
            idx = int(code[1:])
        except ValueError:
            return None
        if lado not in ("A", "I"):
            return None
        if not (1 <= idx <= 9):
            return None
        return lado, idx

    def _ponto_do_atacante(atacante_idx):
        """atacante_idx é índice na EquipeAliada (0..n-1) -> pega 'Pos' e devolve centro do slot aliado."""
        equipe = parametros.get("EquipeAliada") or []
        if atacante_idx is None or not (0 <= int(atacante_idx) < len(equipe)):
            return None
        poke = equipe[int(atacante_idx)]
        pos  = int(poke.get("Pos", 1))
        return _slot_center("A", pos)

    def _desenha_fluxo(x1, y1, x2, y2, cor, translucido=False, raio=5):
        Fluxo(
            tela, x1, y1, x2, y2,
            Pontos=40, pontos_por_100px=8,
            frequencia=4, velocidade=3,
            cor_base=cor, raio=raio, forma="seta",
            translucido=translucido
        )

    # ===== 1) FluxoAlvificando =====
    def FluxoAlvificando():
        if not parametros.get("ModoAlvificando"):
            return
        aliado_sel = parametros.get("AliadoSelecionado")
        if not aliado_sel:
            return

        # ponto de origem: centro do slot do aliado selecionado (usa Pos dele)
        try:
            pos_ali = int(aliado_sel.get("Pos", 1))
        except Exception:
            pos_ali = 1
        origem = _slot_center("A", pos_ali)
        if not origem:
            return

        # destino: mouse; se sobre slot destacado, 'gruda' no centro do slot destacado
        mx, my = pygame.mouse.get_pos()
        alvo_hover = _mouse_over_highlight()
        if alvo_hover:
            _, _, (cx, cy) = alvo_hover
            dest = (cx, cy)
        else:
            dest = (mx, my)

        # --- checa energia ---
        ene = int(aliado_sel.get("Energia", aliado_sel.get("EneAtual", 0)) or 0)
        custo = int(parametros.get("CustoAtualEnergia", 0) or 0)
        if (ene - custo) < -5:
            cor_fluxo = (255, 80, 80)   # vermelho (bloqueado)
        else:
            cor_fluxo = (255, 210, 80)  # amarelo (em construção normal)

        _desenha_fluxo(origem[0], origem[1], dest[0], dest[1],
                    cor_fluxo, translucido=False, raio=6)

    # ===== 2) FluxosAtuais =====
    def FluxosAtuais():
        atacante_idx = parametros.get("AtacanteSelecionado")
        alvos = parametros.get("AlvosSelecionados") or []
        if atacante_idx is None or not alvos:
            return

        origem = _ponto_do_atacante(atacante_idx)
        if not origem:
            return

        mov = parametros.get("MovimentoSelecionado")
        cor = _cor_por_mov(mov)

        for code in alvos:
            parsed = _parse_code(code)
            if not parsed:
                continue
            lado, idx = parsed
            destino = _slot_center(lado, idx)
            if not destino:
                continue
            _desenha_fluxo(origem[0], origem[1], destino[0], destino[1], cor, translucido=False, raio=6)

    # ===== 3) FluxosLog =====
    def FluxosLog():
        logs = parametros.get("LogAtual") or []
        if not isinstance(logs, list) or not logs:
            return

        # alpha bem baixo para “fantasma”
        alpha_soft = 50  # ~quase invisível

        for item in logs:
            if not isinstance(item, dict):
                continue
            atacante_idx = item.get("Atacante")
            origem = _ponto_do_atacante(atacante_idx)
            if not origem:
                continue

            mov = item.get("Movimento")
            cor = _cor_por_mov(mov)
            alvos = item.get("Alvos") or []

            for code in alvos:
                parsed = _parse_code(code)
                if not parsed:
                    continue
                lado, idx = parsed
                destino = _slot_center(lado, idx)
                if not destino:
                    continue
                _desenha_fluxo(
                    origem[0], origem[1], destino[0], destino[1],
                    cor, translucido=alpha_soft, raio=5
                )

    # ==== chamada das três etapas ====
    FluxoAlvificando()
    FluxosAtuais()
    FluxosLog()

# ==================== FUNDO/GRIDS/POKÉMONS (SEM CÂMERA) ====================
def TelaFundoBatalha(tela, estados, eventos, parametros):
    global _slots_esquerda, _slots_direita, _anim_inimigos, _anim_aliados
    global _slot_skin_aliado, _slot_skin_inimigo, _anima_t0

    sw, sh = tela.get_size()

    # Layout fixo em tela
    margem = 280
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

    TelaAlvoBatalha(tela, estados, eventos, parametros)


    DesenharPlayer(tela,Player.Skin,(50,850),nome=Player.Nome,Fonte=Fontes[18])

    if not parametros["BatalhaSimples"]:
        pass

    # atualiza posição por frame (deslocamento horizontal)
    for anim_obj, (cx, cy) in _anim_inimigos:
        anim_obj.atualizar(tela, nova_pos=(int(cx + dx_dir), int(cy)), multiplicador=1.0)
    for anim_obj, (cx, cy) in _anim_aliados:
        anim_obj.atualizar(tela, nova_pos=(int(cx + dx_esq), int(cy)), multiplicador=1.0)

def BatalhaTelaOpçoes(tela, estados, eventos, parametros):

    if parametros["TelaConfigurações"]["Entrou"]:
        if pygame.mouse.get_pressed()[0]:
            return
        else:
            parametros["TelaConfigurações"]["Entrou"] = False

    Botao(
        tela, "Voltar", (710, 300, 500, 150), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": BatalhaTelaPadrao}),
        Fontes[40], BG, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    Botao(
        tela, "Configurações", (710, 500, 500, 150), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": TelaConfigurações, "TelaConfigurações": {"Voltar":lambda: parametros.update({"Tela": BatalhaTelaOpçoes}), "Entrou": True}}),
        Fontes[40], BG, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    Botao(
        tela, "Salvar e Sair", (710, 700, 500, 150), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: [SalvarConta(parametros), SairConta(parametros), estados.update({"Mundo": False, "Inicio": True})],
        Fontes[40], BG, eventos, som="Clique", cor_texto=Cores["branco"]
    )

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

    if Conteudo is not None and atk and Conteudo not in [1,2]:
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
    
    if parametros["AlvosSelecionados"] is not [] and parametros["AtacanteSelecionado"] is not None and parametros["MovimentoSelecionado"] is not None:
        Botao(tela, "Preparar", (1660,960,260,60),Texturas["vermelho"],(0,0,0),(240,240,240),
              [lambda: parametros["LogAtual"].append({"Atacante": parametros["AtacanteSelecionado"], "Movimento": parametros["MovimentoSelecionado"], "Alvos": parametros["AlvosSelecionados"]}),
               lambda: parametros.update({ "AtaqueAliadoSelecionado": None, "AlvosSelecionados": [],
            "AtacanteSelecionado": None, "MovimentoSelecionado": None, "EstadoBotoesPainelPokemonBatalha": {}, "ModoAlvificando": False}),
            anima.update({"_anima_painel_acao": pygame.time.get_ticks()})], 
              Fontes[35], BG, eventos)
    else:
        Botao(tela, "Preparar", (1660,960,260,60),Cores["cinza"],(0,0,0),(240,240,240),lambda: tocar("Bloq"), Fontes[35], BG, eventos)
    
    Desenhar_Botoes_Combate(tela,parametros)

    for i, acao in enumerate(parametros["LogAtual"]):
        if len(Acao_surface_cache) <= i:
            Acao_surface_cache.append(PainelAcao(acao, parametros))

        x = Animar(anima["X1"], anima["X2"], anima["_anima_painel_acao"]) if i == len(parametros["LogAtual"]) - 1 else 40
        y = 250 + i * 90

        tela.blit(Acao_surface_cache[i], (x, y))

        # título do cabeçalho
        txt = Fontes[16].render(f"Ação {i+1}", True, (20, 20, 20))
        tela.blit(txt, (x+6, y + (24 - txt.get_height())//2))

        # botão remover
        Botao(tela, "X", (x+128, y+2, 20, 20), Cores["vermelho"], (0,0,0), (240,240,240),
            [lambda: (parametros["LogAtual"].pop(i), Acao_surface_cache.pop(i))],
            Fontes[10], BG, eventos)

def BatalhaTelaPadrao(tela, estados, eventos, parametros):

    TelaFundoBatalha(tela, estados, eventos, parametros)
    TelaHudBatalha(tela, estados, eventos, parametros)

    Botao_Tecla("esc",lambda: parametros.update({"Tela": BatalhaTelaOpçoes}))

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
            "Tela": BatalhaTelaPadrao,
            "EquipeInimiga": [GeraPokemonBatalha(p) for p in GerarMatilha(parametros["AlvoConfronto"].Dados, Membros)],
            "EquipeAliada":  [GeraPokemonBatalha(p) for p in Equipe],
            "AliadoSelecionado": None,
            "InimigoSelecionado": None,
            "AtaqueAliadoSelecionado": None,
            "AtaqueInimigoSelecionado": None,
            "ItemSelecionado": None,
            "ModoAlvificando": False,
            "Pronto": False,
            "Fuga": 0,
            "AlvosSelecionados": [],
            "AtacanteSelecionado": None,
            "MovimentoSelecionado": None,
            "CustoAtualEnergia": 0,
            "LogAtual": [],
            "EstadoBotoesPainelPokemonBatalha": {},
            "TelaConfigurações": {"Entrou": False},
            "Config": config,
        })
        parametros["AliadosAtivos"]  = definir_ativos(parametros["EquipeAliada"])
        parametros["InimigosAtivos"] = definir_ativos(parametros["EquipeInimiga"])

    # --- antes do loop: taxa de decaimento (1 a cada 0,05s = 20/s)
    DECAY_PER_SEC = 20.0

    # inicializa o float a partir do inteiro (se existir)
    FugaFloat = float(parametros.get("Fuga", 0))
    parametros["Fuga"] = int(round(FugaFloat))

    while estados["Batalha"]:
        dt = relogio.get_time() / 1000.0

        # sincroniza aumentos externos (ex.: clique no botão "Fugir" somou só no inteiro)
        fuga_int = int(parametros.get("Fuga", 0))
        if fuga_int > int(round(FugaFloat)):
            FugaFloat = float(min(100, fuga_int))  # clamp opcional

        # decair Fuga gradativamente por dt (sem bloquear o loop)
        if FugaFloat > 0.0:
            FugaFloat = max(0.0, FugaFloat - DECAY_PER_SEC * dt)
            # espelha o float de volta para o inteiro usado na UI
            parametros["Fuga"] = int(round(FugaFloat))
            parametros["FugaFloat"] = FugaFloat  # útil para debug/overlay

        # se Fuga atingir 100, encerrar batalha e voltar ao Mundo
        if FugaFloat >= 95.0 or parametros["Fuga"] >= 95:
            estados["Batalha"] = False
            estados["Mundo"] = True
            info["AcabouDeSairConfronto"] = True
            break

        tela.blit(Fundos["FundoBatalha"], (0, 0))
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Batalha"] = False
                estados["Rodando"] = False

        parametros["Tela"](tela, estados, eventos, parametros)

        # filtro preto proporcional à Fuga (usa o inteiro espelhado)
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

