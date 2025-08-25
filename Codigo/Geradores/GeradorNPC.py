import pygame, math

from Codigo.Modulos.DesenhoPlayer import PegarRotaçao, CacheExtrairCor, escurecer_cor
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda

class NPC:
    TILE = 70  # px por tile

    def __init__(self, parcial_inicial, Skins, fonte_nome, cor_nome=(255,255,255)):
        # recursos
        self.Skins = Skins
        self.fonte_nome = fonte_nome
        self.cor_nome = cor_nome

        # estado base (parcial)
        self.Nome        = parcial_inicial.get("Nome", "NPC")
        self.SkinNumero  = parcial_inicial.get("Skin", 1)
        self.Skin        = self.Skins[self.SkinNumero]
        self.SkinRedimensionada = pygame.transform.scale(self.Skin, (83, 66))
        self.Nivel       = parcial_inicial.get("Nivel", 1)
        self.Selecionado = parcial_inicial.get("Selecionado", 0)
        self.Velocidade  = float(parcial_inicial.get("Velocidade", 3.0))  # virá no parcial
        self.ID          = parcial_inicial["ID"]

        loc0 = parcial_inicial.get("Loc", [0.0, 0.0])
        ang0 = float(parcial_inicial.get("Angulo", 0.0))

        # estado atual
        self.Loc        = [float(loc0[0]), float(loc0[1])]   # tiles
        self.Angulo     = ang0                               # graus

        # alvos
        self.LocAlvo    = [float(loc0[0]), float(loc0[1])]
        self.AnguloAlvo = ang0

        # inventário (para desenhar item na mão). Se não setar, fica vazio.
        self.Inventario = []

        # tunings
        self.vel_ang_deg_s = 360.0   # vel. angular fixa (graus/s)
        self.snap_dist_tiles = 20.0  # anti-teleporte

        # rect de desenho
        self.draw_rect = pygame.Rect(0,0,83,66)

    # ---------- updates vindos da rede ----------
    def aplicar_dic_parcial(self, dic):
        if "Nome" in dic:
            self.Nome = dic["Nome"]
        if "Skin" in dic and dic["Skin"] != self.SkinNumero:
            self.SkinNumero = dic["Skin"]
            self.Skin = self.Skins[self.SkinNumero]
            self.SkinRedimensionada = pygame.transform.scale(self.Skin, (83, 66))
        if "Nivel" in dic:
            self.Nivel = dic["Nivel"]
        if "Selecionado" in dic:
            self.Selecionado = dic["Selecionado"]
        if "Velocidade" in dic:
            self.Velocidade = float(dic["Velocidade"])
        if "Loc" in dic:
            self.LocAlvo = [float(dic["Loc"][0]), float(dic["Loc"][1])]
        if "Angulo" in dic:
            self.AnguloAlvo = float(dic["Angulo"])

    def set_inventario(self, inventario):
        self.Inventario = inventario or []

    # ---------- ciclo ----------
    def Atualizar(self, tela, delta_time, player_Loc, ItensIMG):
        # 1) mover em direção ao alvo com velocidade do parcial (tiles/s)
        #    usa mesma regra do player: v_tile_s = 0.5*Velocidade + 3.5
        v_tiles_s = (self.Velocidade * 0.5) + 3.5
        step = max(0.0, v_tiles_s * delta_time)

        dx = self.LocAlvo[0] - self.Loc[0]
        dy = self.LocAlvo[1] - self.Loc[1]
        dist = math.hypot(dx, dy)

        if dist > self.snap_dist_tiles:
            # lagzão: snap para não deslizar o mapa todo
            self.Loc[0], self.Loc[1] = self.LocAlvo[0], self.LocAlvo[1]
        elif dist > 1e-6:
            ux, uy = dx / dist, dy / dist
            move = min(dist, step)
            self.Loc[0] += ux * move
            self.Loc[1] += uy * move

        # 2) suavizar ângulo com vel. angular fixa (menor arco)
        self.Angulo = self._step_angulo(self.Angulo, self.AnguloAlvo, self.vel_ang_deg_s * delta_time)

        # 3) mundo->tela (player no centro)
        scr_x, scr_y = self._world_to_screen(self.Loc, player_Loc, tela.get_size())

        # 4) corpo
        angulo_cor = self.Angulo - 90
        corpo_rot = PegarRotaçao(self.SkinRedimensionada, angulo_cor)  # usa seu cache global
        corpo_rect = corpo_rot.get_rect(center=(scr_x, scr_y))
        tela.blit(corpo_rot, corpo_rect)
        self.draw_rect = corpo_rect

        # 5) braços + item (visual simples)
        cor_braco = CacheExtrairCor(self.SkinRedimensionada)
        self._desenhar_bracos_visual(tela, (scr_x, scr_y), cor_braco, math.radians(self.Angulo), ItensIMG)

        # 6) nome
        flut = math.sin(pygame.time.get_ticks() / 200) * 5
        txt = self.fonte_nome.render(self.Nome, True, self.cor_nome)
        x_txt = int(corpo_rect.centerx - txt.get_width() // 2)
        y_txt = int(corpo_rect.top - 8 - txt.get_height() + flut)
        try:
            texto_com_borda(tela, self.Nome, self.fonte_nome, (x_txt, y_txt), self.cor_nome, (0,0,0))
        except Exception:
            tela.blit(txt, (x_txt, y_txt))

    # ---------- helpers de instância (sem decorators) ----------
    def _world_to_screen(self, loc_tiles, player_loc_tiles, tela_size):
        w, h = tela_size
        cx, cy = w // 2, h // 2
        dx_tiles = loc_tiles[0] - player_loc_tiles[0]
        dy_tiles = loc_tiles[1] - player_loc_tiles[1]
        return int(cx + dx_tiles * self.TILE), int(cy + dy_tiles * self.TILE)

    def _step_angulo(self, a_deg, b_deg, max_delta_deg):
        a = (a_deg + 360.0) % 360.0
        b = (b_deg + 360.0) % 360.0
        d = (b - a + 540.0) % 360.0 - 180.0   # menor arco em (-180,180]
        if d >  max_delta_deg: d =  max_delta_deg
        if d < -max_delta_deg: d = -max_delta_deg
        return (a + d) % 360.0

    def _desenhar_bracos_visual(self, tela, centro, cor_braco, angulo_rad, ItensIMG):
        """
        Versão visual/idle dos braços: respiração + posição relativa ao ângulo.
        Desenha item do slot self.Selecionado na mão direita (se existir).
        """
        x_c, y_c = centro
        tempo = pygame.time.get_ticks()

        distancia_braco = 60
        profundidade_amplitude = 4

        # respiração
        profundidade = math.sin(tempo / 500) * profundidade_amplitude
        dx_depth = math.cos(angulo_rad) * profundidade
        dy_depth = math.sin(angulo_rad) * profundidade

        # bases (direita/esquerda) ao redor do corpo
        def base_braco(offset_lado):
            ox = math.cos(angulo_rad + offset_lado * math.pi / 2) * distancia_braco
            oy = math.sin(angulo_rad + offset_lado * math.pi / 2) * distancia_braco
            return (x_c + ox + dx_depth, y_c + oy + dy_depth)

        base_dir = base_braco(+1)
        base_esq = base_braco(-1)

        # desenhar esq (apenas visual)
        cor_borda = escurecer_cor(cor_braco)
        pygame.draw.circle(tela, cor_braco, (int(base_esq[0]), int(base_esq[1])), 10)
        pygame.draw.circle(tela, cor_borda, (int(base_esq[0]), int(base_esq[1])), 13, width=3)

        # desenhar dir (apenas visual)
        pygame.draw.circle(tela, cor_braco, (int(base_dir[0]), int(base_dir[1])), 10)
        pygame.draw.circle(tela, cor_borda, (int(base_dir[0]), int(base_dir[1])), 13, width=3)

        # item na mão direita (self.Selecionado)
        item = self.Inventario[self.Selecionado] if 0 <= self.Selecionado < len(self.Inventario) else None
        if item:
            nome_item = item.get("nome")
            img_item = ItensIMG.get(nome_item)
            if img_item:
                img_aj = pygame.transform.scale(img_item, (35, 35))
                rect_img = img_aj.get_rect(center=(int(base_dir[0]), int(base_dir[1])))
                tela.blit(img_aj, rect_img.topleft)
