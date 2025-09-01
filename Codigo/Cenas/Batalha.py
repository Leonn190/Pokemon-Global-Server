import pygame, random, time, re

from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Modulos.Paineis import PainelPokemonBatalha, CriarSurfacePainelAtaque, PainelAcao, PAINEL_ATAQUE_CACHE
from Codigo.Prefabs.BotoesPrefab import Botao_Selecao, Botao, Botao_invisivel, Botao_Tecla
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda, Animar, caixa_de_texto, Fluxo, Pulso
from Codigo.Prefabs.Animações import Animação
from Codigo.Prefabs.Sonoridade import Musica, AtualizarMusica, tocar
from Codigo.Geradores.GeradorPokemon import GerarMatilha, CarregarAnimacaoPokemon, GeraPokemonBatalha, CarregarPokemon
from Codigo.Modulos.Config import TelaConfigurações
from Codigo.Modulos.DesenhoPlayer import DesenharPlayer
from Codigo.Server.ServerMundo import SairConta, SalvarConta
# from Codigo.Localidades.EstabilizadorBatalhaLocal import IniciarBatalhaLocal

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
_anima_dur_ms = 460
anima = {
    "_anima_painel_aliado": None,
    "_anima_painel_inimigo": None,
    "_anima_painel_conteudo": None,
    "Y1": 900, "Y2": 1080,
    "Y3": -200, "Y4": 0,
    "Y5": 895, "Y6": 1080,

    "_anima_painel_acao": None,
    "X1": -155, "X2": 40,
}

Acao_surface_cache = []
AliadoSelecionadoCache = None
InimigoSelecionadoCache = None

# ======== ESTADOS GLOBAIS ========
EstadoEditorLog = {}            # estados genéricos (hover/click, etc. — se precisar)
EstadoBotoesAcao = {}           # estados por botão principal (seleção de ação)
EstadoBotoesApagar = {}         # estados por botão X (apagar ação)

def Transformador(acao):
    if acao["Movimento"] == 1:
        acao["Movimento"] = "Mover"
        acao["Alvos"].remove["A"]
        int(acao["Alvos"])
    elif acao["Movimento"] == 2:
        acao["Movimento"] = "Trocar"
        acao["Alvos"].remove["RA"]
        int(acao["Alvos"])
    else:
        acao["Movimento"] = acao["Movimento"]["nome"]

def VerificaçãoCombate(parametros):
    if parametros.get("BatalhaSimples"):
        if parametros.get("Pronto"):
            for acao in parametros["LogAtual"]:
                Transformador(acao)

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


def Desenhar_Botoes_Combate(tela, parametros, eventos):
    BTN = 70
    BORDER = 3
    SW, SH = 1920, 1080

    fonte = Fontes[30]
    estado_clique = parametros.setdefault("EstadoBotoesCombateSimples", {})

    # ===== helpers =====
    def _blit_center_scaled(rect_tuple, surf, pad=6):
        if not surf or not hasattr(surf, "get_size"):
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
        key = str(nome_key).lower()
        spr = Pokemons.get(key)
        if spr is None:
            spr = CarregarPokemon(key, Pokemons)
        return spr

    def _indice_do_aliado(aliado_dict):
        equipe = parametros.get("EquipeAliada") or []
        try:
            pos = int(aliado_dict.get("Pos", -1))
            for i, p in enumerate(equipe):
                if p and int(p.get("Pos", -2)) == pos:
                    return i
        except Exception:
            pass
        for i, p in enumerate(equipe):
            if p is aliado_dict or p == aliado_dict:
                return i
        return None

    def _finaliza_alvo_reserva():
        parametros["__alvo_finalizado_ok"] = True
        parametros["__ja_limpei_estado"] = True
        parametros["ModoAlvificando"] = False

    # ===== preparar SlotsRects / SlotsDestaque para magnetismo das reservas =====
    slots_rects = parametros.setdefault("SlotsRects", {"A": [None]*9, "I": [None]*9})
    slots_high  = parametros.setdefault("SlotsDestaque", {"A": set(), "I": set()})
    # garante espaço para 3 reservas após os 9 slots (índices 9,10,11)
    for lado in ("A", "I"):
        arr = slots_rects.get(lado)
        if not isinstance(arr, list):
            slots_rects[lado] = [None]*9
        if len(slots_rects[lado]) < 12:
            slots_rects[lado].extend([None] * (12 - len(slots_rects[lado])))
    # limpa highlights antigos de reserva (≥9), preservando 0..8 da arena
    slots_high["A"] = set(idx for idx in (slots_high.get("A") or set()) if idx < 9)
    slots_high["I"] = set(idx for idx in (slots_high.get("I") or set()) if idx < 9)
    # zera rects de reserva (serão reescritos abaixo)
    for j in range(9, 12):
        slots_rects["A"][j] = None
        slots_rects["I"][j] = None

    # ===== dados (filtrando None) =====
    equipe_a_raw = (parametros.get("EquipeAliada") or [])
    equipe_i_raw = (parametros.get("EquipeInimiga") or parametros.get("EquipeInimigos") or [])
    equipe_a = [p for p in equipe_a_raw if p is not None]
    equipe_i = [p for p in equipe_i_raw if p is not None]

    # reservas = itens válidos e não ativos
    reserva_a = [p for p in equipe_a if not p.get("Ativo", True)]
    reserva_i = [p for p in equipe_i if not p.get("Ativo", True)]

    parametros.setdefault("AlvosSelecionados", [])

    modo_alvo  = bool(parametros.get("ModoAlvificando"))
    aliado_sel = parametros.get("AliadoSelecionado")
    atk_sel    = parametros.get("AtaqueAliadoSelecionado")
    troca_ativa = (atk_sel == 2)

    cor_amarelo = Cores["amarelo"]

    # ===== ALIADOS (baixo) =====
    base_ax = 0
    base_ay = SH - BTN
    rects_a = [
        (base_ax + BTN * 0, base_ay, BTN, BTN),  # Fugir
        (base_ax + BTN * 1, base_ay, BTN, BTN),  # Reserva A0
        (base_ax + BTN * 2, base_ay, BTN, BTN),  # Reserva A1
        (base_ax + BTN * 3, base_ay, BTN, BTN),  # Reserva A2
    ]

    # Fugir (sempre botão simples)
    Botao(
        tela, "", rects_a[0],
        cor_normal=(200, 200, 200), cor_borda=(0, 0, 0), cor_passagem=(255, 255, 255),
        acao=lambda: parametros.__setitem__("Fuga", parametros.get("Fuga", 0) + 10),
        Fonte=fonte, estado_clique=estado_clique, eventos=eventos,
        grossura=BORDER, cor_texto=(0, 0, 0)
    )
    ic_fugir = Icones.get("fugir")
    _blit_center_scaled(rects_a[0], ic_fugir, pad=6)

    # Reservas Aliadas
    for i in range(3):
        r = rects_a[i + 1]
        tem_poke = i < len(reserva_a)

        # MAGNETISMO: salva o Rect da reserva A em SlotsRects["A"][9+i]
        rect_obj_a = pygame.Rect(r)
        slots_rects["A"][9 + i] = rect_obj_a
        # se estiver em alvo+troca e há poke, marca highlight (9..11)
        if modo_alvo and troca_ativa and tem_poke:
            slots_high["A"].add(9 + i)

        if modo_alvo:
            # Seleção falso; destaque só se Troca(2) e existe poke.
            pisc = tem_poke and troca_ativa
            Botao_Selecao(
                tela=tela, texto=("-" if not tem_poke else ""), espaço=r, Fonte=fonte,
                cor_fundo=(200, 200, 200),
                cor_borda_normal=(cor_amarelo if pisc else (0, 0, 0)),
                cor_borda_esquerda=None, cor_borda_direita=None,
                cor_passagem=None, grossura=BORDER,
                id_botao=f"resA-{i}",
                estado_global=EstadoArenaFalso, eventos=None,
                Piscante=pisc
            )
            if tem_poke and pisc:
                def _acao_resA(ii=i):
                    alvos = parametros["AlvosSelecionados"]
                    code = f"RA{ii+1}"
                    if code not in alvos:
                        alvos.append(code)
                    if parametros.get("MovimentoSelecionado") is None:
                        parametros["MovimentoSelecionado"] = 2
                    if parametros.get("AtacanteSelecionado") is None and aliado_sel:
                        idx = _indice_do_aliado(aliado_sel)
                        if idx is not None:
                            parametros["AtacanteSelecionado"] = idx
                    _finaliza_alvo_reserva()
                Botao_invisivel(r, _wrap_energy_guard(_acao_resA, parametros))

        else:
            # Seleção normal + anima (listas de lambdas; sem helpers)
            selecionado = (tem_poke and (parametros.get("AliadoSelecionado") is reserva_a[i]))
            cor_borda = (Cores["azul"] if selecionado else (0, 0, 0))

            func_esq = None
            desf_esq = None
            if tem_poke:
                func_esq = [
                    (lambda ii=i: parametros.update({"AliadoSelecionado": reserva_a[ii]})),
                    (lambda a=anima: a.update({
                        "_anima_painel_aliado": pygame.time.get_ticks(),
                        "Y1": 1080,
                        "Y2": 895,
                    })),
                ]
                desf_esq = [
                    lambda: parametros.update({"AliadoSelecionado": None}),
                    lambda a=anima: a.update({
                        "_anima_painel_aliado": pygame.time.get_ticks(),
                        "Y1": 895,
                        "Y2": 1080,
                    })]

            Botao_Selecao(
                tela=tela, texto=("-" if not tem_poke else ""), espaço=r, Fonte=fonte,
                cor_fundo=(200, 200, 200), cor_borda_normal=cor_borda,
                cor_borda_esquerda=Cores["azul"],
                cor_borda_direita=None,
                cor_passagem=(255, 255, 255), grossura=BORDER,
                id_botao=f"resA-{i}",
                eventos=eventos, estado_global=EstadoArenaBotoesAliado,
                funcao_esquerdo=func_esq,
                desfazer_esquerdo=desf_esq
            )

        if tem_poke:
            spr = _sprite_por_nome(reserva_a[i].get("Nome", ""))
            _blit_center_scaled(r, spr, pad=4)

    # ===== INIMIGOS (topo) =====
    base_ix = SW - BTN * 4
    base_iy = 0
    rects_i = [
        (base_ix + BTN * 0, base_iy, BTN, BTN),
        (base_ix + BTN * 1, base_iy, BTN, BTN),
        (base_ix + BTN * 2, base_iy, BTN, BTN),
        (base_ix + BTN * 3, base_iy, BTN, BTN),  # Trégua
    ]

    for i in range(3):
        r = rects_i[i]
        tem_poke = i < len(reserva_i)

        # MAGNETISMO: salva o Rect da reserva I em SlotsRects["I"][9+i]
        rect_obj_i = pygame.Rect(r)
        slots_rects["I"][9 + i] = rect_obj_i
        # (sem highlight para inimigos na Troca)

        if modo_alvo:
            Botao_Selecao(
                tela=tela, texto=("-" if not tem_poke else ""), espaço=r, Fonte=fonte,
                cor_fundo=(200, 200, 200), cor_borda_normal=(0, 0, 0),
                cor_borda_esquerda=None, cor_borda_direita=None,
                cor_passagem=None, grossura=BORDER,
                id_botao=f"resI-{i}",
                estado_global=EstadoArenaFalso, eventos=None,
                Piscante=False
            )
        else:
            selecionado = (tem_poke and (parametros.get("InimigoSelecionado") is reserva_i[i]))
            cor_borda = (Cores["vermelho"] if selecionado else (0, 0, 0))

            func_esq = None
            desf_esq = None
            if tem_poke:
                func_esq = [
                    (lambda ii=i: parametros.__setitem__("InimigoSelecionado", reserva_i[ii])),
                    (lambda a=anima: a.update({
                        "_anima_painel_inimigo": pygame.time.get_ticks(),
                        "Y3": -200,
                        "Y4": 0,
                    })),
                ]
                desf_esq = [
                    (lambda: parametros.__setitem__("InimigoSelecionado", None)),
                    (lambda a=anima: a.update({
                        "_anima_painel_inimigo": pygame.time.get_ticks(),
                        "Y3": 0,
                        "Y4": -200,
                    })),
                ]

            Botao_Selecao(
                tela=tela, texto=("-" if not tem_poke else ""), espaço=r, Fonte=fonte,
                cor_fundo=(200, 200, 200), cor_borda_normal=cor_borda,
                cor_borda_esquerda=Cores["vermelho"],
                cor_borda_direita=None,
                cor_passagem=(255, 255, 255), grossura=BORDER,
                id_botao=f"resI-{i}",
                eventos=eventos, estado_global=EstadoArenaBotoesInimigo,
                funcao_esquerdo=func_esq,
                desfazer_esquerdo=desf_esq
            )

        if tem_poke:
            spr = _sprite_por_nome(reserva_i[i].get("Nome", ""))
            _blit_center_scaled(r, spr, pad=4)

    # Trégua
    Botao(
        tela, "", rects_i[3],
        cor_normal=(200, 200, 200), cor_borda=(0, 0, 0), cor_passagem=(255, 255, 255),
        acao=(lambda: None), Fonte=fonte, estado_clique=estado_clique, eventos=eventos,
        grossura=BORDER, cor_texto=(0, 0, 0)
    )
    ic_tregua = Icones.get("tregua")
    _blit_center_scaled(rects_i[3], ic_tregua, pad=6)

def Arenas(tela, parametros, Fontes, eventos, dx_esq, dx_dir):
    fonte = Fontes[16]
    modo_alvo = bool(parametros.get("ModoAlvificando"))  # será re-sincronizado após reset

    aliado_sel = parametros.get("AliadoSelecionado")
    atk_sel    = parametros.get("AtaqueAliadoSelecionado")

    slots_rects = parametros.setdefault("SlotsRects", {"A": [None]*9, "I": [None]*9})
    slots_high  = parametros.setdefault("SlotsDestaque", {"A": set(), "I": set()})
    slots_rects["A"] = [None]*9
    slots_rects["I"] = [None]*9
    slots_high["A"]  = set()
    slots_high["I"]  = set()

    parametros.setdefault("AlvosSelecionados", [])

    # -------------------------------------------------------
    # >>> LIMPEZA AUTOMÁTICA ao mudar de POKÉMON/ATAQUE <<<
    # -------------------------------------------------------
    def _id_poke(p):
        if not p: return None
        try:
            return (
                p.get("ID") or p.get("id") or p.get("Code") or p.get("code") or p.get("Nome") or p.get("nome"),
                int(p.get("Pos",  -1)),
                int(p.get("ReservaPos", -1)),
                bool(p.get("Ativo", True)),
            )
        except Exception:
            return (p.get("Nome") or p.get("nome") or str(p), None, None, None)

    def _id_atk(a):
        if isinstance(a, int):  return ("INT", a)
        if isinstance(a, str):  return ("STR", a.strip().lower())
        if isinstance(a, dict):
            return (
                "DICT",
                (a.get("Code") or a.get("code") or a.get("Nome") or a.get("nome") or a.get("Ataque") or a.get("ataque")),
                (a.get("Alvo") or a.get("alvo") or ""),
                (a.get("Estilo") or a.get("estilo") or ""),
            )
        return None

    def _full_reset_estado(preservar_modo=True):
        # NÃO mexe em AliadoSelecionado / InimigoSelecionado
        # NÃO desliga ModoAlvificando (preserva o valor atual, a menos que explicitado)
        parametros["AlvosSelecionados"]    = []
        parametros["AtacanteSelecionado"]  = None
        parametros["MovimentoSelecionado"] = None
        parametros["__alvo_finalizado_ok"] = False
        if not preservar_modo:
            parametros["ModoAlvificando"] = False
        slots_high["A"].clear()
        slots_high["I"].clear()

    cur_poke_id = _id_poke(aliado_sel)
    cur_atk_id  = _id_atk(atk_sel)
    prev_poke_id = parametros.get("__cache_sel_poke", "__NOVO__")
    prev_atk_id  = parametros.get("__cache_sel_atk",  "__NOVO__")

    # Se já tínhamos cache antes, detecta mudança e limpa (sem desligar o modo)
    if prev_poke_id != "__NOVO__" or prev_atk_id != "__NOVO__":
        if cur_poke_id != prev_poke_id or cur_atk_id != prev_atk_id:
            _full_reset_estado(preservar_modo=True)

    # Atualiza cache para o frame atual
    parametros["__cache_sel_poke"] = cur_poke_id
    parametros["__cache_sel_atk"]  = cur_atk_id

    # Re-sincroniza após possíveis resets
    modo_alvo = bool(parametros.get("ModoAlvificando"))
    # -------------------------------------------------------

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

    # ==== helpers que precisam existir antes de uso ====
    def _indice_do_aliado(aliado_dict):
        equipe = parametros.get("EquipeAliada") or []
        try:
            pos = int(aliado_dict.get("Pos", -1))
            for i, p in enumerate(equipe):
                if int((p or {}).get("Pos", -2)) == pos:
                    return i
        except Exception:
            pass
        for i, p in enumerate(equipe):
            if p is aliado_dict or p == aliado_dict:
                return i
        return None

    def _pos_aliado_atual():
        if aliado_sel and isinstance(aliado_sel, dict):
            try:
                return int(aliado_sel.get("Pos", 1))
            except Exception:
                pass
        atk_idx = parametros.get("AtacanteSelecionado")
        equipe  = parametros.get("EquipeAliada") or []
        try:
            if atk_idx is not None and 0 <= int(atk_idx) < len(equipe):
                return int((equipe[int(atk_idx)] or {}).get("Pos", 1))
        except Exception:
            pass
        return 1

    # >>> helpers auto-alvo
    def _apos_primeiro_alvo():
        if parametros.get("AtacanteSelecionado") is None and aliado_sel:
            parametros["AtacanteSelecionado"] = _indice_do_aliado(aliado_sel)
        if parametros.get("MovimentoSelecionado") is None:
            parametros["MovimentoSelecionado"] = atk_sel

    def _finaliza_auto():
        parametros["__alvo_finalizado_ok"] = True
        parametros["__ja_limpei_estado"]   = True
        parametros["ModoAlvificando"]      = False
        slots_high["A"].clear()
        slots_high["I"].clear()

    # >>> auto-seleção quando não precisa escolha manual
    if modo_alvo:
        alvo_raw = None
        if isinstance(atk_sel, dict):
            alvo_raw = (atk_sel.get("Alvo") or atk_sel.get("alvo"))
        elif isinstance(atk_sel, str):
            alvo_raw = atk_sel
        alvo_txt = (str(alvo_raw).strip().lower() if alvo_raw is not None else "")

        tokens_all = {
            "all", "todos", "all inimigos", "todos inimigos",
            "all aliados", "todos aliados", "aleatorio", "aleatório", "random"
        }
        tokens_self = {"sem alvo", "sem", "self", "próprio", "proprio",}

        if alvo_txt in tokens_all and alvo_raw:
            if alvo_raw not in parametros["AlvosSelecionados"]:
                parametros["AlvosSelecionados"].append(alvo_raw)
            _apos_primeiro_alvo()
            _finaliza_auto()
            return

        if alvo_txt in tokens_self:
            pos = max(1, min(9, int(_pos_aliado_atual())))
            code = f"A{pos}"
            if code not in parametros["AlvosSelecionados"]:
                parametros["AlvosSelecionados"].append(code)
            _apos_primeiro_alvo()
            _finaliza_auto()
            return

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
        poke = next((p for p in parametros.get("AliadosAtivos", []) if p and p.get("Pos") == i + 1), None)
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
            # limpa estado ao clicar num novo aliado, mas PRESERVA o valor atual de ModoAlvificando
            def _reset_click():
                _full_reset_estado(preservar_modo=True)

            func_esq_ali = None
            desf_esq_ali = None
            if poke is not None:
                func_esq_ali = [
                    _reset_click,
                    (lambda p=poke: parametros.update({"AliadoSelecionado": p})),
                    (lambda a=anima: a.update({
                        "_anima_painel_aliado": pygame.time.get_ticks(),
                        "Y1": 1080,
                        "Y2": 900,
                    })),
                ]
                desf_esq_ali = [
                    (lambda: parametros.update({"AliadoSelecionado": None})),
                    (lambda a=anima: a.update({
                        "_anima_painel_aliado": pygame.time.get_ticks(),
                        "Y1": 900,
                        "Y2": 1080,
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
        poke = next((p for p in parametros.get("InimigosAtivos", []) if p and p.get("Pos") == i + 1), None)
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
            func_esq_ini = None
            desf_esq_ini = None
            if poke is not None:
                func_esq_ini = [
                    (lambda p=poke: parametros.update({"InimigoSelecionado": p})),
                    (lambda a=anima: a.update({
                        "_anima_painel_inimigo": pygame.time.get_ticks(),
                        "Y3": -200,
                        "Y4": 0,
                    })),
                ]
                desf_esq_ini = [
                    (lambda: parametros.update({"InimigoSelecionado": None})),
                    (lambda a=anima: a.update({
                        "_anima_painel_inimigo": pygame.time.get_ticks(),
                        "Y3": 0,
                        "Y4": -200,
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

def TelaAlvoBatalha(tela, estados, eventos, parametros):
    # ===== helpers gerais =====
    def _slot_center(lado, idx1based):
        slots = parametros.get("SlotsRects", {})
        arr = slots.get(lado) or []
        i0 = max(1, min(12, int(idx1based))) - 1
        if 0 <= i0 < len(arr) and isinstance(arr[i0], pygame.Rect):
            r = arr[i0]
            return (r.centerx, r.centery)
        return None

    def _mouse_over_highlight():
        mx, my = pygame.mouse.get_pos()
        slots = parametros.get("SlotsRects", {})
        hi    = parametros.get("SlotsDestaque", {"A": set(), "I": set()})
        for lado in ("A", "I"):
            arr = slots.get(lado) or []
            for i0, r in enumerate(arr):
                if i0 in (hi.get(lado) or set()) and isinstance(r, pygame.Rect) and r.collidepoint(mx, my):
                    return lado, (i0 + 1), (r.centerx, r.centery)  # idx1based (10..12 = reservas)
        return None

    def _is_reserva_idx(idx1based: int) -> bool:
        try:
            return int(idx1based) > 9
        except Exception:
            return False

    def _norm_parse(res):
        """Aceita _parse_code retornando (lado, idx) ou (lado, idx, is_reserva)."""
        if not res or not isinstance(res, tuple):
            return None
        if len(res) == 2:
            lado, idx = res
            return lado, idx, (int(idx) > 9)
        if len(res) >= 3:
            lado, idx, is_reserva = res[0], res[1], bool(res[2])
            return lado, idx, is_reserva
        return None
    
    def _parse_code(code):
        """
        Aceita:
        - A/I1..12  (onde 10..12 são reservas)
        - RA1..3 / RI1..3  (mapeados para 10..12)
        Retorna (lado, idx1based, is_reserva) ou None.
        """
        if not code or not isinstance(code, str):
            return None
        s = code.strip().upper()

        # RA1..3 / RI1..3  → idx 10..12
        if len(s) >= 3 and s[0] == "R" and s[1] in ("A", "I"):
            lado = s[1]
            try:
                k = int(s[2:])
            except ValueError:
                return None
            if 1 <= k <= 3:
                idx = 9 + k  # 10..12
                return lado, idx, True
            return None

        # A1..12 / I1..12
        if s[0] in ("A", "I"):
            lado = s[0]
            try:
                idx = int(s[1:])
            except ValueError:
                return None
            if 1 <= idx <= 12:
                return lado, idx, (idx > 9)

        return None

    def _cor_por_mov(mov):
        ROXO   = (160, 90, 255)
        LARAN  = (255, 150, 40)
        AZUL   = (60, 160, 255)
        VERDE  = (70, 220, 120)
        ROSA   = (255, 110, 200)
        if isinstance(mov, int):
            if mov == 1:  # mover
                return VERDE
            if mov == 2:  # trocar
                return ROSA
            return (255, 255, 255)
        if isinstance(mov, dict):
            est = (mov.get("Estilo") or mov.get("estilo") or "").strip().lower()
            if est == "e": return ROXO      # especial
            if est == "n": return LARAN     # físico
            if est == "s": return AZUL      # suporte
        return (255, 255, 255)

    def _ponto_do_atacante(atacante_idx):
        equipe = parametros.get("EquipeAliada") or []
        if atacante_idx is None or not (0 <= int(atacante_idx) < len(equipe)):
            return None
        poke = equipe[int(atacante_idx)]
        pos  = int(poke.get("Pos", 1))
        return _slot_center("A", pos)

    def _desenha_fluxo(x1, y1, x2, y2, cor, translucido=False, raio=5):
        Fluxo(
            tela, x1, y1, x2, y2,
            Pontos=40, pontos_por_100px=5,
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

        # origem: centro do slot do aliado selecionado
        try:
            pos_ali = int(aliado_sel.get("Pos", 1))
        except Exception:
            pos_ali = 1
        origem = _slot_center("A", pos_ali)
        if not origem:
            return

        # destino: mouse ou slot destacado sob o mouse
        mx, my = pygame.mouse.get_pos()
        alvo_hover = _mouse_over_highlight()
        if alvo_hover:
            _, idx1b, (cx, cy) = alvo_hover
            dest = (cx, cy)
            reserva_hover = _is_reserva_idx(idx1b)
        else:
            dest = (mx, my)
            reserva_hover = False

        # cor: vermelho se sem energia, senão amarelo
        ene = int(aliado_sel.get("Energia", aliado_sel.get("EneAtual", 0)) or 0)
        custo = int(parametros.get("CustoAtualEnergia", 0) or 0)
        cor_fluxo = (255, 80, 80) if (ene - custo) < -5 else (255, 210, 80)

        # fluxo dinâmico (inclui reservas)
        _desenha_fluxo(origem[0], origem[1], dest[0], dest[1], cor_fluxo, translucido=False, raio=6)

        # pulso menor se for reserva
        if alvo_hover:
            if reserva_hover:
                Pulso(tela, dest, cor=cor_fluxo, raio_base=18, variacao=0.35, velocidade=1.6, alpha_base=95)
            else:
                Pulso(tela, dest, cor=cor_fluxo, raio_base=32, variacao=0.42, velocidade=1.6, alpha_base=95)

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
            parsed = _norm_parse(_parse_code(code))
            if not parsed:
                continue
            lado, idx, is_reserva = parsed
            destino = _slot_center(lado, idx)
            if not destino:
                continue

            # fluxo estável da ação atual (A/I1..12, incluindo reservas)
            _desenha_fluxo(origem[0], origem[1], destino[0], destino[1], cor, translucido=False, raio=6)

            # pulso: menor nas reservas
            if is_reserva:
                Pulso(tela, destino, cor=cor, raio_base=16, variacao=0.28, velocidade=1.4, alpha_base=90)
            else:
                Pulso(tela, destino, cor=cor, raio_base=30, variacao=0.36, velocidade=1.4, alpha_base=90)

    # ===== 3) FluxosLog =====
    def FluxosLog():
        logs = parametros.get("LogAtual") or []
        if not isinstance(logs, list) or not logs:
            return
        alpha_soft = 80  # estático

        for item in logs:
            if not isinstance(item, dict):
                continue
            origem = _ponto_do_atacante(item.get("Atacante"))
            if not origem:
                continue

            cor = _cor_por_mov(item.get("Movimento"))
            for code in (item.get("Alvos") or []):
                parsed = _norm_parse(_parse_code(code))
                if not parsed:
                    continue
                lado, idx, _is_res = parsed
                destino = _slot_center(lado, idx)
                if not destino:
                    continue

                # fluxo de log estático (sem pulso)
                _desenha_fluxo(origem[0], origem[1], destino[0], destino[1], cor, translucido=alpha_soft, raio=5)

    # ==== chamada das três etapas ====
    FluxoAlvificando()
    FluxosAtuais()
    FluxosLog()

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
    Desenhar_Botoes_Combate(tela,parametros,eventos)

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


    DesenharPlayer(tela,Player.Skin,(70,880),nome=Player.Nome,Fonte=Fontes[18])

    if not parametros["BatalhaSimples"]:
        pass

    # atualiza posição por frame (deslocamento horizontal)
    for anim_obj, (cx, cy) in _anim_inimigos:
        anim_obj.atualizar(tela, nova_pos=(int(cx + dx_dir), int(cy)), multiplicador=1.0)
    for anim_obj, (cx, cy) in _anim_aliados:
        anim_obj.atualizar(tela, nova_pos=(int(cx + dx_esq), int(cy)), multiplicador=1.0)

def TelaHudBatalha(tela, estados, eventos, parametros):
    global AliadoSelecionadoCache, InimigoSelecionadoCache

    if parametros["AliadoSelecionado"] != None:
        AliadoSelecionadoCache = parametros["AliadoSelecionado"]

    if parametros["InimigoSelecionado"] != None:
        InimigoSelecionadoCache = parametros["InimigoSelecionado"]

    if AliadoSelecionadoCache is not None:
        YA = Animar(anima["Y1"], anima["Y2"], anima["_anima_painel_aliado"])
        PainelPokemonBatalha(AliadoSelecionadoCache, tela, (330, YA), eventos, parametros, anima)

    if InimigoSelecionadoCache is not None:
        YI = Animar(anima["Y3"], anima["Y4"], anima["_anima_painel_inimigo"])
        PainelPokemonBatalha(InimigoSelecionadoCache, tela, (680, YI), eventos, parametros, anima)

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
        if parametros["AliadoSelecionado"]["Energia"] - parametros["CustoAtualEnergia"] >= -5:
            Botao(
                tela, "Preparar", (1660,960,260,60),
                Texturas["vermelho"], (0,0,0), (240,240,240),
                [
                    lambda: parametros["LogAtual"].append({
                        "Atacante": parametros["AtacanteSelecionado"],
                        "Movimento": parametros["MovimentoSelecionado"],
                        "Alvos": parametros["AlvosSelecionados"]
                    }),
                    lambda: parametros["AliadoSelecionado"].update({
                        "Energia": parametros["AliadoSelecionado"]["Energia"] - parametros["CustoAtualEnergia"],
                        "PreGasto": parametros["CustoAtualEnergia"]
                    }),
                    lambda: parametros.update({
                        "AtaqueAliadoSelecionado": None,
                        "AlvosSelecionados": [],
                        "CustoAtualEnergia": 0,
                        "AtacanteSelecionado": None,
                        "MovimentoSelecionado": None,
                        "EstadoBotoesPainelPokemonBatalha": {},
                        "ModoAlvificando": False
                    }),
                    anima.update({"_anima_painel_acao": pygame.time.get_ticks()})
                ],
                Fontes[35], BG, eventos
            )
        else:
            Botao(
                tela, "Preparar", (1660,960,260,60),
                Cores["cinza"], (0,0,0), (240,240,240),
                lambda: tocar("Bloq"),
                Fontes[35], BG, eventos
            )
    else:
        Botao(
            tela, "Preparar", (1660,960,260,60),
            Cores["cinza"], (0,0,0), (240,240,240),
            lambda: tocar("Bloq"),
            Fontes[35], BG, eventos
        )

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
        Botao(tela, "X", (x+124, y+2, 20, 20), Cores["vermelho"], (0,0,0), (240,240,240),
            [lambda: parametros["EquipeAliada"][acao["Atacante"]].update({"Energia": parametros["EquipeAliada"][acao["Atacante"]]["Energia"] + parametros["EquipeAliada"][acao["Atacante"]]["PreGasto"]}),
            lambda: (parametros["LogAtual"].pop(i), Acao_surface_cache.pop(i))],
            Fontes[10], BG, eventos, grossura=1)


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

def BatalhaTelaPadrao(tela, estados, eventos, parametros):

    TelaFundoBatalha(tela, estados, eventos, parametros)
    TelaHudBatalha(tela, estados, eventos, parametros)

    Botao_Tecla("esc",lambda: parametros.update({"Tela": BatalhaTelaOpçoes}))

def BatalhaLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes, Icones, Player
    global _anim_aliados, _anim_inimigos, AliadoSelecionadoCache, InimigoSelecionadoCache, Acao_surface_cache
    from Codigo.Cenas.Mundo import player

    _anim_inimigos = None
    _anim_aliados = None

    InimigoSelecionadoCache = None
    AliadoSelecionadoCache = None
    Acao_surface_cache = []

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

