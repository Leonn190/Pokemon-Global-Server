import math
import pygame

from Codigo.Prefabs.FunçõesPrefabs import extrair_cor_predominante, escurecer_cor, texto_com_borda

class Player:
    def __init__(self, Informações, Skins):

        self.Code = Informações["Code"]
        self.Nome = Informações["Nome"]

        self.Pokemons = Informações["Pokemons"]
        self.Inventario = Informações["Inventario"]
        self.Ouro = Informações["Ouro"]
        self.SkinNumero = Informações["Skin"]
        self.Skin = Skins[self.SkinNumero]
        self.SkinRedimensionada = pygame.transform.scale(self.Skin, (115, 127))
        self.Nivel = Informações["Nivel"]
        self.Xp = Informações["XP"]
        
        self.Mochila = Informações["Mochila"]
        self.Velocidade = Informações["Velocidade"]
        self.Maestria = Informações["Maestria"]

        self.Loc = Informações["Loc"]

        self.MaoEsquerda = Informações.get("Esquerda",None)
        self.MaoDireita = Informações.get("Direita",None)
        self.Angulo = 90

        self.rect = pygame.Rect(0, 0, 115, 127)
        self.rect.center = (self.Loc[0], self.Loc[1])  # Pos inicial

        self.tile = 70

    def Atualizar(self, tela, delta_time, mapa, fonte):
        self.mover(delta_time, mapa.ChunksCarregados)

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
        self.desenhar_bracos(tela, (x_centro, y_centro), cor_braco, math.radians(angulo))

        # Nome flutuante
        texto_surface = fonte.render(self.Nome, True, (255, 255, 255))
        flutuacao = math.sin(pygame.time.get_ticks() / 200) * 5
        texto_rect = texto_surface.get_rect(center=(x_centro, y_centro - 80 + flutuacao))
        texto_com_borda(tela, self.Nome, fonte, texto_rect.topleft, (255, 255, 255), (0, 0, 0))

    def desenhar_bracos(self, tela, centro, cor_braco, angulo_rad):
        x_centro, y_centro = centro
        t = pygame.time.get_ticks() / 200
        respiracao = math.sin(t) * 4

        distancia_braco = 58
        profundidade = respiracao

        # Offset padrão do braço (posição base)
        offset_x = math.cos(angulo_rad + math.pi / 2) * distancia_braco
        offset_y = math.sin(angulo_rad + math.pi / 2) * distancia_braco

        # Profundidade (para simular 3D leve)
        depth_x = math.cos(angulo_rad) * profundidade
        depth_y = math.sin(angulo_rad) * profundidade

        # Movimento adicional ao clicar
        mouse_botoes = pygame.mouse.get_pressed()
        movimento_extra = 25

        # Leve rotação angular (5 graus) no movimento de arremesso
        desvio_angular = math.radians(6)

        if mouse_botoes[0]:  # botão esquerdo
            angulo_lancamento = angulo_rad - desvio_angular
            offset_extra = movimento_extra + 10  # mais impulso
            offset_x_esq = offset_x - math.cos(angulo_lancamento) * offset_extra
            offset_y_esq = offset_y - math.sin(angulo_lancamento) * offset_extra
        else:
            offset_x_esq, offset_y_esq = offset_x, offset_y

        if mouse_botoes[2]:  # botão direito
            angulo_lancamento = angulo_rad + desvio_angular
            offset_extra = movimento_extra + 10
            offset_x_dir = offset_x + math.cos(angulo_lancamento) * offset_extra
            offset_y_dir = offset_y + math.sin(angulo_lancamento) * offset_extra
        else:
            offset_x_dir, offset_y_dir = offset_x, offset_y

        # Cálculo da posição final de cada braço
        pos_braco_esquerdo = (x_centro - offset_x_esq + depth_x, y_centro - offset_y_esq + depth_y)
        pos_braco_direito = (x_centro + offset_x_dir + depth_x, y_centro + offset_y_dir + depth_y)

        # Desenhar com sombra/borda
        cor_borda = escurecer_cor(cor_braco)
        raio = 10
        raio_borda = 13

        for pos in [pos_braco_esquerdo, pos_braco_direito]:
            pygame.draw.circle(tela, cor_borda, pos, raio_borda)
            pygame.draw.circle(tela, cor_braco, pos, raio)

    def mover(self, delta_time, chunks_visiveis):
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

            # Simula o novo centro do rect na tela (baseado na posição atual)
            nova_pos_tela_x = self.rect.centerx + dx * self.tile
            novo_rect_x = self.rect.copy()
            novo_rect_x.centerx = nova_pos_tela_x

            if not self.colide_com_estruturas(novo_rect_x, chunks_visiveis):
                self.Loc[0] += dx  # atualiza a posição do jogador no mundo

            nova_pos_tela_y = self.rect.centery + dy * self.tile
            novo_rect_y = self.rect.copy()
            novo_rect_y.centery = nova_pos_tela_y

            if not self.colide_com_estruturas(novo_rect_y, chunks_visiveis):
                self.Loc[1] += dy

            # Atualiza a posição do rect do player com a posição na tela (assumindo fixo)
            self.rect.center = (self.rect.centerx, self.rect.centery)

    def colide_com_estruturas(self, novo_rect, chunks_visiveis):
        for chunk in chunks_visiveis.values():
            for estrutura in chunk.values():
                if estrutura.rect and novo_rect.colliderect(estrutura.rect):
                    return True
        return False

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
    