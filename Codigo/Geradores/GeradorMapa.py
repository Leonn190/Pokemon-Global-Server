import pygame

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

class Camera:
    def __init__(self, raio_em_tiles):
        # Calcula a resolução máxima do monitor
        info = pygame.display.Info()
        self.Resolucao = (info.current_w, info.current_h)
        
        # Raio da câmera em tiles (ex: 10 mostraria 21x21 tiles)
        self.raio = raio_em_tiles

        # A resolução em pixels que a câmera desenha é baseada nesse raio
        self.largura_em_tiles = 2 * raio_em_tiles + 1
        self.altura_em_tiles = 2 * raio_em_tiles + 1

    def desenhar(self, tela, jogador_pos, mapa, EstruturasIMG, BausIMG):
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

                pokemon.Atualizar(tela, (pos_x + tile // 2, pos_y + tile // 2))

        baus_para_remover = []

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
                        if bau.TempoAposAbrir >= 180:
                            baus_para_remover.append(bau_id)
                else:
                    img = BausIMG[bau.raridade][0]
                    bau.desenhar(tela, centro_pos, img)

        # Remover após o loop
        for bau_id in baus_para_remover:
            del mapa.BausAtivos[bau_id]

    def pegar_cor_bioma(self, bioma):
        # Dicionário simples de cor por tipo de bioma
        cores = {
            0: (100, 200, 100),  # verde - grama
            1: (150, 150, 255),  # azul - água
            2: (210, 180, 140),  # marrom - terra
            3: (250, 250, 250),  # branco - neve
            4: (255, 255, 0),    # amarelo - deserto
        }
        return cores.get(bioma, (0, 0, 0))  # padrão: preto
    