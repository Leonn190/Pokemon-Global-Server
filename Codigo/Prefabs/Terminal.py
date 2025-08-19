import pygame
import time

# ---------------- Estado do terminal ----------------
mensagens_terminal = []   # cada item: (texto, cor, timestamp)
ultimo_tempo_msg = 0.0

# ---------------- Estado UI (persistente) ----------------
_terminal_ui = {
    "sticky": False,        # terminal preso visível
    "input": "",            # buffer de texto
    "cursor": 0,            # posição do cursor no buffer
    "last_blink": 0.0,      # controle de blink
    "blink_on": True,       # estado atual do cursor
    "focus": True,          # foco no campo (sempre True aqui)
    "space_down": False,
    "space_since": 0.0,
    "chaos_next": 0.0,
}

_BACKSPACE = {
    "held": False,
    "next_ms": 0,
    "delay_ms": 280,  # atraso inicial até começar a repetir
    "rate_ms": 35,    # intervalo entre repetições
}

# Configurações
TERMINAL_LARGURA = 700
TERMINAL_ALTURA  = 280
TERMINO_VISIVEL  = 5.0   # segundos "cheio" de visibilidade
FADE_IN_DUR      = 0.4    # segundos
FADE_OUT_DUR     = 0.8    # segundos
ALPHA_MAX        = 180    # opacidade máxima do fundo (0-255)
MARGEM           = 10

COR_FUNDO_INPUT  = (255, 255, 255, 28)
COR_BORDA_INPUT  = (220, 220, 220, 80)
COR_TEXTO        = (255, 255, 255)

def quebrar_linhas(texto, fonte, largura_max):
    """
    Quebra 'texto' em linhas para caber em 'largura_max' (px), usando 'fonte'.
    Retorna lista de linhas (strings).
    """
    palavras = str(texto).split()
    linhas = []
    atual = ""

    for p in palavras:
        tentativa = p if not atual else (atual + " " + p)
        if fonte.size(tentativa)[0] <= largura_max:
            atual = tentativa
        else:
            if atual:
                linhas.append(atual)
            # Se a palavra sozinha não cabe, quebra forçando
            while fonte.size(p)[0] > largura_max and len(p) > 1:
                i = len(p)
                while i > 0 and fonte.size(p[:i])[0] > largura_max:
                    i -= 1
                if i <= 0:
                    break
                linhas.append(p[:i])
                p = p[i:]
            atual = p
    if atual:
        linhas.append(atual)
    return linhas

def _alpha_terminal(sticky=False):
    """
    Calcula alpha do fundo do terminal.
    Se sticky=True, fica sempre no máximo.
    """
    if sticky:
        return ALPHA_MAX
    if ultimo_tempo_msg <= 0:
        return 0
    t = time.time() - ultimo_tempo_msg
    total = FADE_IN_DUR + TERMINO_VISIVEL + FADE_OUT_DUR

    if t < 0:
        return 0
    if t <= FADE_IN_DUR:  # fade in
        k = t / FADE_IN_DUR
        return int(ALPHA_MAX * k)
    elif t <= FADE_IN_DUR + TERMINO_VISIVEL:  # cheio
        return ALPHA_MAX
    elif t <= total:  # fade out
        k = 1.0 - (t - FADE_IN_DUR - TERMINO_VISIVEL) / FADE_OUT_DUR
        return int(ALPHA_MAX * max(0.0, min(1.0, k)))
    else:
        return 0

def LeComandos(raw, comandos):
    """
    Executa comandos no formato: /Func_Arg1_Arg2 ...
    - 'Func' é o nome da função em 'comandos' (dict: nome -> callable)
    - Args são separados por '_' e convertidos para int/float quando fizer sentido.
    Retorna: (ok: bool, msg_erro: str | None, func_name: str | None)
    """
    raw = str(raw).strip()
    if not raw.startswith("/"):
        return False, None, None

    token = raw.split()[0]        # ex: "/LevelUp_3_jonas"
    cmdline = token[1:]           # "LevelUp_3_jonas"
    if not cmdline:
        return False, "Comando '' não encontrado", ""

    parts = cmdline.split("_")
    func_name = parts[0]
    arg_tokens = parts[1:]

    # resolve handler
    handler = None
    if isinstance(comandos, dict):
        handler = comandos.get(func_name)

    if handler is None or not callable(handler):
        return False, f"Comando '{func_name}' não encontrado", func_name

    # coerce simples para números quando possível
    def _coerce(s):
        s = str(s).strip()
        try:
            return int(s)
        except Exception:
            try:
                return float(s.replace(",", "."))  # suporta "3,5"
            except Exception:
                return s

    args = [_coerce(a) for a in arg_tokens]

    try:
        handler(*args)
        return True, None, func_name
    except Exception:
        return False, f'erro ao executar o comando "{func_name}"', func_name

def adicionar_mensagem_terminal(msg, cor=(255, 255, 255), online_ctx=None, comandos=None, nome="Server"):
    """
    - Mensagem comum: escreve no terminal e repassa para online_ctx["MensagemOnline"] (sem prefixo).
    - Comando (/...): executa via LeComandos; sucesso = não loga nada; erro/não encontrado = loga em amarelo.
    Mantém apenas as 10 últimas mensagens.
    """
    global ultimo_tempo_msg, mensagens_terminal
    agora = time.time()

    raw = str(msg).strip()
    is_cmd = raw.startswith("/")

    if is_cmd:
        ok, erro, _fname = LeComandos(raw, comandos)
        if not ok and erro:
            mensagens_terminal.append((f"[{nome}] {erro}", (255, 255, 0), agora))
    else:
        txt = f"[{nome}] {raw}"
        mensagens_terminal.append((txt, cor, agora))
        if isinstance(online_ctx, dict):
            online_ctx["MensagemOnline"] = raw

    # manter apenas as 10 últimas
    if len(mensagens_terminal) > 10:
        mensagens_terminal = mensagens_terminal[-10:]

    ultimo_tempo_msg = agora

def _desenhar_barra_texto_terminal(tela, fonte, x, y, w, alpha_bg, eventos=None, teclado_ctx=None):
    h = fonte.get_height() + 10
    rect = pygame.Rect(x, y, w, h)

    # fundo
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, COR_FUNDO_INPUT, surf.get_rect(), border_radius=h // 2)
    pygame.draw.rect(surf, COR_BORDA_INPUT, surf.get_rect(), width=1, border_radius=h // 2)
    surf.set_alpha(alpha_bg)
    tela.blit(surf, rect.topleft)

    # parâmetros do "hold" de ESPAÇO (mantendo sua lógica)
    HOLD_DELAY = 0.45   # iniciar deleção após ~450ms
    REPEAT_RATE = 0.05  # deletar a cada 50ms enquanto segurado

    # só processa eventos se o modo teclado estiver ativo
    modo_teclado_ativo = bool(teclado_ctx and teclado_ctx.get("ModoTeclado"))
    submitted = False

    # utilitário: colar do clipboard
    def _clipboard_paste_text():
        txt = ""
        try:
            import pyperclip
            txt = pyperclip.paste() or ""
        except Exception:
            # fallback leve
            try:
                if hasattr(pygame, "scrap"):
                    try:
                        pygame.scrap.init()
                    except Exception:
                        pass
                    data = pygame.scrap.get(getattr(pygame, "SCRAP_TEXT", None)) if hasattr(pygame, "SCRAP_TEXT") else None
                    if data:
                        if isinstance(data, bytes):
                            data = data.decode("utf-8", "ignore")
                        txt = data or ""
            except Exception:
                txt = ""
        # saneamento básico: transformar quebras em espaço único
        if txt:
            txt = txt.replace("\r\n", "\n").replace("\r", "\n")
            txt = " ".join(txt.split())
        return txt

    if eventos and modo_teclado_ativo:
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                # COLAR (Ctrl+V, Shift+Insert, Ctrl+Insert)
                if (
                    ((mods & pygame.KMOD_CTRL) and ev.key == pygame.K_v) or
                    ((mods & pygame.KMOD_SHIFT) and ev.key == pygame.K_INSERT) or
                    ((mods & pygame.KMOD_CTRL) and ev.key == pygame.K_INSERT)
                ):
                    pasted = _clipboard_paste_text()
                    if pasted:
                        s = _terminal_ui["input"]; i = _terminal_ui["cursor"]
                        _terminal_ui["input"] = s[:i] + pasted + s[i:]
                        _terminal_ui["cursor"] = i + len(pasted)
                    continue  # evita cair no TEXTINPUT com 'v' etc.

                # ENTER envia
                if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    submitted = True

                # BACKSPACE: apaga 1x e arma repetição rápida
                elif ev.key == pygame.K_BACKSPACE:
                    if _terminal_ui["cursor"] > 0:
                        s = _terminal_ui["input"]; i = _terminal_ui["cursor"]
                        _terminal_ui["input"] = s[:i - 1] + s[i:]
                        _terminal_ui["cursor"] -= 1
                    # habilita repetição externa
                    _BACKSPACE["held"] = True
                    _BACKSPACE["next_ms"] = pygame.time.get_ticks() + _BACKSPACE["delay_ms"]

                # DELETE
                elif ev.key == pygame.K_DELETE:
                    s = _terminal_ui["input"]; i = _terminal_ui["cursor"]
                    if i < len(s):
                        _terminal_ui["input"] = s[:i] + s[i + 1:]

                elif ev.key == pygame.K_LEFT:
                    _terminal_ui["cursor"] = max(0, _terminal_ui["cursor"] - 1)

                elif ev.key == pygame.K_RIGHT:
                    _terminal_ui["cursor"] = min(len(_terminal_ui["input"]), _terminal_ui["cursor"] + 1)

                elif ev.key == pygame.K_HOME:
                    _terminal_ui["cursor"] = 0

                elif ev.key == pygame.K_END:
                    _terminal_ui["cursor"] = len(_terminal_ui["input"])

                elif ev.key == pygame.K_SPACE:
                    # início do "hold de espaço" (sua lógica existente)
                    if not _terminal_ui.get("space_down", False):
                        _terminal_ui["space_down"] = True
                        _terminal_ui["space_since"] = time.time()
                        _terminal_ui["chaos_next"] = 0.0  # usado como "repeat_next" do espaço

            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_SPACE:
                    _terminal_ui["space_down"] = False
                    _terminal_ui["chaos_next"] = 0.0
                elif ev.key == pygame.K_BACKSPACE:
                    _BACKSPACE["held"] = False
                    _BACKSPACE["next_ms"] = 0

            elif ev.type == pygame.TEXTINPUT:
                txt = ev.text
                if txt:
                    # se estamos em "apagar segurando espaço" (após o delay), ignore espaços
                    ignore_space_for_delete = (
                        _terminal_ui.get("space_down", False)
                        and (time.time() - (_terminal_ui.get("space_since") or time.time()) >= HOLD_DELAY)
                        and txt == " "
                    )
                    if not ignore_space_for_delete:
                        s = _terminal_ui["input"]; i = _terminal_ui["cursor"]
                        _terminal_ui["input"] = s[:i] + txt + s[i:]
                        _terminal_ui["cursor"] += len(txt)

    # Repetição rápida do BACKSPACE (externo)
    if modo_teclado_ativo and _BACKSPACE["held"]:
        now = pygame.time.get_ticks()
        if now >= _BACKSPACE["next_ms"]:
            if _terminal_ui["cursor"] > 0 and len(_terminal_ui["input"]) > 0:
                s = _terminal_ui["input"]; i = _terminal_ui["cursor"]
                _terminal_ui["input"] = s[:i - 1] + s[i:]
                _terminal_ui["cursor"] -= 1
            _BACKSPACE["next_ms"] = now + _BACKSPACE["rate_ms"]

    # efeito: SEGURAR ESPAÇO => repetir "backspace" após delay (sua lógica)
    if modo_teclado_ativo and _terminal_ui.get("space_down", False):
        t_hold = time.time() - (_terminal_ui.get("space_since") or time.time())
        if t_hold >= HOLD_DELAY:
            nowf = time.time()
            next_time = _terminal_ui.get("chaos_next", 0.0)
            if nowf >= next_time:
                if _terminal_ui["cursor"] > 0 and len(_terminal_ui["input"]) > 0:
                    s = _terminal_ui["input"]; i = _terminal_ui["cursor"]
                    _terminal_ui["input"] = s[:i - 1] + s[i:]
                    _terminal_ui["cursor"] -= 1
                _terminal_ui["chaos_next"] = nowf + REPEAT_RATE

    # texto
    texto = _terminal_ui["input"]
    txt_surf = fonte.render(texto or "", True, COR_TEXTO)
    txt_surf.set_alpha(alpha_bg)
    tx = rect.x + 12
    ty = rect.y + (rect.height - txt_surf.get_height()) // 2
    tela.blit(txt_surf, (tx, ty))

    # cursor piscante (só quando pode digitar)
    if modo_teclado_ativo:
        tnow = time.time()
        if tnow - _terminal_ui.get("last_blink", 0.0) > 0.5:
            _terminal_ui["blink_on"] = not _terminal_ui.get("blink_on", True)
            _terminal_ui["last_blink"] = tnow
        if _terminal_ui.get("blink_on", True):
            prefix = (texto or "")[:_terminal_ui["cursor"]]
            px = tx + fonte.size(prefix)[0]
            pygame.draw.line(
                tela, (255, 255, 255, alpha_bg),
                (px, rect.y + 6), (px, rect.y + rect.height - 6), width=1
            )

    return submitted

def terminal(tela, fonte, Nome, tecla_ativacao=None, eventos=None, online_ctx=None, comandos=None, teclado_ctx=None):
    """
    Desenha o terminal em (0,0), com fade in/out OU travado (sticky) via tecla_ativacao.
    Integra barra de texto inferior controlada por 'ModoTeclado' (em teclado_ctx).
    - tecla_ativacao: pygame.K_*, alterna sticky e ModoTeclado (True/False).
    - ESC ou clique do mouse desativam ModoTeclado se ele estiver ativo.
    - Se mensagem começa com '/', trata como comando (não envia online); senão,
      quando online_ctx for dict, preenche online_ctx["MensagemOnline"].

    Extra:
    - ModoTecladoCache: quando ModoTeclado transita de True -> False, o terminal desaparece imediatamente.
    """
    global ultimo_tempo_msg
    # garante as chaves no dicionário externo (sem auto-ativar)
    if teclado_ctx is not None:
        if "ModoTeclado" not in teclado_ctx:
            teclado_ctx["ModoTeclado"] = False
        if "ModoTecladoCache" not in teclado_ctx:
            teclado_ctx["ModoTecladoCache"] = teclado_ctx["ModoTeclado"]

    # --- entrada/controles ---
    if eventos and tecla_ativacao is not None:
        for ev in eventos:
            if ev.type == pygame.KEYDOWN and ev.key == tecla_ativacao:
                # alterna visibilidade "presa"
                _terminal_ui["sticky"] = not _terminal_ui["sticky"]
                if _terminal_ui["sticky"]:
                    ultimo_tempo_msg = time.time()
                # alterna modo de digitação somente via tecla de ativação
                if teclado_ctx is not None:
                    teclado_ctx["ModoTeclado"] = not teclado_ctx["ModoTeclado"]

            # ESC sai do modo teclado (não mexe no sticky)
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                if teclado_ctx is not None and teclado_ctx.get("ModoTeclado"):
                    teclado_ctx["ModoTeclado"] = False

            # qualquer clique do mouse sai do modo teclado
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if teclado_ctx is not None and teclado_ctx.get("ModoTeclado"):
                    teclado_ctx["ModoTeclado"] = False

    # --- queda de ModoTeclado: True -> False => esconder terminal ---
    if teclado_ctx is not None:
        prev = teclado_ctx.get("ModoTecladoCache", False)
        cur  = teclado_ctx.get("ModoTeclado", False)
        if prev and not cur:
            _terminal_ui["sticky"] = False
            ultimo_tempo_msg = 0  # força alpha a 0
            teclado_ctx["ModoTecladoCache"] = cur
            return  # não desenha nada neste frame
        # atualiza cache para o próximo frame
        teclado_ctx["ModoTecladoCache"] = cur

    sticky = _terminal_ui["sticky"]

    # sem mensagens e não-sticky => não desenha
    if not mensagens_terminal and not sticky:
        return

    alpha_bg = _alpha_terminal(sticky=sticky)
    if alpha_bg <= 0:
        return

    # --- fundo do terminal ---
    fundo = pygame.Surface((TERMINAL_LARGURA, TERMINAL_ALTURA), pygame.SRCALPHA)
    fundo.fill((0, 0, 0, alpha_bg))
    tela.blit(fundo, (0, 0))

    # --- layout de texto + barra de entrada ---
    input_h = fonte.get_height() + 10
    area_texto_w = TERMINAL_LARGURA - 2 * MARGEM
    linha_altura = fonte.get_height() + 4
    area_lin_h = (TERMINAL_ALTURA - 3 * MARGEM - input_h)
    max_linhas_visiveis = max(1, area_lin_h // linha_altura)

    # quebra de linhas de todas as mensagens
    linhas = []
    for texto, cor, ts in mensagens_terminal:
        for l in quebrar_linhas(texto, fonte, area_texto_w):
            linhas.append((l, cor, ts))

    # mantém apenas as últimas que cabem
    if len(linhas) > max_linhas_visiveis:
        linhas = linhas[-max_linhas_visiveis:]

    # desenha do "pé" para cima (terminando acima da barra de entrada)
    base_y = MARGEM + area_lin_h - (len(linhas) * linha_altura)
    y_texto = max(MARGEM, base_y)
    for l, cor, _ in linhas:
        surf = fonte.render(l, True, cor)
        surf.set_alpha(alpha_bg)
        tela.blit(surf, (MARGEM, y_texto))
        y_texto += linha_altura

    # --- barra de texto inferior ---
    input_x = MARGEM
    input_y = TERMINAL_ALTURA - MARGEM - input_h
    submitted = _desenhar_barra_texto_terminal(
        tela, fonte, input_x, input_y, area_texto_w, alpha_bg,
        eventos=eventos, teclado_ctx=teclado_ctx
    )

    # só envia se ModoTeclado estiver ativo
    if submitted and teclado_ctx and teclado_ctx.get("ModoTeclado"):
        texto = _terminal_ui["input"].strip()
        if texto:
            adicionar_mensagem_terminal(texto, COR_TEXTO, online_ctx=online_ctx, comandos=comandos, nome=Nome)
        _terminal_ui["input"] = ""
        _terminal_ui["cursor"] = 0
