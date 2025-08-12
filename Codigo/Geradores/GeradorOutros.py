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

        self.imagem_original = self.imagem  # mantém a imagem original para evitar perda de qualidade
        self.angulo = 0  # ângulo inicial
        self.velocidade_rotacao = 10  # graus por frame, ajuste como quiser

    def atualizar(self, tela, cords_atuais, player):
        if self.alvo_reached:
            return

        # Movimento próprio do projétil
        deslocamento = self.direcao * self.velocidade
        self.pos += deslocamento
        self.distancia_percorrida += self.velocidade

        # Faz o projétil girar
        self.angulo = (self.angulo + self.velocidade_rotacao) % 360
        imagem_rotacionada = pygame.transform.rotate(self.imagem_original, self.angulo)
        rect_rotacionado = imagem_rotacionada.get_rect(center=self.rect.center)

        # Calcula diferença de tiles que o cenário se moveu desde o disparo
        diferenca_tiles = pygame.math.Vector2(cords_atuais) - self.cords_iniciais
        diferenca_pixels = diferenca_tiles * 70  # conversão para pixels

        # Posição final de renderização é a posição do projétil ajustada pelo movimento do cenário
        render_pos = self.pos - diferenca_pixels
        rect_rotacionado.center = (int(render_pos.x), int(render_pos.y))

        self.rect = rect_rotacionado

        # Desenha
        tela.blit(imagem_rotacionada, rect_rotacionado)
        
        player.Mirando = True

        self.VerificaColisão(player, tela)

        # Checa distância máxima
        if self.distancia_percorrida >= self.distancia_total:
            self.alvo_reached = True
    
    def VerificaColisão(self, player, tela):
        for alvo_nome, alvo in self.Alvos.items():
            offset_x = alvo.Rect.left - self.rect.left
            offset_y = alvo.Rect.top - self.rect.top
            offset = (offset_x, offset_y)
            self.Offset = offset

            if self.rect.colliderect(alvo.Rect):
                overlap = self.mask.overlap(alvo.Mask, offset)

                if overlap:
                    if self.dados["estilo"] == "bola":
                        overlap_mirando = self.mask.overlap(alvo.MaskMirando, offset)
                        critico = bool(overlap_mirando)
                        alvo.Capturar(self.dados, player, critico)

                    elif self.dados["estilo"] == "fruta":
                        alvo.Frutificar(self.dados, player)

                    self.alvo_reached = True
                    break

