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

        # fim da ação
        if a["t"] >= a["dur"]:
            self._acao = None
            # se quiser, poderia deixar um pequeno cooldown aqui; mantive simples

    def _efeitos_acao(self, sprite, pos_base):
        """
        Calcula (sprite_mod, pos_mod) a partir da ação atual.
        - tomar_dano: piscada vermelha
        - avanco: offset parabólico e leve squash opcional (mantido simples)
        """
        if not self._acao:
            return sprite, pos_base

        a = self._acao
        prog = min(1.0, a["t"] / a["dur"])

        # posição final default
        x, y = pos_base
        sprite_mod = sprite

        if a["tipo"] == "tomar_dano":
            # piscada: liga/desliga conforme freq
            # liga quando floor(prog * dur * freq * 2) é par -> efeito “blink”
            # Como nosso prog ∈ [0,1], usamos contador = floor(prog * freq * 2)
            contador = int((prog * a["dur"]) * a["freq"] * 2)
            blink_on = (contador % 2 == 0)
            if blink_on:
                # cria overlay vermelho
                overlay = pygame.Surface(sprite.get_size(), flags=pygame.SRCALPHA)
                overlay.fill((255, 64, 64, 140))  # levemente translúcido
                # compõe no sprite atual (copiando p/ não destruir frame original)
                sprite_mod = sprite.copy()
                sprite_mod.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        elif a["tipo"] == "avanco":
            # trajetória parabólica indo e voltando: pico no meio (prog=0.5)
            # fator curva: -4*(p-0.5)^2 + 1 -> 0 nas bordas, 1 no meio
            curva = -4 * (prog - 0.5) ** 2 + 1.0
            dx = a["dx"] * max(0.0, curva)
            dy = a["dy"] * max(0.0, curva)
            # salto vertical (para cima é negativo em Y)
            lift = -a["altura"] * (4 * prog * (1 - prog))  # 0 nas pontas, -altura no meio
            x += dx
            y += dy + lift

        return sprite_mod, (x, y)

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

        # desenha
        rect = sprite.get_rect(center=pos_desenho)
        self.rect = tela.blit(sprite, rect)

        # --- barras (mesma lógica) ---
        vida = self.pokemon["Vida"]
        energia = self.pokemon["Energia"]
        vida_max = self.pokemon["VidaMax"]
        ene_max = self.pokemon["Ene"]

        largura = 100
        offset_y = -18

        # hover
        mouse_pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse_pos)
        h_vida, h_ene = (6, 4) if hover else (3, 2)

        rx, ry = rect.topleft

        # barra vida
        vida_pct = max(0, float(vida)) / max(1, float(vida_max))
        pygame.draw.rect(tela, (0, 0, 0), (rx, ry + offset_y, largura, h_vida))
        pygame.draw.rect(tela, (0, 200, 0), (rx, ry + offset_y, int(largura * vida_pct), h_vida))
        for i in range(30, int(vida_max), 30):
            px = rx + int(largura * (i / vida_max))
            pygame.draw.line(tela, (0, 0, 0), (px, ry + offset_y), (px, ry + offset_y + h_vida))

        # barra energia
        offset_y2 = offset_y + h_vida + 2
        ene_pct = max(0, float(energia)) / max(1, float(ene_max))
        pygame.draw.rect(tela, (0, 0, 0), (rx, ry + offset_y2, largura, h_ene))
        pygame.draw.rect(tela, (0, 0, 200), (rx, ry + offset_y2, int(largura * ene_pct), h_ene))
        for i in range(15, int(ene_max), 15):
            px = rx + int(largura * (i / ene_max))
            pygame.draw.line(tela, (0, 0, 0), (px, ry + offset_y2), (px, ry + offset_y2 + h_ene))
