import pygame

class Projetil:
    def __init__(self, pos, cords_iniciais, dados, imagem, alvos):
        self.pos = pygame.math.Vector2(pos)  # posição em pixels do disparo
        self.cords_iniciais = pygame.math.Vector2(cords_iniciais)  # posição do player no momento do disparo (em tiles)
        self.dados = dados
        self.alvo = pygame.math.Vector2(pygame.mouse.get_pos())

        if self.dados["estilo"] == "bola":
            self.velocidade = 5
            self.distancia_total = 520
        elif self.dados["estilo"] == "fruta":
            self.velocidade = 4
            self.distancia_total = 420

        self.distancia_percorrida = 0

        # Direção de movimento
        direcao = self.alvo - self.pos
        self.direcao = direcao.normalize() if direcao.length() != 0 else pygame.math.Vector2(0, 0)

        # Imagem e colisão
        self.imagem = pygame.transform.scale(imagem, (35, 35))
        self.mask = pygame.mask.from_surface(self.imagem)
        self.rect = self.imagem.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        self.alvo_reached = False

        self.Alvos = alvos

    def atualizar(self, tela, cords_atuais, player):
        if self.alvo_reached:
            return

        # Movimento próprio do projétil
        deslocamento = self.direcao * self.velocidade
        self.pos += deslocamento
        self.distancia_percorrida += self.velocidade

        # Calcula diferença de tiles que o cenário se moveu desde o disparo
        diferenca_tiles = pygame.math.Vector2(cords_atuais) - self.cords_iniciais
        diferenca_pixels = diferenca_tiles * 70  # conversão para pixels

        # Posição final de renderização é a posição do projétil ajustada pelo movimento do cenário
        render_pos = self.pos - diferenca_pixels

        # Atualiza rect
        self.rect.center = (int(render_pos.x), int(render_pos.y))

        # Desenha
        tela.blit(self.imagem, self.rect)
        
        player.Mirando = True

        self.VerificaColisão(player, tela)

        # Checa distância máxima
        if self.distancia_percorrida >= self.distancia_total:
            self.alvo_reached = True
    
    def VerificaColisão(self, player, tela):
        
        for alvo in self.Alvos.values():
            # Calcula offset entre o projétil e o alvo
            offset_x = alvo.Rect.left - self.rect.left
            offset_y = alvo.Rect.top - self.rect.top
            offset = (offset_x, offset_y)

            # Guarda último offset calculado (pode ser útil para debug)
            self.Offset = offset

            # Verifica colisão de bounding box primeiro (rápido)
            if self.rect.colliderect(alvo.Rect):
                # Colisão pixel-perfect
                if self.mask.overlap(alvo.Mask, offset):
                    alvo.Capturar(player)
                    self.alvo_reached = True
                    break  # Para no primeiro alvo atingido

