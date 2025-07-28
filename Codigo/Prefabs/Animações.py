import pygame

class Animação:
    def __init__(self, frames, posicao, intervalo=50, duracao=None, ao_terminar=None, loop=True, ping_pong=False, tamanho=1):
        self.frames = [pygame.transform.scale(frame, (int(frame.get_width() * tamanho), int(frame.get_height() * tamanho))) for frame in frames]
        self.pos = posicao
        self.intervalo = intervalo  # tempo entre frames (ms)
        self.duracao = duracao  # tempo total da animação (ms) ou None para infinita
        self.ao_terminar = ao_terminar
        self.loop = loop
        self.ping_pong = ping_pong  # se True, vai e volta (efeito de "respirar")

        self.index = 0
        self.direcao = 1
        self.ultimo_tempo = pygame.time.get_ticks()
        self.inicio = self.ultimo_tempo

        self.chamou_callback = False
        self.ativo = True

    def atualizar(self, tela):
        if not self.ativo:
            return

        agora = pygame.time.get_ticks()

        # Controle de animação
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

        # Desenho
        if 0 <= self.index < len(self.frames):
            frame = self.frames[self.index]
            rect = frame.get_rect(center=self.pos)
            tela.blit(frame, rect)

        # Finalização baseada em duração
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
