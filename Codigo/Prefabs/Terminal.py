import pygame
import time

class Terminal:
    # ===== Configurações padrão =====
    TERMINAL_LARGURA = 700
    TERMINAL_ALTURA  = 280
    TERMINO_VISIVEL  = 3.0   # segundos "cheio" visível
    FADE_IN_DUR      = 0.4   # s
    FADE_OUT_DUR     = 0.8   # s
    ALPHA_MAX        = 180
    MARGEM           = 10

    COR_FUNDO_INPUT  = (255, 255, 255, 28)
    COR_BORDA_INPUT  = (220, 220, 220, 80)
    COR_TEXTO        = (255, 255, 255)

    def __init__(self):
        # ----- Estado do terminal -----
        self.mensagens = []          # itens: (texto, cor, timestamp)
        self.ultimo_tempo_msg = 0.0

        # ----- Estado UI persistente -----
        self.ui = {
            "sticky": False,
            "input": "",
            "cursor": 0,
            "last_blink": 0.0,
            "blink_on": True,
            "focus": True,
            "space_down": False,
            "space_since": 0.0,
            "chaos_next": 0.0,  # usado como repeat do "apagar com espaço"
        }

        # backspace hold/repeat
        self._backspace = {
            "held": False,
            "next_ms": 0,
            "delay_ms": 280,
            "rate_ms": 35,
        }

    # ========= Utilitários =========
    @staticmethod
    def quebrar_linhas(texto, fonte, largura_max):
        palavras = str(texto).split()
        linhas, atual = [], ""
        for p in palavras:
            tentativa = p if not atual else (atual + " " + p)
            if fonte.size(tentativa)[0] <= largura_max:
                atual = tentativa
            else:
                if atual:
                    linhas.append(atual)
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

    def _alpha(self, sticky=False):
        if sticky:
            return self.ALPHA_MAX
        if self.ultimo_tempo_msg <= 0:
            return 0
        t = time.time() - self.ultimo_tempo_msg
        total = self.FADE_IN_DUR + self.TERMINO_VISIVEL + self.FADE_OUT_DUR

        if t < 0:
            return 0
        if t <= self.FADE_IN_DUR:
            k = t / self.FADE_IN_DUR
            return int(self.ALPHA_MAX * k)
        elif t <= self.FADE_IN_DUR + self.TERMINO_VISIVEL:
            return self.ALPHA_MAX
        elif t <= total:
            k = 1.0 - (t - self.FADE_IN_DUR - self.TERMINO_VISIVEL) / self.FADE_OUT_DUR
            return int(self.ALPHA_MAX * max(0.0, min(1.0, k)))
        else:
            return 0

    @staticmethod
    def LeComandos(raw, comandos):
        """Mesma lógica do seu LeComandos (formato /Func_Arg1_Arg2)."""
        raw = str(raw).strip()
        if not raw.startswith("/"):
            return False, None, None

        token = raw.split()[0]
        cmdline = token[1:]
        if not cmdline:
            return False, "Comando '' não encontrado", ""

        parts = cmdline.split("_")
        func_name = parts[0]
        arg_tokens = parts[1:]

        handler = None
        if isinstance(comandos, dict):
            handler = comandos.get(func_name)

        if handler is None or not callable(handler):
            return False, f"Comando '{func_name}' não encontrado", func_name

        def _coerce(s):
            s = str(s).strip()
            try:
                return int(s)
            except Exception:
                try:
                    return float(s.replace(",", "."))
                except Exception:
                    return s

        args = [_coerce(a) for a in arg_tokens]

        try:
            handler(*args)
            return True, None, func_name
        except Exception:
            return False, f'fatal: erro ao executar o comando "{func_name}"', func_name

    # alias opcional, se preferir estilo de instância:
    def le_comandos(self, raw, comandos):
        return self.LeComandos(raw, comandos)

    # ========= API pública compatível =========
    def add(self, msg, cor=(255, 255, 255), online_ctx=None, comandos=None, nome="Server"):
        """Equivale a adicionar_mensagem_terminal(...)"""
        agora = time.time()
        raw = str(msg).strip()
        is_cmd = raw.startswith("/")

        if is_cmd:
            ok, erro, _fname = self.LeComandos(raw, comandos)
            if not ok and erro:
                self.mensagens.append((f"[{nome}] {erro}", (255, 255, 0), agora))
        else:
            txt = f"[{nome}] {raw}"
            self.mensagens.append((txt, cor, agora))
            if isinstance(online_ctx, dict):
                online_ctx["MensagemOnline"] = raw

        if len(self.mensagens) > 10:
            self.mensagens = self.mensagens[-10:]

        self.ultimo_tempo_msg = agora

    def _clipboard_paste_text(self):
        txt = ""
        try:
            import pyperclip
            txt = pyperclip.paste() or ""
        except Exception:
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
        if txt:
            txt = txt.replace("\r\n", "\n").replace("\r", "\n")
            txt = " ".join(txt.split())
        return txt

    def _barra_texto(self, tela, fonte, x, y, w, alpha_bg, eventos=None, teclado_ctx=None):
        h = fonte.get_height() + 10
        rect = pygame.Rect(x, y, w, h)

        # fundo
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.COR_FUNDO_INPUT, surf.get_rect(), border_radius=h // 2)
        pygame.draw.rect(surf, self.COR_BORDA_INPUT, surf.get_rect(), width=1, border_radius=h // 2)
        surf.set_alpha(alpha_bg)
        tela.blit(surf, rect.topleft)

        HOLD_DELAY = 0.45
        REPEAT_RATE = 0.05

        modo_teclado_ativo = bool(teclado_ctx and teclado_ctx.get("ModoTeclado"))
        submitted = False

        if eventos and modo_teclado_ativo:
            for ev in eventos:
                if ev.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()

                    # COLAR
                    if (
                        ((mods & pygame.KMOD_CTRL) and ev.key == pygame.K_v) or
                        ((mods & pygame.KMOD_SHIFT) and ev.key == pygame.K_INSERT) or
                        ((mods & pygame.KMOD_CTRL) and ev.key == pygame.K_INSERT)
                    ):
                        pasted = self._clipboard_paste_text()
                        if pasted:
                            s = self.ui["input"]; i = self.ui["cursor"]
                            self.ui["input"] = s[:i] + pasted + s[i:]
                            self.ui["cursor"] = i + len(pasted)
                        continue

                    if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        submitted = True

                    elif ev.key == pygame.K_BACKSPACE:
                        if self.ui["cursor"] > 0:
                            s = self.ui["input"]; i = self.ui["cursor"]
                            self.ui["input"] = s[:i - 1] + s[i:]
                            self.ui["cursor"] -= 1
                        self._backspace["held"] = True
                        self._backspace["next_ms"] = pygame.time.get_ticks() + self._backspace["delay_ms"]

                    elif ev.key == pygame.K_DELETE:
                        s = self.ui["input"]; i = self.ui["cursor"]
                        if i < len(s):
                            self.ui["input"] = s[:i] + s[i + 1:]

                    elif ev.key == pygame.K_LEFT:
                        self.ui["cursor"] = max(0, self.ui["cursor"] - 1)

                    elif ev.key == pygame.K_RIGHT:
                        self.ui["cursor"] = min(len(self.ui["input"]), self.ui["cursor"] + 1)

                    elif ev.key == pygame.K_HOME:
                        self.ui["cursor"] = 0

                    elif ev.key == pygame.K_END:
                        self.ui["cursor"] = len(self.ui["input"])

                    elif ev.key == pygame.K_SPACE:
                        if not self.ui.get("space_down", False):
                            self.ui["space_down"] = True
                            self.ui["space_since"] = time.time()
                            self.ui["chaos_next"] = 0.0

                elif ev.type == pygame.KEYUP:
                    if ev.key == pygame.K_SPACE:
                        self.ui["space_down"] = False
                        self.ui["chaos_next"] = 0.0
                    elif ev.key == pygame.K_BACKSPACE:
                        self._backspace["held"] = False
                        self._backspace["next_ms"] = 0

                elif ev.type == pygame.TEXTINPUT:
                    txt = ev.text
                    if txt:
                        ignore_space_for_delete = (
                            self.ui.get("space_down", False)
                            and (time.time() - (self.ui.get("space_since") or time.time()) >= HOLD_DELAY)
                            and txt == " "
                        )
                        if not ignore_space_for_delete:
                            s = self.ui["input"]; i = self.ui["cursor"]
                            self.ui["input"] = s[:i] + txt + s[i:]
                            self.ui["cursor"] += len(txt)

        # backspace repeat
        if modo_teclado_ativo and self._backspace["held"]:
            now = pygame.time.get_ticks()
            if now >= self._backspace["next_ms"]:
                if self.ui["cursor"] > 0 and len(self.ui["input"]) > 0:
                    s = self.ui["input"]; i = self.ui["cursor"]
                    self.ui["input"] = s[:i - 1] + s[i:]
                    self.ui["cursor"] -= 1
                self._backspace["next_ms"] = now + self._backspace["rate_ms"]

        # espaço segurado => repetir delete
        if modo_teclado_ativo and self.ui.get("space_down", False):
            t_hold = time.time() - (self.ui.get("space_since") or time.time())
            if t_hold >= HOLD_DELAY:
                nowf = time.time()
                next_time = self.ui.get("chaos_next", 0.0)
                if nowf >= next_time:
                    if self.ui["cursor"] > 0 and len(self.ui["input"]) > 0:
                        s = self.ui["input"]; i = self.ui["cursor"]
                        self.ui["input"] = s[:i - 1] + s[i:]
                        self.ui["cursor"] -= 1
                    self.ui["chaos_next"] = nowf + REPEAT_RATE

        # texto
        texto = self.ui["input"]
        txt_surf = fonte.render(texto or "", True, self.COR_TEXTO)
        txt_surf.set_alpha(alpha_bg)
        tx = rect.x + 12
        ty = rect.y + (rect.height - txt_surf.get_height()) // 2
        tela.blit(txt_surf, (tx, ty))

        # cursor piscante
        if modo_teclado_ativo:
            tnow = time.time()
            if tnow - self.ui.get("last_blink", 0.0) > 0.5:
                self.ui["blink_on"] = not self.ui.get("blink_on", True)
                self.ui["last_blink"] = tnow
            if self.ui.get("blink_on", True):
                prefix = (texto or "")[:self.ui["cursor"]]
                px = tx + fonte.size(prefix)[0]
                pygame.draw.line(
                    tela, (255, 255, 255, alpha_bg),
                    (px, rect.y + 6), (px, rect.y + rect.height - 6), width=1
                )

        return submitted

    def atualizar(self, tela, fonte, Nome, tecla_ativacao=None, eventos=None,
             online_ctx=None, comandos=None, teclado_ctx=None):
        """Equivale à função terminal(...)."""
        # garantir chaves externas
        if teclado_ctx is not None:
            if "ModoTeclado" not in teclado_ctx:
                teclado_ctx["ModoTeclado"] = False
            if "ModoTecladoCache" not in teclado_ctx:
                teclado_ctx["ModoTecladoCache"] = teclado_ctx["ModoTeclado"]

        # entrada/controles
        if eventos and tecla_ativacao is not None:
            for ev in eventos:
                if ev.type == pygame.KEYDOWN and ev.key == tecla_ativacao:
                    self.ui["sticky"] = not self.ui["sticky"]
                    if self.ui["sticky"]:
                        self.ultimo_tempo_msg = time.time()
                    if teclado_ctx is not None:
                        teclado_ctx["ModoTeclado"] = not teclado_ctx["ModoTeclado"]

                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    if teclado_ctx is not None and teclado_ctx.get("ModoTeclado"):
                        teclado_ctx["ModoTeclado"] = False

                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if teclado_ctx is not None and teclado_ctx.get("ModoTeclado"):
                        teclado_ctx["ModoTeclado"] = False

        # queda do modo teclado: True->False => esconder imediatamente
        if teclado_ctx is not None:
            prev = teclado_ctx.get("ModoTecladoCache", False)
            cur  = teclado_ctx.get("ModoTeclado", False)
            if prev and not cur:
                self.ui["sticky"] = False
                self.ultimo_tempo_msg = 0
                teclado_ctx["ModoTecladoCache"] = cur
                return
            teclado_ctx["ModoTecladoCache"] = cur

        sticky = self.ui["sticky"]

        if not self.mensagens and not sticky:
            return

        alpha_bg = self._alpha(sticky=sticky)
        if alpha_bg <= 0:
            return

        # fundo do terminal
        fundo = pygame.Surface((self.TERMINAL_LARGURA, self.TERMINAL_ALTURA), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, alpha_bg))
        tela.blit(fundo, (0, 0))

        # layout texto + barra
        input_h = fonte.get_height() + 10
        area_texto_w = self.TERMINAL_LARGURA - 2 * self.MARGEM
        linha_altura = fonte.get_height() + 4
        area_lin_h = (self.TERMINAL_ALTURA - 3 * self.MARGEM - input_h)
        max_linhas_visiveis = max(1, area_lin_h // linha_altura)

        # quebra + filtro de últimas
        linhas = []
        for texto, cor, ts in self.mensagens:
            for l in self.quebrar_linhas(texto, fonte, area_texto_w):
                linhas.append((l, cor, ts))
        if len(linhas) > max_linhas_visiveis:
            linhas = linhas[-max_linhas_visiveis:]

        base_y = self.MARGEM + area_lin_h - (len(linhas) * linha_altura)
        y_texto = max(self.MARGEM, base_y)
        for l, cor, _ in linhas:
            surf = fonte.render(l, True, cor)
            surf.set_alpha(alpha_bg)
            tela.blit(surf, (self.MARGEM, y_texto))
            y_texto += linha_altura

        input_x = self.MARGEM
        input_y = self.TERMINAL_ALTURA - self.MARGEM - input_h
        submitted = self._barra_texto(
            tela, fonte, input_x, input_y, area_texto_w, alpha_bg,
            eventos=eventos, teclado_ctx=teclado_ctx
        )

        if submitted and teclado_ctx and teclado_ctx.get("ModoTeclado"):
            texto = self.ui["input"].strip()
            if texto:
                self.add(texto, self.COR_TEXTO, online_ctx=online_ctx, comandos=comandos, nome=Nome)
            self.ui["input"] = ""
            self.ui["cursor"] = 0
