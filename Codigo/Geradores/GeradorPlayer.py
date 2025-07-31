import math
import pygame

from Codigo.Prefabs.FunçõesPrefabs import extrair_cor_predominante, escurecer_cor

class Player:
    def __init__(self, Informações, Skins):

        self.Code = Informações["Code"]

        self.Pokemons = Informações["Pokemons"]
        self.Inventario = Informações["Inventario"]
        self.Ouro = Informações["Ouro"]
        self.SkinNumero = Informações["Skin"]
        self.Skin = Skins[self.SkinNumero]
        self.Nivel = Informações["Nivel"]
        self.Xp = Informações["XP"]
        
        self.Mochila = Informações["Mochila"]
        self.Velocidade = Informações["Velocidade"]
        self.Maestria = Informações["Maestria"]

        self.Loc = Informações["Loc"]

        self.MaoEsquerda = None
        self.MaoDireita = None

    def Atualizar(self, tela):
        self.mover()

        largura_tela, altura_tela = tela.get_size()
        x_centro = largura_tela // 2
        y_centro = altura_tela // 2

        # Posição real no mundo
        mundo_x, mundo_y = self.Loc

        # Câmera desloca o mundo ao redor do jogador
        camera_offset_x = mundo_x - x_centro
        camera_offset_y = mundo_y - y_centro

        # Posição relativa à tela
        x = x_centro
        y = y_centro

        imagem_corpo = self.Skin
        cor_braco = extrair_cor_predominante(imagem_corpo)
        mouse_pos = pygame.mouse.get_pos()

        # Corrigir ângulo com base na posição relativa do mouse
        dx, dy = mouse_pos[0] - x, mouse_pos[1] - y
        angulo = math.degrees(math.atan2(dy, dx))
        angulo_correcao = angulo - 90
        angulo_rad = math.radians(angulo)

        corpo_rotacionado = pygame.transform.rotate(imagem_corpo, -angulo_correcao)
        corpo_rect = corpo_rotacionado.get_rect(center=(x, y))
        tela.blit(corpo_rotacionado, corpo_rect)

        t = pygame.time.get_ticks() / 200
        respiracao = math.sin(t) * 4

        distancia_braco = 58
        profundidade = respiracao

        offset_x = math.cos(angulo_rad + math.pi / 2) * distancia_braco
        offset_y = math.sin(angulo_rad + math.pi / 2) * distancia_braco

        depth_x = math.cos(angulo_rad) * profundidade
        depth_y = math.sin(angulo_rad) * profundidade

        pos_braco_esquerdo = (x - offset_x + depth_x, y - offset_y + depth_y)
        pos_braco_direito = (x + offset_x + depth_x, y + offset_y + depth_y)

        cor_borda = escurecer_cor(cor_braco)
        raio = 10
        raio_borda = 13

        for pos in [pos_braco_esquerdo, pos_braco_direito]:
            pygame.draw.circle(tela, cor_borda, pos, raio_borda)
            pygame.draw.circle(tela, cor_braco, pos, raio)

    def mover(self):
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

        # Calcula magnitude do vetor
        magnitude = math.hypot(direcao_x, direcao_y)

        if magnitude > 0:
            # Normaliza vetor e aplica velocidade
            velocidade = (self.Velocidade + 1) / 20
            direcao_x /= magnitude
            direcao_y /= magnitude

            self.Loc[0] += direcao_x * velocidade
            self.Loc[1] += direcao_y * velocidade
