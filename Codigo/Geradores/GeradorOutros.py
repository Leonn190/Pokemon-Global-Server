import pygame

class Projetil:
    
    def __init__(self, pos, cords_iniciais, dados, imagem, alvos):
        self.pos = pygame.math.Vector2(pos)  # posição em pixels do disparo
        self.cords_iniciais = pygame.math.Vector2(cords_iniciais)  # posição do player no momento do disparo (em tiles)
        self.dados = dados
        self.alvo = pygame.math.Vector2(pygame.mouse.get_pos())

        if self.dados["estilo"] == "bola":
            self.velocidade = 380
            self.distancia_total = 520
            if self.dados["nome"] == "Sniperball":
                self.velocidade = 560
                self.distancia_total = 620
            if self.dados["nome"] == "Fastball":
                self.velocidade = 540
        elif self.dados["estilo"] == "fruta":
            self.velocidade = 340
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
        self.velocidade_rotacao = 90  # graus por frame, ajuste como quiser

    def atualizar(self, tela, cords_atuais, player, delta_time):

        if self.alvo_reached:
            return

        # Movimento do projétil (direção deve ser unitária)
        deslocamento = self.direcao * (self.velocidade * float(delta_time))
        self.pos += deslocamento
        # acumula distância percorrida em pixels (robusto mesmo se a direção variar)
        self.distancia_percorrida += deslocamento.length()

        # Rotação time-based
        self.angulo = (self.angulo + self.velocidade_rotacao * float(delta_time)) % 360
        imagem_rotacionada = pygame.transform.rotate(self.imagem_original, self.angulo)

        # Rect centrado na posição atual (ajustada pelo deslocamento do cenário)
        # diferença de tiles que o cenário andou desde o disparo
        diferenca_tiles = pygame.math.Vector2(cords_atuais) - self.cords_iniciais
        diferenca_pixels = diferenca_tiles * 70  # conversão tiles->pixels

        render_pos = self.pos - diferenca_pixels
        rect_rotacionado = imagem_rotacionada.get_rect(center=(int(render_pos.x), int(render_pos.y)))
        self.rect = rect_rotacionado

        # Desenho
        tela.blit(imagem_rotacionada, rect_rotacionado)

        # Estado do player
        player.Mirando = True

        # Colisão
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

