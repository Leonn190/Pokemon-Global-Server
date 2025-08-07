import math
import pygame

from Codigo.Prefabs.FunçõesPrefabs import extrair_cor_predominante, escurecer_cor, texto_com_borda, Fluxo

class Player:
    def __init__(self, Informações, Skins):

        self.Code = Informações["Code"]
        self.Nome = Informações["Nome"]

        self.Pokemons = Informações["Pokemons"]
        self.Inventario = Informações["Inventario"]
        self.Ouro = Informações["Ouro"]
        self.SkinNumero = Informações["Skin"]
        self.Skin = Skins[self.SkinNumero]
        self.SkinRedimensionada = pygame.transform.scale(self.Skin, (83, 66))
        self.Nivel = Informações["Nivel"]
        self.Xp = Informações["XP"]
        
        self.Mochila = Informações["Mochila"]
        self.Velocidade = Informações["Velocidade"]
        self.Maestria = Informações["Maestria"]

        self.Loc = Informações["Loc"]

        self.MaoEsquerda = Informações.get("Esquerda",None)
        self.MaoDireita = Informações.get("Direita",None)
        self.Angulo = 90

        self.estado_tapa = {
            "esquerdo": {"tapando": False, "inicio_tapa": 0, "tempo_ultimo_tapa": 0},
            "direito": {"tapando": False, "inicio_tapa": 0, "tempo_ultimo_tapa": 0}
        }

        self.rect = pygame.Rect(0, 0, 83, 66)
        self.rect.center = (self.Loc[0], self.Loc[1])  # Pos inicial

        self.tile = 70

    def Atualizar(self, tela, delta_time, mapa, fonte, parametros, ItensIMG):

        self.mover(delta_time, mapa, parametros)

        largura_tela, altura_tela = tela.get_size()
        x_centro = largura_tela // 2
        y_centro = altura_tela // 2
        self.rect.center = (x_centro, y_centro)

        imagem_corpo = self.SkinRedimensionada
        cor_braco = extrair_cor_predominante(imagem_corpo)

        # Calcula ângulo entre centro da tela e mouse
        mouse_pos = pygame.mouse.get_pos()
        dx, dy = mouse_pos[0] - x_centro, mouse_pos[1] - y_centro
        angulo = math.degrees(math.atan2(dy, dx))
        angulo_correcao = angulo - 90
        self.angulo = angulo

        corpo_rotacionado = pygame.transform.rotate(imagem_corpo, -angulo_correcao)
        corpo_rect = corpo_rotacionado.get_rect(center=(x_centro, y_centro))
        tela.blit(corpo_rotacionado, corpo_rect)

        # Novo: desenha braços
        self.desenhar_bracos(tela, (x_centro, y_centro), cor_braco, math.radians(angulo), ItensIMG)

        pygame.draw.rect(tela, (0, 255, 0), self.rect, 2)

        # Nome flutuante
        texto_surface = fonte.render(self.Nome, True, (255, 255, 255))
        flutuacao = math.sin(pygame.time.get_ticks() / 200) * 5
        texto_rect = texto_surface.get_rect(center=(x_centro, y_centro - 80 + flutuacao))
        texto_com_borda(tela, self.Nome, fonte, texto_rect.topleft, (255, 255, 255), (0, 0, 0))

    def desenhar_bracos(self, tela, centro, cor_braco, angulo_rad, ItensIMG):
        x_centro, y_centro = centro
        tempo = pygame.time.get_ticks()

        distancia_braco = 58
        ciclo_tapa_ms = 900
        tapa_amplitude = 35
        profundidade_amplitude = 4

        def calcular_respiração():
            profundidade = math.sin(tempo / 500) * profundidade_amplitude
            dx = math.cos(angulo_rad) * profundidade
            dy = math.sin(angulo_rad) * profundidade
            return dx, dy

        def calcular_base_braco(lado):
            direcao = 1 if lado == "direito" else -1
            offset_x = math.cos(angulo_rad + direcao * math.pi / 2) * distancia_braco
            offset_y = math.sin(angulo_rad + direcao * math.pi / 2) * distancia_braco
            return x_centro + offset_x, y_centro + offset_y

        def aplicar_respiração(base, depth):
            return base[0] + depth[0], base[1] + depth[1]

        def calcular_movimento_mao(lado, base):
            estado = self.estado_tapa[lado]
            mouse = pygame.mouse.get_pressed()
            tempo_atual = pygame.time.get_ticks()

            mao = self.MaoEsquerda if lado == "esquerdo" else self.MaoDireita
            botao_pressionado = (lado == "esquerdo" and mouse[0]) or (lado == "direito" and mouse[2])

            # 📐 Calcular ângulo em radianos automaticamente (base → mouse)
            mx, my = pygame.mouse.get_pos()
            dx_mouse = mx - base[0]
            dy_mouse = my - base[1]
            angulo_rad = math.atan2(dy_mouse, dx_mouse)

            if mao:  # 🟢 COM ITEM → MIRAR
                if botao_pressionado:
                    # Normalizar direção
                    dist = math.hypot(dx_mouse, dy_mouse)
                    if dist == 0:
                        dist = 0.001
                    dir_x = dx_mouse / dist
                    dir_y = dy_mouse / dist

                    # Desenhar fluxo animado
                    alcance = 500
                    destino_x = int(base[0] + dir_x * alcance)
                    destino_y = int(base[1] + dir_y * alcance)
                    Fluxo(tela, base[0], base[1], destino_x, destino_y, cor_base=(150, 150, 255))

                    # Mão vai para trás
                    movimento = 0.5 + 0.5 * math.sin((tempo_atual % 1000) / 1000 * math.pi)
                    offset = -20 * movimento
                    dx = math.cos(angulo_rad) * offset
                    dy = math.sin(angulo_rad) * offset

                    return base[0] + dx, base[1] + dy

                return base  # parado se não estiver pressionando

            else:  # 🔴 SEM ITEM → TAPA
                if botao_pressionado and not estado["tapando"]:
                    estado["tapando"] = True
                    estado["inicio_tapa"] = tempo_atual
                    estado["tempo_ultimo_tapa"] = tempo_atual

                if estado["tapando"]:
                    t = (tempo_atual - estado["inicio_tapa"]) / ciclo_tapa_ms
                    if t >= 1:
                        estado["tapando"] = False
                        t = 1
                        if botao_pressionado and tempo_atual - estado["tempo_ultimo_tapa"] >= ciclo_tapa_ms:
                            estado["tapando"] = True
                            estado["inicio_tapa"] = tempo_atual
                            estado["tempo_ultimo_tapa"] = tempo_atual
                            t = 0

                    movimento = math.sin(t * math.pi)
                    angulo_offset = math.pi / 18 if lado == "esquerdo" else -math.pi / 18
                    angulo_tapa = angulo_rad + angulo_offset
                    dx = math.cos(angulo_tapa) * movimento * tapa_amplitude
                    dy = math.sin(angulo_tapa) * movimento * tapa_amplitude
                    return base[0] + dx, base[1] + dy

                return base

        def desenhar_item_na_mao(lado, pos_mao):
            item = self.MaoEsquerda if lado == "esquerdo" else self.MaoDireita
            if item:
                nome_item = item.get("nome")
                imagem_item = ItensIMG.get(nome_item)
                if imagem_item:
                    imagem_ajustada = pygame.transform.scale(imagem_item, (30, 30))  # tamanho adequado à mão
                    rect_img = imagem_ajustada.get_rect(center=(int(pos_mao[0]), int(pos_mao[1])))
                    tela.blit(imagem_ajustada, rect_img.topleft)

        # Fluxo principal
        depth = calcular_respiração()

        base_esq = aplicar_respiração(calcular_base_braco("esquerdo"), depth)
        base_dir = aplicar_respiração(calcular_base_braco("direito"), depth)

        pos_braco_esquerdo = calcular_movimento_mao("esquerdo", base_esq)
        pos_braco_direito = calcular_movimento_mao("direito", base_dir)

        # Desenhar os braços
        pygame.draw.circle(tela, cor_braco, (int(pos_braco_esquerdo[0]), int(pos_braco_esquerdo[1])), 10)
        pygame.draw.circle(tela, cor_braco, (int(pos_braco_direito[0]), int(pos_braco_direito[1])), 10)

        # Desenhar a borda dos braços
        cor_borda = escurecer_cor(cor_braco)
        raio = 10
        raio_borda = 13

        for pos in [pos_braco_esquerdo, pos_braco_direito]:
            pygame.draw.circle(tela, cor_borda, pos, raio_borda)
            pygame.draw.circle(tela, cor_braco, pos, raio)

        # ✅ Desenhar os itens nas mãos, se houver
        desenhar_item_na_mao("esquerdo", pos_braco_esquerdo)
        desenhar_item_na_mao("direito", pos_braco_direito)

    def mover(self, delta_time, mapa, parametros):

        ObjetosColisão = mapa.ObjetosColisão
        BausColisão = mapa.BausColisão

        teclas = pygame.key.get_pressed()
        direcao_x = 0
        direcao_y = 0

        if teclas[pygame.K_w]:
            direcao_y -= 1
        if teclas[pygame.K_s]:
            direcao_y += 1
        if teclas[pygame.K_a]:
            direcao_x -= 1
        if teclas[pygame.K_d]:
            direcao_x += 1

        magnitude = math.hypot(direcao_x, direcao_y)

        if magnitude > 0:
            direcao_x /= magnitude
            direcao_y /= magnitude
            velocidade = self.Velocidade + 6
            dx = direcao_x * velocidade * delta_time
            dy = direcao_y * velocidade * delta_time

            # Simula o novo centro do rect na tela
            nova_pos_tela_x = self.rect.centerx + dx * self.tile
            novo_rect_x = self.rect.copy()
            novo_rect_x.centerx = nova_pos_tela_x

            self.ColideComBaus(novo_rect_x, BausColisão, parametros)
            if not self.ColideComEstruturas(novo_rect_x, ObjetosColisão):
                self.Loc[0] += dx  # atualiza a posição do jogador no mundo

            nova_pos_tela_y = self.rect.centery + dy * self.tile
            novo_rect_y = self.rect.copy()
            novo_rect_y.centery = nova_pos_tela_y

            self.ColideComBaus(novo_rect_y, BausColisão, parametros)
            if not self.ColideComEstruturas(novo_rect_y, ObjetosColisão):
                self.Loc[1] += dy

            # Atualiza a posição do rect do player com base na posição real
            self.rect.center = (self.rect.centerx, self.rect.centery)

    def ColideComEstruturas(self, novo_rect, ObjetosColisão):
        for estrutura in ObjetosColisão.values():
            if estrutura.rect and novo_rect.colliderect(estrutura.rect):
                return True
        return False
    
    def ColideComBaus(self, novo_rect, BausColisão, parametros):
        for Bau in BausColisão.values():
            if Bau.rect and novo_rect.colliderect(Bau.rect):
                if Bau.Aberto is False:
                    Bau.AbrirBau(self, parametros)

    def ToDicParcial(self):
        return {
            "Nome": self.Nome,
            "Skin": self.SkinNumero,
            "Nivel": self.Nivel,
            "Loc": self.Loc,
            "Esquerda": self.MaoEsquerda,
            "Direita": self.MaoDireita,
            "Angulo": self.Angulo
        }
    
    def ToDicTotal(self):
        return {
            "Nome": self.Nome,
            "Code": self.Code,
            "Skin": self.SkinNumero,
            "Nivel": self.Nivel,
            "Pokemons": self.Pokemons,
            "Inventario": self.Inventario,
            "XP": self.Xp,
            "Ouro": self.Ouro,
            "Velocidade": self.Velocidade,
            "Mochila": self.Mochila,
            "Maestria": self.Maestria,
            "Loc": self.Loc,
            "Esquerda": self.MaoEsquerda,
            "Direita": self.MaoDireita,
        }
    