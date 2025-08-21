import pygame
from pygame.math import Vector2

class Mapa:
    def __init__(self, GridBiomas, DicObjetos):
        self.GridBiomas = GridBiomas  # matriz de números
        self.DicObjetos = DicObjetos  # dicionário global de objetos {(x, y): objeto}

        self.PokemonsAtivos = {}
        self.BausAtivos = {}
        self.PlayerAtivos = {}

        self.Tile = 70  # tamanho de um tile em pixels
        self.Largura = len(GridBiomas[0]) * self.Tile
        self.Altura = len(GridBiomas) * self.Tile

        self.ObjetosColisão = None
        self.PokemonsColisão = None
        self.PokemonsColisãoPlayer = None
        self.BausColisão = None

    def dividir_em_chunks(self, dic_objetos):
        chunks = {}

        # Garante que todos os chunks possíveis existam, mesmo vazios
        max_x = len(self.GridBiomas[0])
        max_y = len(self.GridBiomas)

        for y in range(max_y):
            for x in range(max_x):
                cx = x // 100
                cy = y // 100
                coord_chunk = (cx, cy)

                if coord_chunk not in chunks:
                    chunks[coord_chunk] = {}

        # Adiciona os objetos existentes nos seus chunks
        for (x, y), objeto in dic_objetos.items():
            cx = x // 100
            cy = y // 100
            coord_chunk = (cx, cy)

            chunks[coord_chunk][(x, y)] = objeto

        return chunks

class CameraMundo:
    def __init__(self, raio_em_tiles):
        # Calcula a resolução máxima do monitor
        info = pygame.display.Info()
        self.Resolucao = (info.current_w, info.current_h)
        
        # Raio da câmera em tiles (ex: 10 mostraria 21x21 tiles)
        self.raio = raio_em_tiles

        # A resolução em pixels que a câmera desenha é baseada nesse raio
        self.largura_em_tiles = 2 * raio_em_tiles + 1
        self.altura_em_tiles = 2 * raio_em_tiles + 1

    def desenhar(self, tela, jogador_pos, mapa, player, EstruturasIMG, delta_time, BausIMG, parametros, Consumiveis, Fontes):
        tile = mapa.Tile
        grid = mapa.GridBiomas
        objetos = mapa.DicObjetos
        PokemonsAtivos = mapa.PokemonsAtivos
        BausAtivos = mapa.BausAtivos

        jogador_x, jogador_y = jogador_pos

        inicio_x = int(jogador_x) - self.raio
        inicio_y = int(jogador_y) - self.raio

        offset_x = (jogador_x % 1) * tile
        offset_y = (jogador_y % 1) * tile

        centro_tela_x = self.Resolucao[0] // 2
        centro_tela_y = self.Resolucao[1] // 2

        for linha in range(self.altura_em_tiles):
            for coluna in range(self.largura_em_tiles):
                grid_x = inicio_x + coluna
                grid_y = inicio_y + linha

                if 0 <= grid_y < len(grid) and 0 <= grid_x < len(grid[0]):
                    bioma = grid[grid_y][grid_x]
                    cor = self.pegar_cor_bioma(bioma)

                    pos_x = centro_tela_x + (coluna - self.raio) * tile - offset_x
                    pos_y = centro_tela_y + (linha - self.raio) * tile - offset_y

                    pygame.draw.rect(tela, cor, (pos_x, pos_y, tile, tile))
        
        player.Atualizar(tela, delta_time, mapa, Fontes[20], parametros, Consumiveis)

        # Desenha estruturas visíveis
        for (x, y), estrutura in objetos.items():
            if inicio_x <= x < inicio_x + self.largura_em_tiles and inicio_y <= y < inicio_y + self.altura_em_tiles:
                coluna = x - inicio_x
                linha = y - inicio_y

                pos_x = centro_tela_x + (coluna - self.raio) * tile - offset_x
                pos_y = centro_tela_y + (linha - self.raio) * tile - offset_y

                img = EstruturasIMG[estrutura.nome]  # <- pegamos imagem aqui
                estrutura.desenhar(tela, (pos_x + tile // 2, pos_y + tile // 2), img)  # <- ajusta para centro
        
        for chave, pokemon in PokemonsAtivos.items():
            x, y = pokemon.Loc  # Obtemos diretamente do atributo .Loc do objeto
            if inicio_x <= x < inicio_x + self.largura_em_tiles and inicio_y <= y < inicio_y + self.altura_em_tiles:
                coluna = x - inicio_x
                linha = y - inicio_y

                pos_x = centro_tela_x + (coluna - self.raio) * tile - offset_x
                pos_y = centro_tela_y + (linha - self.raio) * tile - offset_y

                pokemon.Atualizar(tela, (pos_x + tile // 2, pos_y + tile // 2), player, delta_time)

        for bau_id, bau in BausAtivos.items():
            x, y = bau.Loc

            if inicio_x <= x < inicio_x + self.largura_em_tiles and inicio_y <= y < inicio_y + self.altura_em_tiles:
                coluna = x - inicio_x
                linha = y - inicio_y

                pos_x = centro_tela_x + (coluna - self.raio) * tile - offset_x
                pos_y = centro_tela_y + (linha - self.raio) * tile - offset_y

                centro_pos = (pos_x + tile // 2, pos_y + tile // 2)

                if bau.Aberto:
                    imagens = BausIMG[bau.raridade]
                    frame_total = len(imagens)

                    frame_index = int(bau.Animando)
                    if frame_index >= frame_total:
                        frame_index = frame_total - 1

                    img = imagens[frame_index]
                    bau.desenhar(tela, centro_pos, img)

                    if bau.Animando < frame_total - 1:
                        bau.Animando += 0.2
                    else:
                        bau.TempoAposAbrir += 1
                        if bau.TempoAposAbrir >= 150:
                            bau.Apagar = True
                else:
                    img = BausIMG[bau.raridade][0]
                    bau.desenhar(tela, centro_pos, img)

    def pegar_cor_bioma(self, bioma):
        # Dicionário simples de cor por tipo de bioma

        #     "OCEAN":        0,
        #     "LAKE":         1,
        #     "PLAIN":        2,
        #     "FOREST":       3,
        #     "DESERT":       4,
        #     "SNOW":         5,
        #     "VULCANO":      6,
        #     "TERRA_MAGICA": 7,
        #     "PANTANO":      8,


        cores = {
            0: (20, 60, 150),  
            1: (40, 90, 170),  
            2: (120, 190, 90),  
            3: (50, 120, 60),  
            4: (238, 214, 87),
            5: (235, 240, 245),
            6: (150, 20, 20),
            7: (150, 60, 200)    
        }

        if bioma == 8:
            bioma = 2
        if bioma != 3:
            print("eita")

        return cores.get(bioma, (0, 0, 0))  # padrão: preto

class CameraBatalha:
    """
    - self.Centro: ponto central da câmera em coordenadas do fundo (mundo)
    - self.Zoom: escala (px_tela por px_mundo)
    - ZoomMin = max(SW/BgW, SH/BgH) => sem barras pretas
    - Clamp mantém a viewport dentro do fundo
    - Zoom ao redor do mouse preservando o ponto sob o cursor
    - Pan com botão direito (drag)
    """
    def __init__(self, bg_surface, tamanho_tela):
        self.Bg = bg_surface
        self.BgW, self.BgH = self.Bg.get_size()
        self.SW, self.SH   = tamanho_tela

        self.ZoomMax = 3.0
        self.ZoomMin = self._calc_zoom_min()

        self.Zoom   = self.ZoomMin
        self.Centro = Vector2(self.BgW/2, self.BgH/2)

        # arraste
        self.Arrastando   = False
        self.MouseInicio  = Vector2(0, 0)
        self.CentroInicio = self.Centro.copy()

    # ---- utilidades ----
    def _calc_zoom_min(self):
        zx = float(self.SW) / float(self.BgW)
        zy = float(self.SH) / float(self.BgH)
        return max(zx, zy)

    def _half_view_world(self):
        # metade da viewport em unidades de MUNDO
        return (self.SW / (2.0*self.Zoom), self.SH / (2.0*self.Zoom))

    def _clamp_centro(self):
        half_w, half_h = self._half_view_world()
        cx_min = half_w
        cy_min = half_h
        cx_max = self.BgW - half_w
        cy_max = self.BgH - half_h

        if cx_min > cx_max:
            self.Centro.x = self.BgW/2.0
        else:
            if self.Centro.x < cx_min: self.Centro.x = cx_min
            if self.Centro.x > cx_max: self.Centro.x = cx_max

        if cy_min > cy_max:
            self.Centro.y = self.BgH/2.0
        else:
            if self.Centro.y < cy_min: self.Centro.y = cy_min
            if self.Centro.y > cy_max: self.Centro.y = cy_max

    # ---- conversões ----
    def TelaAPartirDoMundo(self, pos_mundo):
        # screen = (world - Centro)*Zoom + meio_da_tela
        mx, my = pos_mundo
        sx = (mx - self.Centro.x) * self.Zoom + self.SW/2.0
        sy = (my - self.Centro.y) * self.Zoom + self.SH/2.0
        return Vector2(sx, sy)

    def MundoAPartirDaTela(self, pos_tela):
        # world = (screen - meio_da_tela)/Zoom + Centro
        sx, sy = pos_tela
        wx = (sx - self.SW/2.0) / self.Zoom + self.Centro.x
        wy = (sy - self.SH/2.0) / self.Zoom + self.Centro.y
        return Vector2(wx, wy)

    def AtualizarTamanhoTela(self, novo_tamanho):
        self.SW, self.SH = int(novo_tamanho[0]), int(novo_tamanho[1])
        self.ZoomMin = self._calc_zoom_min()
        if self.Zoom < self.ZoomMin:
            # aumenta só até o mínimo e recentra
            self.Zoom = self.ZoomMin
            self.Centro.update(self.BgW/2.0, self.BgH/2.0)
        self._clamp_centro()

    # ---- interação ----
    def ZoomNoPonto(self, fator, pos_mouse_tela):
        # mantém o ponto do mundo sob o mouse fixo na tela
        alvo_world = self.MundoAPartirDaTela(pos_mouse_tela)

        novo_zoom = self.Zoom * float(fator)
        if novo_zoom < self.ZoomMin: novo_zoom = self.ZoomMin
        if novo_zoom > self.ZoomMax: novo_zoom = self.ZoomMax
        if abs(novo_zoom - self.Zoom) < 1e-6:
            return

        self.Zoom = novo_zoom
        # resolve Centro para manter alvo_world sob o cursor
        mid = Vector2(self.SW/2.0, self.SH/2.0)
        self.Centro = Vector2(
            alvo_world.x - (pos_mouse_tela[0] - mid.x)/self.Zoom,
            alvo_world.y - (pos_mouse_tela[1] - mid.y)/self.Zoom
        )
        self._clamp_centro()

    def IniciarArraste(self, pos_mouse_tela):
        self.Arrastando   = True
        self.MouseInicio  = Vector2(pos_mouse_tela)
        self.CentroInicio = self.Centro.copy()

    def PararArraste(self):
        self.Arrastando = False

    def ArrastarAte(self, pos_mouse_tela):
        if not self.Arrastando: return
        delta_screen = Vector2(pos_mouse_tela) - self.MouseInicio
        # mover Centro no sentido oposto do delta da tela, escalado pelo zoom
        self.Centro = self.CentroInicio - delta_screen / self.Zoom
        self._clamp_centro()

    def Atualizar(self, eventos):
        for e in eventos:
            if e.type == pygame.VIDEORESIZE:
                self.AtualizarTamanhoTela((e.w, e.h))
            elif e.type == pygame.MOUSEWHEEL:
                fator = 1.0 + 0.1 * float(e.y)
                self.ZoomNoPonto(fator, pygame.mouse.get_pos())
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                self.IniciarArraste(pygame.mouse.get_pos())
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 3:
                self.PararArraste()
            elif e.type == pygame.MOUSEMOTION and self.Arrastando:
                self.ArrastarAte(pygame.mouse.get_pos())

    # ---- desenho ----
    def Desenhar(self, destino):
        # 1) calcula a área visível em MUNDO a partir dos cantos da tela
        p0 = self.MundoAPartirDaTela((0, 0))                 # topo-esquerda (mundo)
        p1 = self.MundoAPartirDaTela((self.SW, self.SH))     # baixo-direita (mundo)

        left = int(p0.x) if p0.x < p1.x else int(p1.x)
        top  = int(p0.y) if p0.y < p1.y else int(p1.y)
        right  = int(p1.x) if p1.x > p0.x else int(p0.x)
        bottom = int(p1.y) if p1.y > p0.y else int(p0.y)

        # clamp dentro do fundo
        if left < 0: left = 0
        if top  < 0: top  = 0
        if right  > self.BgW: right  = self.BgW
        if bottom > self.BgH: bottom = self.BgH

        src_w = right - left
        src_h = bottom - top
        if src_w <= 0 or src_h <= 0:
            return  # nada visível (evita erros quando em clamp extremo)

        src_rect = pygame.Rect(left, top, src_w, src_h)

        # 2) recorta só a região visível e escala uma única vez para o tamanho da TELA
        view = self.Bg.subsurface(src_rect)
        scaled = pygame.transform.scale(view, (self.SW, self.SH))

        # 3) desenha alinhado a (0,0) porque já está do tamanho da tela
        destino.blit(scaled, (0, 0))
