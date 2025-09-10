import pygame

class Animação:
    def __init__(self, frames, posicao, intervalo=50, duracao=None,
                 ao_terminar=None, loop=True, ping_pong=False,
                 tamanho=1, inverted=False):
        """
        frames: lista de superfícies
        posicao: posição do centro
        tamanho: escala inicial
        inverted: se True, inverte horizontalmente os frames
        """
        self.frames = []
        for frame in frames:
            if inverted:
                frame = pygame.transform.flip(frame, True, False)  # espelha na horizontal
            frame = pygame.transform.scale(
                frame,
                (int(frame.get_width() * tamanho), int(frame.get_height() * tamanho))
            )
            self.frames.append(frame)

        self.pos = posicao
        self.intervalo = intervalo
        self.duracao = duracao
        self.ao_terminar = ao_terminar
        self.loop = loop
        self.ping_pong = ping_pong

        self.index = 0
        self.direcao = 1
        self.ultimo_tempo = pygame.time.get_ticks()
        self.inicio = self.ultimo_tempo

        self.chamou_callback = False
        self.ativo = True

    def atualizar(self, tela, nova_pos=None, multiplicador=1):
        """
        Desenha a animação na tela.
        multiplicador: fator de escala temporário aplicado apenas no frame atual
        (agora com cache de frames escalados por multiplicador)
        """
        if not self.ativo or not self.frames:
            return

        agora = pygame.time.get_ticks()

        # --------- avanço de índice (inalterado) ----------
        if agora - self.ultimo_tempo > self.intervalo:
            self.ultimo_tempo = agora
            if self.ping_pong:
                self.index += self.direcao
                if self.index >= len(self.frames):
                    self.index = len(self.frames) - 2
                    self.direcao = -1
                elif self.index < 0:
                    self.index = 1
                    self.direcao = 1
            elif self.loop:
                self.index = (self.index + 1) % len(self.frames)
            else:
                self.index = min(self.index + 1, len(self.frames) - 1)

        # --------- seleção do frame com cache de escala ----------
        if 0 <= self.index < len(self.frames):
            # chave de cache arredondada para evitar thrash com floats tipo 1.999999
            try:
                m_key = 1.0 if multiplicador == 1 else round(float(multiplicador), 3)
            except Exception:
                m_key = 1.0

            # prepara atributos de cache se ainda não existirem
            if not hasattr(self, "_cache_mult"):
                self._cache_mult = None
            if not hasattr(self, "_cache_frames"):
                self._cache_frames = None

            if m_key == 1.0:
                # usa frames originais; limpa cache para economizar memória
                frames_to_use = self.frames
                if self._cache_mult is not None:
                    self._cache_mult = None
                    self._cache_frames = None
            else:
                # (re)gera cache somente se multiplicador mudou
                if self._cache_mult != m_key or self._cache_frames is None:
                    scaled = []
                    # usa o multiplicador exato para cálculo de tamanho
                    mul = float(multiplicador)
                    for f in self.frames:
                        w = max(1, int(round(f.get_width()  * mul)))
                        h = max(1, int(round(f.get_height() * mul)))
                        # se o tamanho é idêntico ao original, reaproveita o frame original
                        if (w, h) == f.get_size():
                            scaled.append(f)
                        else:
                            # scale é mais leve que smoothscale por frame
                            scaled.append(pygame.transform.scale(f, (w, h)))
                    self._cache_frames = scaled
                    self._cache_mult   = m_key
                frames_to_use = self._cache_frames

            frame = frames_to_use[self.index]

            pos_desenho = nova_pos if nova_pos is not None else self.pos
            rect = frame.get_rect(center=pos_desenho)
            tela.blit(frame, rect)

        # --------- finalização baseada em duração (inalterado) ----------
        if self.duracao is not None:
            if not self.chamou_callback and agora - self.inicio >= self.duracao * 0.76:
                if self.ao_terminar:
                    self.ao_terminar()
                self.chamou_callback = True

            if agora - self.inicio >= self.duracao:
                self.ativo = False

    def finalizado(self):
        return not self.ativo

    def apagar(self):
        self.ativo = False

class PokemonAnimator:
    def __init__(self, pokemon, frames, pos, inverted=False, tamanho=1.0):
        self.pokemon = pokemon
        self.pos = pos  # posição inicial (igual Animação)

        # parâmetros novos
        self.inverted = bool(inverted)
        self.velocidade = 3.0
        self.tamanho = float(tamanho) if tamanho else 1.0

        # prepara frames aplicando invert e escala
        self.frames = []
        for frame in frames:
            f = frame
            if self.inverted:
                f = pygame.transform.flip(f, True, False)
            if self.tamanho != 1.0:
                w = max(1, int(round(f.get_width()  * self.tamanho)))
                h = max(1, int(round(f.get_height() * self.tamanho)))
                f = pygame.transform.scale(f, (w, h))
            self.frames.append(f)

        self.frame_index = 0
        self.timer = 0.0
        self.rect = None

        # intervalo base
        self._intervalo_base = 0.1

        # --------- SISTEMA DE AÇÕES / ANIMAÇÕES ---------
        # _acao: None ou dict com { "tipo": "tomar_dano"/"avanco", "t":..., "dur":..., ... }
        self._acao = None
        self._gat_pct = 0.6          # percentual de progresso para disparar gatilho (0..1)
        self._gat_disparado = False  # se já disparou no ciclo atual
        self._on_gatilho = None      # callback opcional
        # -------------------------------------------------

    # ================= API DE CONTROLE (thread-safe o suficiente p/ set simples) =================
    def iniciar_tomar_dano(self, dur=0.30, freq=12.0, gatilho_pct=0.6, on_gatilho=None):
        """Piscada vermelha por 'dur' segundos. freq = piscadas por segundo."""
        self._acao = {
            "tipo": "tomar_dano",
            "t": 0.0,
            "dur": max(0.01, float(dur)),
            "freq": float(freq)
        }
        self._configurar_gatilho(gatilho_pct, on_gatilho)

    def iniciar_avanco(self, desloc, altura=24, dur=0.40, gatilho_pct=0.6, on_gatilho=None):
        """
        Avança numa parábola e retorna ao ponto.
        desloc: (dx, dy) direção máxima no ápice (meio da animação).
        altura: quanto "sobe" no meio (efeito salto).
        """
        dx, dy = desloc
        self._acao = {
            "tipo": "avanco",
            "t": 0.0,
            "dur": max(0.01, float(dur)),
            "dx": float(dx),
            "dy": float(dy),
            "altura": float(altura)
        }
        self._configurar_gatilho(gatilho_pct, on_gatilho)

    # ---------------------- NOVAS AÇÕES ----------------------

    def iniciar_curar(self, dur=0.30, freq=12.0, gatilho_pct=0.6, on_gatilho=None):
        """Piscada verde por 'dur' segundos. freq = piscadas por segundo."""
        self._acao = {
            "tipo": "curar",
            "t": 0.0,
            "dur": max(0.01, float(dur)),
            "freq": float(freq)
        }
        self._configurar_gatilho(gatilho_pct, on_gatilho)

    def iniciar_investida(self, desloc, dur=0.28, gatilho_pct=0.6, on_gatilho=None):
        """
        Avança em linha reta e retorna (sem arco).
        desloc: (dx, dy) deslocamento máximo no meio da animação.
        """
        dx, dy = desloc
        self._acao = {
            "tipo": "investida",
            "t": 0.0,
            "dur": max(0.01, float(dur)),
            "dx": float(dx),
            "dy": float(dy)
        }
        self._configurar_gatilho(gatilho_pct, on_gatilho)

    def iniciar_disparo(self, alvo_pos, proj_img=None, dur=0.50, gatilho_pct=0.5, on_gatilho=None):
        """
        Cresce até +20% até o 'gatilho' e então dispara projétil do atacante até 'alvo_pos'.
        - alvo_pos: (x, y) na tela/mundo onde o projétil deve chegar.
        - proj_img: pygame.Surface opcional para o projétil. Se None, usa genérico.
        - dur: duração total (escala + voo do projétil).
        """
        self._acao = {
            "tipo": "disparo",
            "t": 0.0,
            "dur": max(0.05, float(dur)),
            "alvo": (float(alvo_pos[0]), float(alvo_pos[1])),
            "crescimento": 1.20,       # +20%
            "gatilho_fired": False
        }
        # prepara estrutura do projétil
        self._projetil = {
            "ativo": False,
            "pos": None,                      # (x, y) atual
            "ini": None,                      # origem
            "fim": self._acao["alvo"],        # destino
            "t": 0.0,
            "dur": max(0.10, self._acao["dur"] * (1.0 - float(gatilho_pct))),
            "img": proj_img,
            "tamanho": 12                     # raio do genérico
        }
        self._configurar_gatilho(gatilho_pct, on_gatilho)

    # --- NOVAS: SOFRERGOLPE (overlay de frames) e CARTUCHO (surface que sai do centro) ---

    def iniciar_sofrergolpe(self, frames, fps=20, offset=(0, 0)):
        """
        Reproduz 'frames' por cima do pokémon (uma vez).
        - frames: lista de pygame.Surface.
        - fps: quadros por segundo.
        - offset: deslocamento (x, y) relativo ao centro do pokémon.
        """
        if not frames:
            return
        self._atk_fx = {
            "ativo": True,
            "frames": frames,
            "fps": max(1, int(fps)),
            "t": 0.0,
            "offset": (int(offset[0]), int(offset[1]))
        }

    def iniciar_cartucho(self, cartucho_surf, lado="dir", dur=0.9, altura=140, dx=80, scale_ini=0.6, scale_fim=1.0):
        """
        Faz o 'cartucho_surf' surgir do centro do pokémon, aumentar e subir até o topo,
        deslocando-se para a direita/esquerda com curva parabólica e sumindo gradualmente.
        - lado: 'dir'/'esq' ou 1/-1.
        - dur: duração total da animação.
        - altura: quanto sobe (px).
        - dx: deslocamento horizontal total (px).
        """
        if cartucho_surf is None:
            return
        dir_sign = 1
        if isinstance(lado, (int, float)):
            dir_sign = 1 if lado >= 0 else -1
        else:
            lado_s = str(lado).lower()
            if "esq" in lado_s or "left" in lado_s:
                dir_sign = -1

        self._cartucho = {
            "ativo": True,
            "surf": cartucho_surf.convert_alpha(),
            "t": 0.0,
            "dur": max(0.15, float(dur)),
            "altura": float(altura),
            "dx": float(dx) * dir_sign,
            "s0": float(scale_ini),
            "s1": float(scale_fim),
            "orig": None  # será definido a partir do último draw do pokémon
        }

    # ---------------------------------------------------------------------------------------------

    def acao_em_andamento(self):
        return self._acao is not None

    def progresso_acao(self):
        """Retorna progresso 0..1 da ação atual (0 se não há ação)."""
        if not self._acao:
            return 0.0
        return min(1.0, self._acao["t"] / self._acao["dur"])

    def poll_acao_gatilho(self):
        """
        Retorna True exatamente uma vez quando o progresso cruza o gatilho.
        Útil p/ o leitor de log encadear a próxima animação.
        """
        if self._gat_disparado:
            self._gat_disparado = False
            return True
        return False

    def _configurar_gatilho(self, gatilho_pct, on_gatilho):
        self._gat_pct = float(max(0.0, min(1.0, gatilho_pct)))
        self._gat_disparado = False
        self._on_gatilho = on_gatilho

    # =============================================================================================

    def atualizar(self, novos_dados):
        self.pokemon.update(novos_dados)

    def _atualizar_acao(self, dt):
        """Avança o tempo da ação e dispara gatilho/encerra quando devido."""
        if not self._acao:
            # atualiza overlays independentes
            if hasattr(self, "_projetil"):
                self._step_projetil(dt)
            if hasattr(self, "_atk_fx"):
                if self._atk_fx.get("ativo"):
                    self._atk_fx["t"] += dt
                    total = len(self._atk_fx["frames"])
                    if int(self._atk_fx["t"] * self._atk_fx["fps"]) >= total:
                        self._atk_fx["ativo"] = False
            if hasattr(self, "_cartucho"):
                if self._cartucho.get("ativo"):
                    self._cartucho["t"] += dt
                    if self._cartucho["t"] >= self._cartucho["dur"]:
                        self._cartucho["ativo"] = False
            return

        a = self._acao
        a["t"] += dt

        prog = min(1.0, a["t"] / a["dur"])

        # dispara gatilho ao cruzar limiar
        if (not self._gat_disparado) and (prog >= self._gat_pct):
            self._gat_disparado = True
            if callable(self._on_gatilho):
                try:
                    self._on_gatilho(self)  # opcional
                except Exception:
                    pass  # não derrubar o loop por callback

        # step dos overlays/projétil
        if hasattr(self, "_projetil"):
            self._step_projetil(dt)
        if hasattr(self, "_atk_fx") and self._atk_fx.get("ativo"):
            self._atk_fx["t"] += dt
            total = len(self._atk_fx["frames"])
            if int(self._atk_fx["t"] * self._atk_fx["fps"]) >= total:
                self._atk_fx["ativo"] = False
        if hasattr(self, "_cartucho") and self._cartucho.get("ativo"):
            self._cartucho["t"] += dt
            if self._cartucho["t"] >= self._cartucho["dur"]:
                self._cartucho["ativo"] = False

        # fim da ação
        if a["t"] >= a["dur"]:
            self._acao = None
            # cooldown opcional poderia entrar aqui

    def _efeitos_acao(self, sprite, pos_base):
        """
        Calcula (sprite_mod, pos_mod) a partir da ação atual.
        - tomar_dano: piscada vermelha
        - curar: piscada verde
        - avanco: offset parabólico e leve squash opcional (mantido simples)
        - investida: offset linear (reta)
        - disparo: scale-up até gatilho; projétil é desenhado em desenhar_extras(...)
        """
        if not self._acao:
            # ainda assim salve a caixa para overlays
            self._ultimo_draw = {"pos": pos_base, "size": sprite.get_size()}
            return sprite, pos_base

        a = self._acao
        prog = min(1.0, a["t"] / a["dur"])

        # posição final default
        x, y = pos_base
        sprite_mod = sprite

        if a["tipo"] == "tomar_dano":
            # piscada: liga/desliga conforme freq
            contador = int((prog * a["dur"]) * a["freq"] * 2)
            blink_on = (contador % 2 == 0)
            if blink_on:
                overlay = pygame.Surface(sprite.get_size(), flags=pygame.SRCALPHA)
                overlay.fill((255, 64, 64, 140))  # translúcido vermelho
                sprite_mod = sprite.copy()
                sprite_mod.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        elif a["tipo"] == "curar":
            contador = int((prog * a["dur"]) * a["freq"] * 2)
            blink_on = (contador % 2 == 0)
            if blink_on:
                overlay = pygame.Surface(sprite.get_size(), flags=pygame.SRCALPHA)
                overlay.fill((64, 255, 64, 140))  # translúcido verde
                sprite_mod = sprite.copy()
                sprite_mod.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        elif a["tipo"] == "avanco":
            # trajetória parabólica indo e voltando
            curva = -4 * (prog - 0.5) ** 2 + 1.0
            dx = a["dx"] * max(0.0, curva)
            dy = a["dy"] * max(0.0, curva)
            lift = -a["altura"] * (4 * prog * (1 - prog))  # 0 nas pontas, -altura no meio
            x += dx
            y += dy + lift

        elif a["tipo"] == "investida":
            # mesma curva de ida/volta, mas sem lift (reta)
            curva = -4 * (prog - 0.5) ** 2 + 1.0
            dx = a["dx"] * max(0.0, curva)
            dy = a["dy"] * max(0.0, curva)
            x += dx
            y += dy

        elif a["tipo"] == "disparo":
            # scale-up até o gatilho
            escala_max = a.get("crescimento", 1.20)
            if self._gat_pct > 1e-6:
                sprog = min(1.0, prog / self._gat_pct)
            else:
                sprog = 1.0
            scale = 1.0 + (escala_max - 1.0) * sprog
            scale = max(1.0, min(escala_max, scale))

            if abs(scale - 1.0) > 1e-3:
                w, h = sprite.get_size()
                nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
                sprite_mod = pygame.transform.smoothscale(sprite, (nw, nh))
                # mantém o centro visual ao escalar
                x -= (nw - w) // 2
                y -= (nh - h) // 2

            # quando cruzar o gatilho, arma o projétil exatamente 1x
            if (not a.get("gatilho_fired")) and prog >= self._gat_pct:
                a["gatilho_fired"] = True
                p = getattr(self, "_projetil", None)
                if p is not None:
                    p["ativo"] = True
                    # origem ≈ centro do sprite
                    w0, h0 = sprite_mod.get_size()
                    p["ini"] = (x + w0 * 0.5, y + h0 * 0.35)
                    p["pos"] = p["ini"]
                    p["t"] = 0.0

        # registra último draw para overlays (sofrergolpe e cartucho)
        self._ultimo_draw = {"pos": (x, y), "size": sprite_mod.get_size()}
        return sprite_mod, (x, y)

    # ================= EXTRAS: desenhar overlays (projétil, golpe, cartucho) =================

    def desenhar_extras(self, tela):
        """Chame após blitar o sprite do pokémon."""
        # PROJÉTIL (se existir, já gerenciado por iniciar_disparo/_step_projetil)
        p = getattr(self, "_projetil", None)
        if p and p.get("ativo"):
            x, y = p["pos"]
            if p["img"] is not None:
                img = p["img"]
                rect = img.get_rect(center=(int(x), int(y)))
                tela.blit(img, rect.topleft)
            else:
                r = int(p.get("tamanho", 12))
                superficie = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(superficie, (255, 255, 255, 220), (r, r), r)
                pygame.draw.circle(superficie, (0, 180, 255, 220), (r, r), r//2)
                tela.blit(superficie, (int(x - r), int(y - r)))

        # SOFRERGOLPE (overlay de frames sobre o pokémon)
        fx = getattr(self, "_atk_fx", None)
        if fx and fx.get("ativo") and hasattr(self, "_ultimo_draw"):
            (px, py) = self._ultimo_draw["pos"]
            (sw, sh) = self._ultimo_draw["size"]
            cx = px + sw * 0.5 + fx["offset"][0]
            cy = py + sh * 0.35 + fx["offset"][1]

            idx = int(fx["t"] * fx["fps"])
            if 0 <= idx < len(fx["frames"]):
                frame = fx["frames"][idx]
                rect = frame.get_rect(center=(int(cx), int(cy)))
                tela.blit(frame, rect.topleft)

        # CARTUCHO (sai do centro, cresce, curva p/ lado e sobe até o topo + fade)
        c = getattr(self, "_cartucho", None)
        if c and c.get("ativo") and hasattr(self, "_ultimo_draw"):
            (px, py) = self._ultimo_draw["pos"]
            (sw, sh) = self._ultimo_draw["size"]
            # origem no centro "alto" do pokémon (levemente acima do meio)
            orig = (px + sw * 0.5, py + sh * 0.30)
            if c["orig"] is None:
                c["orig"] = orig
            else:
                orig = c["orig"]

            s = max(0.0, min(1.0, c["t"] / c["dur"]))
            # posição (parabólica no x e linear no y até o topo)
            x = orig[0] + c["dx"] * (s ** 2)
            y = orig[1] - c["altura"] * s

            # escala (surge pequeno e cresce)
            esc = c["s0"] + (c["s1"] - c["s0"]) * s
            src = c["surf"]
            w0, h0 = src.get_size()
            nw, nh = max(1, int(w0 * esc)), max(1, int(h0 * esc))
            img = pygame.transform.smoothscale(src, (nw, nh))

            # fade out
            alpha = int(255 * (1.0 - s))
            img.set_alpha(max(0, min(255, alpha)))

            rect = img.get_rect(center=(int(x), int(y)))
            tela.blit(img, rect.topleft)

    def desenhar(self, dt, tela, nova_pos=None, multiplicador=1.0):
        # --- animação de frames (velocidade) ---
        self.timer += dt
        mult_vel = self.velocidade if self.velocidade > 0 else 1e-6
        intervalo = self._intervalo_base / mult_vel
        if self.timer > intervalo:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.timer = 0.0

        # pega frame atual
        sprite = self.frames[self.frame_index]

        # aplica multiplicador de escala temporário
        if multiplicador != 1.0:
            w = max(1, int(round(sprite.get_width()  * multiplicador)))
            h = max(1, int(round(sprite.get_height() * multiplicador)))
            sprite = pygame.transform.scale(sprite, (w, h))

        # posição base
        pos_base = nova_pos if nova_pos is not None else self.pos

        # atualiza ação e aplica efeitos (offsets / tint)
        self._atualizar_acao(dt)
        sprite, pos_desenho = self._efeitos_acao(sprite, pos_base)

        # desenha sprite
        rect = sprite.get_rect(center=pos_desenho)
        self.rect = tela.blit(sprite, rect)

        # ===================== BARRAS ESTILO TFT =====================
        vida      = float(self.pokemon["Vida"])
        energia   = float(self.pokemon["Energia"])
        vida_max  = max(1.0, float(self.pokemon["VidaMax"]))
        ene_max   = max(1.0, float(self.pokemon["Ene"]))

        # centro acima do pokémon
        largura  = 70
        offset_y = -16

        # hover: engrossa levemente
        mouse_pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse_pos)
        h_vida, h_ene = (14, 7) if hover else (12, 6)

        # base centralizada
        cx = rect.centerx
        x0 = int(cx - largura // 2)
        y0 = int(rect.top + offset_y)

        # Cores
        cor_borda = (0, 0, 0)
        cor_fundo = (24, 24, 24)   # fundo escuro tft-like
        cor_vida  = (0, 200, 0)
        cor_ene   = (0, 0, 200)

        # raios de borda (cantinhos arredondados leves)
        br_vida = min(h_vida // 2, 6)
        br_ene  = min(h_ene  // 2, 6)

        # percentuais
        vida_pct = max(0.0, min(1.0, vida / vida_max))
        ene_pct  = max(0.0, min(1.0, energia / ene_max))

        # ----------------- VIDA (barra superior) -----------------
        # fundo + borda
        r_bg = pygame.Rect(x0, y0, largura, h_vida)
        pygame.draw.rect(tela, cor_fundo, r_bg, border_radius=br_vida)
        pygame.draw.rect(tela, cor_borda, r_bg, width=1, border_radius=br_vida)

        # preenchimento
        fill_w = int(largura * vida_pct)
        if fill_w > 0:
            r_fill = pygame.Rect(x0, y0, fill_w, h_vida)
            pygame.draw.rect(tela, cor_vida, r_fill, border_radius=br_vida)

            # divisórias pretas (apenas sobre a parte preenchida)
            passo = 30.0
            top_i = max(0, int(passo))  # evita loop vazio
            for i in range(top_i, int(vida_max), int(passo)):
                px = x0 + int(round(largura * (i / vida_max)))
                if px <= x0 + fill_w - 1:
                    # não tocar a borda superior/inferior para ficar "TFT-like"
                    pygame.draw.line(tela, cor_borda, (px, y0 + 1), (px, y0 + h_vida - 2))

        # ----------------- ENERGIA (barra inferior) -----------------
        y1 = y0 + h_vida + 2
        r_bg2 = pygame.Rect(x0, y1, largura, h_ene)
        pygame.draw.rect(tela, cor_fundo, r_bg2, border_radius=br_ene)
        pygame.draw.rect(tela, cor_borda, r_bg2, width=1, border_radius=br_ene)

        fill_w2 = int(largura * ene_pct)
        if fill_w2 > 0:
            r_fill2 = pygame.Rect(x0, y1, fill_w2, h_ene)
            pygame.draw.rect(tela, cor_ene, r_fill2, border_radius=br_ene)

            # divisórias pretas (apenas na parte preenchida)
            passo2 = 15.0
            top_i2 = max(0, int(passo2))
            for i in range(top_i2, int(ene_max), int(passo2)):
                px = x0 + int(round(largura * (i / ene_max)))
                if px <= x0 + fill_w2 - 1:
                    pygame.draw.line(tela, cor_borda, (px, y1 + 1), (px, y1 + h_ene - 2))
        # ============================================================

