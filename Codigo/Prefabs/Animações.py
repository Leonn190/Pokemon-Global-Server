import pygame, math, random

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
        self.pos = pos  # canto superior esquerdo inicial

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

        # # posição central (x, y) do sprite inicial
        # if self.frames:
        #     w, h = self.frames[0].get_size()
        #     self.posCenter = (self.pos[0] + w // 2, self.pos[1] + h // 2)
        # else:
        self.posCenter = self.pos

    # --------- SISTEMA DE AÇÕES / ANIMAÇÕES ---------
        self._acao = None
        self.Continue = True          # ← único “sinal” de encadeamento
        self._pct_continue = 1.0      # limiar para liberar Continue
        # -------------------------------------------------

    # ===================== HELPERS DE CONTROLE ===================================
    def _armar_continue(self, pct):
        """Arma o 'Continue': ao iniciar QUALQUER ação/overlay, zera e define o limiar."""
        self._pct_continue = float(max(0.0, min(1.0, pct)))
        self.Continue = False

    def _tentar_liberar_continue(self, progresso):
        """Se ainda não liberou e o progresso cruzou o limiar, libera o Continue."""
        if (not self.Continue) and (float(progresso) >= self._pct_continue):
            self.Continue = True
    # ============================================================================

    # ================= API DE CONTROLE (thread-safe o suficiente p/ set simples) ================= 
    def iniciar_tomardano(self, dur=0.30, freq=12.0, pct_continue=0.6):
        """Piscada vermelha por 'dur' segundos. freq = piscadas por segundo."""
        self._acao = {
            "tipo": "tomar_dano",
            "t": 0.0,
            "dur": max(0.01, float(dur)),
            "freq": float(freq),
            "pct_continue": float(pct_continue),
        }
        self._armar_continue(pct_continue)

    def iniciar_avanco(self, alvo_pos, altura=240, dur=0.40, pct_continue=0.6):
        """
        Avança em parábola até 'alvo_pos' (ápice no meio) e retorna à origem.
        alvo_pos: (ax, ay) absoluto no mesmo referencial do draw.
        altura: quanto "sobe" no meio (efeito salto).
        """
        ax, ay = alvo_pos
        self._acao = {
            "tipo": "avanco",
            "t": 0.0,
            "dur": max(0.01, float(dur)),
            "alvo": (float(ax), float(ay)),
            "orig": None,            # setado no primeiro draw
            "dx": None, "dy": None,  # calculados no primeiro draw
            "altura": float(altura),
            "pct_continue": float(pct_continue),
        }
        self._armar_continue(pct_continue)

    # ---------------------- NOVAS AÇÕES ----------------------

    def iniciar_curar(self, dur=0.30, freq=12.0, pct_continue=0.6):
        """Piscada verde por 'dur' segundos. freq = piscadas por segundo."""
        self._acao = {
            "tipo": "curar",
            "t": 0.0,
            "dur": max(0.01, float(dur)),
            "freq": float(freq),
            "pct_continue": float(pct_continue),
        }
        self._armar_continue(pct_continue)

    def iniciar_investida(self, alvo_pos, dur=0.28, pct_continue=0.6):
        """
        Avança em linha reta até 'alvo_pos' e retorna (sem arco).
        alvo_pos: (ax, ay) absoluto no mesmo referencial do draw.
        """
        ax, ay = alvo_pos
        self._acao = {
            "tipo": "investida",
            "t": 0.0,
            "dur": max(0.01, float(dur)),
            "alvo": (float(ax), float(ay)),
            "orig": None,            # setado no primeiro draw
            "dx": None, "dy": None,  # calculados no primeiro draw
            "pct_continue": float(pct_continue),
        }
        self._armar_continue(pct_continue)

    def iniciar_disparo(self, alvo_pos, proj_img=None, dur=0.50, pct_continue=0.5):
        """
        Cresce até +~10% até 'pct_continue' e então dispara projétil até 'alvo_pos'.
        - alvo_pos: (x, y) na tela/mundo onde o projétil deve chegar.
        - proj_img: pygame.Surface opcional para o projétil. Se None, usa genérico.
        - dur: duração total (escala + voo do projétil).
        """
        self._acao = {
            "tipo": "disparo",
            "t": 0.0,
            "dur": max(0.05, float(dur)),
            "alvo": (float(alvo_pos[0]), float(alvo_pos[1])),
            "crescimento": 1.1,            # ~+10%
            "proj_lancado": False,
            "pct_continue": float(pct_continue),
        }
        # prepara estrutura do projétil (tempo proporcional à “cauda” pós-continue)
        self._projetil = {
            "ativo": False,
            "pos": None,                           # (x, y) atual
            "ini": None,                           # origem
            "fim": self._acao["alvo"],             # destino
            "t": 0.0,
            "dur": max(0.10, self._acao["dur"] * (1.0 - float(pct_continue))),
            "img": proj_img,
            "tamanho": 12                          # raio do genérico
        }
        self._armar_continue(pct_continue)

    # --- OVERLAYS (sem gatilhos; também podem armar o Continue) ---

    def iniciar_aplicar_golpe(self, pos, frames, fps=20, offset=(0, 0), pct_continue=0.5,
                            scale=1.0, angle=0.0):
        """
        Aplica o efeito de golpe (lista de frames) centrado em `pos` (x, y).
        - frames: lista de pygame.Surface
        - fps: quadros/segundo
        - offset: deslocamento (x, y) relativo ao centro passado
        - scale, angle: opcionais (mesma ideia do seu _draw atual)
        """
        if not frames or not pos:
            return
        fps_i = max(1, int(fps))
        dur_total = max(1e-3, len(frames) / float(fps_i))
        self._atk_fx = {
            "ativo": True,
            "frames": frames,
            "fps": fps_i,
            "t": 0.0,
            "dur": dur_total,
            "pos": (int(pos[0]), int(pos[1])),
            "offset": (int(offset[0]), int(offset[1])),
            "pct_continue": float(pct_continue),
            "scale": float(scale),
            "angle": float(angle),
        }
        self._armar_continue(pct_continue)

    def iniciar_cartucho(self, cartucho_surf, lado="dir", dur=1.05, altura=140, dx=80,
                         scale_ini=0.6, scale_fim=1.0, pct_continue=0.5):
        """
        Faz o 'cartucho_surf' surgir do centro do pokémon, aumentar e subir até o topo,
        deslocando-se para a direita/esquerda com curva parabólica e sumindo gradualmente.
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
            "orig": None,  # será definido a partir do último draw do pokémon
            "pct_continue": float(pct_continue),
        }
        self._armar_continue(pct_continue)

    def iniciar_buff(self, dur=0.9, qtd=6, area=(60, 40), cor=(90, 200, 255),
                     pct_continue=0.6, debuff=False):
        """
        Desenha setinhas subindo (ou descendo, se debuff) ao redor do pokémon durante 'dur'.
        - qtd: número de setas.
        - area: (largura, altura) do campo.
        - cor: cor das setas.
        """
        self._buff = {
            "ativo": True,
            "t": 0.0,
            "dur": max(0.15, float(dur)),
            "qtd": max(1, int(qtd)),
            "area": (float(area[0]), float(area[1])),
            "cor": cor,
            "orig": None,  # setado no draw
            "debuff": bool(debuff),
            "pct_continue": float(pct_continue),
        }
        self._armar_continue(pct_continue)

    # ---------------------------------------------------------------------------------------------

    def acao_em_andamento(self):
        return self._acao is not None

    def progresso_acao(self):
        """Retorna progresso 0..1 da ação atual (0 se não há ação)."""
        if not self._acao:
            return 0.0
        return min(1.0, self._acao["t"] / self._acao["dur"])

    # (Opcional) Alias p/ compat: se algum código antigo chamar, devolvemos o estado atual
    def poll_acao_gatilho(self):
        """Compat: não há mais gatilhos. Use 'Continue'. Aqui retornamos o booleano atual."""
        return bool(self.Continue)

    # =============================================================================================

    def _atualizar_acao(self, dt):
        """Avança o tempo da ação e libera 'Continue' quando cruzar o limiar."""
        # ---------- overlays independentes (sempre atualizam) ----------
        if hasattr(self, "_projetil"):
            self._step_projetil(dt)

        # sofrer golpe
        if hasattr(self, "_atk_fx") and self._atk_fx.get("ativo"):
            fx = self._atk_fx
            fx["t"] += dt
            prog_fx = min(1.0, fx["t"] / fx["dur"])
            self._tentar_liberar_continue(prog_fx)
            total = len(fx["frames"])
            if int(fx["t"] * fx["fps"]) >= total or fx["t"] >= fx["dur"]:
                fx["ativo"] = False

        # cartucho
        if hasattr(self, "_cartucho") and self._cartucho.get("ativo"):
            c = self._cartucho
            c["t"] += dt
            prog_c = min(1.0, c["t"] / c["dur"])
            self._tentar_liberar_continue(prog_c)
            if c["t"] >= c["dur"]:
                c["ativo"] = False

        # buff
        if hasattr(self, "_buff") and self._buff.get("ativo"):
            b = self._buff
            b["t"] += dt
            prog_b = min(1.0, b["t"] / b["dur"])
            self._tentar_liberar_continue(prog_b)
            if b["t"] >= b["dur"]:
                b["ativo"] = False

        # ---------- ação principal ----------
        if not self._acao:
            return

        a = self._acao
        a["t"] += dt
        prog = min(1.0, a["t"] / a["dur"])

        # libera Continue conforme limiar definido na própria ação
        self._tentar_liberar_continue(prog)

        # fim da ação
        if a["t"] >= a["dur"]:
            self._acao = None
            # cooldown opcional poderia entrar aqui

    
    def _efeitos_acao(self, sprite, pos_base):
        """
        Orquestrador: decide qual animação aplicar e retorna (sprite_mod, pos_mod).
        Também atualiza _ultimo_draw para os overlays.
        """
        # fallback: nada ativo
        if not self._acao:
            self._ultimo_draw = {"pos": pos_base, "size": sprite.get_size()}
            return sprite, pos_base

        a = self._acao
        prog = min(1.0, a["t"] / a["dur"]) if a.get("dur") else 1.0

        # defaults
        x, y = pos_base
        sprite_mod = sprite

        # ——— ações puras no sprite ———
        if a["tipo"] == "tomar_dano":
            sprite_mod, (x, y) = self._anim_fluxo(sprite, (x, y), a, prog,
                                                  cor=(255,50,40), wash=(50,6,6), dir_sign=+1)
        elif a["tipo"] == "curar":
            sprite_mod, (x, y) = self._anim_fluxo(sprite, (x, y), a, prog,
                                                  cor=(60,255,190), wash=(6,32,26), dir_sign=-1)
        elif a["tipo"] == "avanco":
            sprite_mod, (x, y) = self._anim_avanco(sprite, (x, y), a, prog)
        elif a["tipo"] == "investida":
            sprite_mod, (x, y) = self._anim_investida(sprite, (x, y), a, prog)
        elif a["tipo"] == "disparo":
            sprite_mod, (x, y) = self._anim_disparo(sprite, (x, y), a, prog)
        else:
            # tipo desconhecido → mantém
            pass

        # registra último draw para overlays
        self._ultimo_draw = {"pos": (x, y), "size": sprite_mod.get_size()}
        return sprite_mod, (x, y)

    # === AÇÕES (no sprite) ========================================================

    def _anim_fluxo(self, sprite, pos, a, prog,
                    cor=(255, 0, 0), wash=None, dir_sign=+1):
        """
        Fluxo colorido intenso atravessando o sprite.
        Usa BLEND_RGB_MAX para reforçar a cor (não fica lavado/branco).
        """
        s = sprite.copy()
        w, h = s.get_size()

        ciclos       = float(a.get("ciclos", 1.6))
        largura_pct  = float(a.get("largura_pct", 0.25))
        intensidade  = int(a.get("int_add", 200))
        core_boost   = int(a.get("core_add", 255))
        suavidade    = float(a.get("suavidade", 0.6))

        # wash base bem mais forte (puxa cor do pokémon)
        if wash is None:
            wash = (cor[0]//6, cor[1]//6, cor[2]//6)

        wash_surf = pygame.Surface((w, h))
        wash_surf.fill(wash)
        s.blit(wash_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # centro do feixe
        fase = dir_sign * prog * ciclos * 2.0 * math.pi
        cx = int((math.sin(fase) * 0.5 + 0.5) * (w - 1))

        def aplica_feixe(cx_loc, larg_pct, inten, core):
            banda = max(3, int(w * larg_pct))
            core_w = max(2, banda // 3)
            overlay = pygame.Surface((w, h))

            for dx in range(-banda, banda+1):
                x = cx_loc + dx
                if 0 <= x < w:
                    k = 1.0 - abs(dx)/float(banda)
                    k = k**(1.0 + 3.0*(1.0-suavidade))
                    if abs(dx) <= core_w:
                        k_core = 1.0 - abs(dx)/float(core_w+1)
                        add = int(inten*k + core*(k_core**2))
                    else:
                        add = int(inten*k)
                    add = max(0, min(255, add))

                    # usa a cor base saturada (não mistura branco!)
                    r = min(255, (cor[0]*add)//255)
                    g = min(255, (cor[1]*add)//255)
                    b = min(255, (cor[2]*add)//255)

                    pygame.draw.line(overlay, (r, g, b), (x, 0), (x, h-1))

            # usa BLEND_RGB_MAX pra reforçar a cor sem lavar
            s.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_MAX)

        # feixe principal + secundário deslocado
        aplica_feixe(cx, largura_pct, intensidade, core_boost)
        desloc = int(w*0.08) * (1 if dir_sign>0 else -1)
        aplica_feixe(cx+desloc, largura_pct*0.5,
                     int(intensidade*0.7), int(core_boost*0.7))

        return s, pos

    # === HELPERS DE ÂNCORA / CENTRO ==============================================

    def _anchor_atual(self):
        """
        Usa _ultimo_draw para inferir a âncora visual do pokémon.
        Retorna (anc_x, anc_y) e (px, py, sw, sh)
        """
        (px, py) = self._ultimo_draw["pos"]
        (sw, sh) = self._ultimo_draw["size"]
        anc_x = px + sw * 0.5
        anc_y = py + sh * 0.45
        return (anc_x, anc_y), (px, py, sw, sh)

    def _resolver_mov_alvo(self, a):
        """Inicializa delta em relação à âncora no primeiro uso."""
        (anc_x, anc_y), _ = self._anchor_atual()
        if a.get("orig") is None:
            a["orig"] = (anc_x, anc_y)
            ax, ay = a["alvo"]
            a["dx"] = ax - anc_x
            a["dy"] = ay - anc_y

    def _anim_avanco(self, sprite, pos, a, prog):
        """
        Salto parabólico em duas fases:
        - 0.0 → 0.5: vai da origem até o alvo, sobe e *desce para pousar no alvo* (lift=0 em 0.5).
        - 0.5 → 1.0: volta do alvo à origem pela MESMA rota (espelhada), pousando na origem (lift=0 em 1.0).

        'altura' é o pico de elevação (pixels) no meio de cada metade do trajeto.
        """
        self._resolver_mov_alvo(a)
        x0, y0 = pos
        dx = float(a.get("dx", 0.0))
        dy = float(a.get("dy", 0.0))
        altura = float(a.get("altura", 0.0))

        if prog <= 0.5:
            # ida: origem -> alvo
            u = prog / 0.5  # 0..1
            # interpola linha reta até o alvo
            x = x0 + dx * u
            y = y0 + dy * u
            # lift parabólico: 0 nos extremos (u=0 e u=1), pico em u=0.5
            lift = -altura * (4.0 * u * (1.0 - u))
        else:
            # volta: alvo -> origem (espelhado)
            u = (prog - 0.5) / 0.5  # 0..1
            # ponto de partida da volta é o alvo (x0+dx, y0+dy)
            x = (x0 + dx) + (-dx) * u
            y = (y0 + dy) + (-dy) * u
            # mesmo perfil de lift, zera no início (no alvo) e no fim (na origem)
            lift = -altura * (4.0 * u * (1.0 - u))

        return sprite, (x, y + lift)

    def _anim_investida(self, sprite, pos, a, prog):
        self._resolver_mov_alvo(a)
        x, y = pos
        curva = -4 * (prog - 0.5) ** 2 + 1.0
        dx = (a.get("dx", 0.0)) * max(0.0, curva)
        dy = (a.get("dy", 0.0)) * max(0.0, curva)
        return sprite, (x + dx, y + dy)

    def _anim_disparo(self, sprite, pos, a, prog):
        x, y = pos
        s = sprite
        escala_max = a.get("crescimento", 1.08)
        pct = float(a.get("pct_continue", self._pct_continue))

        # escala cresce até o pct_continue e satura
        sprog = min(1.0, (prog / max(1e-6, pct)))
        scale = 1.0 + (escala_max - 1.0) * sprog
        scale = max(1.0, min(escala_max, scale))

        if abs(scale - 1.0) > 1e-3:
            w, h = s.get_size()
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            s = pygame.transform.smoothscale(s, (nw, nh))
            x -= (nw - w) // 2
            y -= (nh - h) // 2

        # lançar projétil exatamente 1x ao cruzar o pct_continue
        if (not a.get("proj_lancado")) and (prog >= pct):
            a["proj_lancado"] = True
            p = getattr(self, "_projetil", None)
            if p is not None:
                p["ativo"] = True
                w0, h0 = s.get_size()
                p["ini"] = (x + w0 * 0.5, y + h0 * 0.35)
                p["pos"] = p["ini"]
                p["t"] = 0.0

        return s, (x, y)


    # === EXTRAS: STEP + DRAW por tipo ============================================

    def _step_projetil(self, dt):
        """Atualiza trajetória do projétil."""
        p = getattr(self, "_projetil", None)
        if not p or not p.get("ativo"):
            return
        p["t"] += dt
        prog = min(1.0, p["t"] / p["dur"]) if p.get("dur") else 1.0
        if p.get("ini") and p.get("fim"):
            x0, y0 = p["ini"]
            x1, y1 = p["fim"]
            p["pos"] = (x0 + (x1 - x0) * prog, y0 + (y1 - y0) * prog)
        if p["t"] >= p.get("dur", 0):
            p["ativo"] = False

    def _draw_projetil(self, tela):
        p = getattr(self, "_projetil", None)
        if not p or not p.get("ativo"):
            return
        x, y = p["pos"]
        if p.get("img") is not None:
            img = p["img"]
            rect = img.get_rect(center=(int(x), int(y)))
            tela.blit(img, rect.topleft)
        else:
            r = int(p.get("tamanho", 12))
            surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 255, 220), (r, r), r)
            pygame.draw.circle(surf, (0, 180, 255, 220), (r, r), r//2)
            tela.blit(surf, (int(x - r), int(y - r)))

    def _draw_aplicar_golpe(self, tela):
        fx = getattr(self, "_atk_fx", None)
        if not fx or not fx.get("ativo"):
            return

        # centro absoluto informado no iniciar_aplicar_golpe
        cx, cy = fx.get("pos", (None, None))
        if cx is None or cy is None:
            return

        # offset opcional
        ox, oy = fx.get("offset", (0, 0))
        cx += ox
        cy += oy

        # frame atual
        idx = int(fx.get("t", 0.0) * fx.get("fps", 24))
        frames = fx.get("frames", []) or []
        if not (0 <= idx < len(frames)):
            return

        frame = frames[idx]

        # extras opcionais: escala e rotação
        scale = float(fx.get("scale", 1.0))
        angle = float(fx.get("angle", 0.0))
        if scale != 1.0:
            w, h = frame.get_size()
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            frame = pygame.transform.smoothscale(frame, (nw, nh))
        if angle != 0.0:
            frame = pygame.transform.rotate(frame, angle)

        rect = frame.get_rect(center=(int(cx), int(cy)))
        tela.blit(frame, rect.topleft)

    def _draw_cartucho(self, tela):
        c = getattr(self, "_cartucho", None)
        if not c or not c.get("ativo") or not hasattr(self, "_ultimo_draw"):
            return

        (_, _), (px, py, sw, sh) = self._anchor_atual()
        orig_now = (px + sw * 0.5, py + sh * 0.30)
        if c["orig"] is None:
            c["orig"] = orig_now
        orig = c["orig"]

        s = max(0.0, min(1.0, c["t"] / c["dur"])) if c.get("dur") else 1.0

        # trajeto/escala
        x = orig[0] + c["dx"] * (s ** 2)
        y = orig[1] - c["altura"] * s
        esc = c["s0"] + (c["s1"] - c["s0"]) * s

        src = c["surf"]
        w0, h0 = src.get_size()
        nw, nh = max(1, int(w0 * esc)), max(1, int(h0 * esc))
        img = pygame.transform.smoothscale(src, (nw, nh))

        # === FADE custom: sólido no começo, apaga rápido no fim ===
        fade_start = float(c.get("fade_start", 0.25))  # 0..1
        fade_pow   = float(c.get("fade_pow",   2.0))   # >1 = mais rápido no fim
        if s <= fade_start:
            alpha = 255
        else:
            t = (s - fade_start) / max(1e-6, (1.0 - fade_start))  # 0..1
            t = min(1.0, max(0.0, t)) ** fade_pow
            alpha = int(255 * (1.0 - t))

        img.set_alpha(alpha)

        rect = img.get_rect(center=(int(x), int(y)))
        tela.blit(img, rect.topleft)

    def _draw_buff(self, tela):
        b = getattr(self, "_buff", None)
        if not b or not b.get("ativo"):
            return

        # === ÂNCORA: centro exato do pokémon ===
        if hasattr(self, "posCenter"):
            cx, cy = self.posCenter
        else:
            # fallback seguro
            if hasattr(self, "_ultimo_draw"):
                (px, py) = self._ultimo_draw["pos"]; (sw, sh) = self._ultimo_draw["size"]
                cx = px + sw * 0.5; cy = py + sh * 0.45
            else:
                return

        # progresso global
        s_global = max(0.0, min(1.0, (b.get("t", 0.0) / max(1e-6, b.get("dur", 1.0)))))

        # parâmetros
        aw, ah = b.get("area", (100, 100))
        amp_mul = float(b.get("amp", 1.0))          # ↑ amplitude vertical extra
        qtd = int(max(1, b.get("qtd", 8)))
        is_debuff = bool(b.get("debuff", False))
        base_cor = b.get("cor", (60, 220, 80, 235)) # RGBA

        # layer centralizada no posCenter
        layer_w = int(aw) + 80
        layer_h = int(ah) + 120
        layer = pygame.Surface((layer_w, layer_h), pygame.SRCALPHA)
        lx = int(cx - layer_w // 2)
        ly = int(cy - layer_h // 2)

        # inicializa partículas
        if ("parts" not in b) or (len(b["parts"]) != qtd):
            rng = random.Random(b.get("seed", 1337))
            parts = []

            n_left = (qtd + 1) // 2
            n_right = qtd // 2

            def gera_offsets(n, side):
                min_x = 0.40 * (aw * 0.5)
                max_x = 0.98 * (aw * 0.5)
                span = max_x - min_x
                if n == 1:
                    base = [min_x + span * 0.5]
                else:
                    base = [min_x + i * (span / (n - 1)) for i in range(n)]
                jitter = 0.15 * (span / max(1, n))
                return [side * (x + rng.uniform(-jitter, jitter)) for x in base]

            left_xs  = gera_offsets(n_left,  -1)
            right_xs = gera_offsets(n_right, +1)

            seq_xs, iL, iR = [], 0, 0
            for i in range(qtd):
                if i % 2 == 0:  # L
                    seq_xs.append(left_xs[iL]); iL += 1
                else:           # R
                    seq_xs.append(right_xs[iR]); iR += 1

            for i in range(qtd):
                side = -1 if (i % 2 == 0) else +1
                parts.append({
                    "side": side,
                    "x_off": seq_xs[i],
                    "delay": (i / max(1, qtd - 1)) * 0.45,
                    "speed": rng.uniform(0.9, 1.15),
                    "size":  rng.uniform(0.95, 1.15),
                    "wob":   rng.uniform(0.7, 1.3),
                })
            b["parts"] = parts

        parts = b["parts"]

        # centro local da layer
        lc_x = layer_w // 2
        lc_y = layer_h // 2

        # amplitude vertical maior, centrada no posCenter
        amp = (ah * 0.6) * amp_mul

        for i, p in enumerate(parts):
            s = (s_global * p["speed"]) - p["delay"]
            if s <= 0.0 or s >= 1.0:
                continue

            # setas
            base_h = 18
            base_w = 8
            seta_h = int(base_h * p["size"] * (0.9 + 0.2 * s))
            seta_w = int(base_w * p["size"])

            # sombra
            shadow_y = 1

            # leve oscilação lateral
            wobble = 4 * math.sin((s * 2.2 + i) * p["wob"])
            x0 = int(lc_x + p["x_off"] + wobble)

            if not is_debuff:
                # BUFF: sobe
                y_start = lc_y + amp
                y_end   = lc_y - amp
                y0 = int(y_start + (y_end - y_start) * s)

                head_pts = [(x0, y0 - 2),
                            (x0 - seta_w, y0 + 6),
                            (x0 + seta_w, y0 + 6)]
                shaft_start = (x0, y0 + seta_h)
                shaft_end   = (x0, y0)
            else:
                # DEBUFF: desce
                y_start = lc_y - amp
                y_end   = lc_y + amp
                y0 = int(y_start + (y_end - y_start) * s)

                head_pts = [(x0, y0 + 2),
                            (x0 - seta_w, y0 - 6),
                            (x0 + seta_w, y0 - 6)]
                shaft_start = (x0, y0 - seta_h)
                shaft_end   = (x0, y0)

            # cor com alpha
            if len(base_cor) == 4:
                alpha = int((0.55 + 0.45 * s) * base_cor[3])
                cor = (base_cor[0], base_cor[1], base_cor[2], max(0, min(255, alpha)))
            else:
                alpha = int(255 * (0.55 + 0.45 * s))
                cor = (base_cor[0], base_cor[1], base_cor[2], alpha)

            # sombra
            pygame.draw.line(layer, (0, 0, 0, alpha),
                             (shaft_start[0], shaft_start[1] + shadow_y),
                             (shaft_end[0],   shaft_end[1]   + shadow_y),
                             3)
            head_shadow = [(x, y + shadow_y) for (x, y) in head_pts]
            pygame.draw.polygon(layer, (0, 0, 0, alpha), head_shadow, 0)

            # seta
            pygame.draw.line(layer, cor, shaft_start, shaft_end, 2)
            pygame.draw.polygon(layer, cor, head_pts, 0)

        # blita layer
        tela.blit(layer, (lx, ly))
        
    # === LOOP DE EXTRAS (público) ================================================

    def step_extras(self, dt):
        """Atualize estados temporais de extras (chamar 1x por frame)."""
        self._step_projetil(dt)
        # (se futuramente tiver timers em _atk_fx/_cartucho/_buff, gerencie aqui)

    def desenhar_extras(self, tela):
        """Desenhe todos os overlays após blitar o sprite do pokémon."""
        self._draw_projetil(tela)
        self._draw_aplicar_golpe(tela)
        self._draw_cartucho(tela)
        self._draw_buff(tela)

    def desenhar(self, dt, tela, nova_pos=None, multiplicador=1.0):
        # --- animação de frames (velocidade) ---
        self.timer += dt
        mult_vel = self.velocidade if self.velocidade > 0 else 1e-6
        intervalo = self._intervalo_base / mult_vel
        if self.timer > intervalo:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.timer = 0.0

        # frame atual
        sprite = self.frames[self.frame_index]

        # escala temporária
        if multiplicador != 1.0:
            w = max(1, int(round(sprite.get_width()  * multiplicador)))
            h = max(1, int(round(sprite.get_height() * multiplicador)))
            sprite = pygame.transform.scale(sprite, (w, h))

        # posição base
        pos_base = nova_pos if nova_pos is not None else self.pos

        # atualizar ação / efeitos
        self._atualizar_acao(dt)
        sprite, pos_desenho = self._efeitos_acao(sprite, pos_base)

        # desenha sprite
        rect = sprite.get_rect(center=pos_desenho)
        self.rect = tela.blit(sprite, rect)

        self.desenhar_extras(tela)

        # ===================== BARRAS ESTILO TFT =====================
        vida     = float(self.pokemon["Vida"])
        energia  = float(self.pokemon["Energia"])
        vida_max = max(1.0, float(self.pokemon["VidaMax"]))
        ene_max  = max(1.0, float(self.pokemon["Ene"]))

        largura  = 80
        offset_y = -18
        h_vida, h_ene = 10, 7   # sem hover

        # base centralizada
        cx = rect.centerx
        x0 = int(cx - largura // 2)
        y0 = int(rect.top + offset_y)

        # cores
        cor_borda = (0, 0, 0)
        cor_fundo = (24, 24, 24)
        cor_vida  = (0, 200, 0)
        cor_ene   = (0, 0, 200)

        # cantos levemente arredondados
        br_vida = min(h_vida // 2, 6)
        br_ene  = min(h_ene  // 2, 6)

        # percentuais
        vida_pct = max(0.0, min(1.0, vida / vida_max))
        ene_pct  = max(0.0, min(1.0, energia / ene_max))

        # ----------------- VIDA (barra superior) -----------------
        r_bg = pygame.Rect(x0, y0, largura, h_vida)
        pygame.draw.rect(tela, cor_fundo, r_bg, border_radius=br_vida)
        pygame.draw.rect(tela, cor_borda, r_bg, width=1, border_radius=br_vida)

        fill_w = int(largura * vida_pct)
        if fill_w > 0:
            r_fill = pygame.Rect(x0, y0, fill_w, h_vida)
            pygame.draw.rect(tela, cor_vida, r_fill, border_radius=br_vida)

            # divisórias pretas (SOMENTE na vida)
            passo = 30.0
            for i in range(int(passo), int(vida_max), int(passo)):
                px = x0 + int(round(largura * (i / vida_max)))
                if px <= x0 + fill_w - 1:
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
        # ==========================================================


