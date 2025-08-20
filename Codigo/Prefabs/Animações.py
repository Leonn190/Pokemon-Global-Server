import pygame

class Animação:
    def __init__(self, frames, posicao, intervalo=50, duracao=None,
                 ao_terminar=None, loop=True, ping_pong=False,
                 tamanho=1, inverted=False):
        """
        frames: lista de superfícies
        posicao: posição do centro
        tamanho: escala inicial
        inverted: se True, inverte horizontalmente os frames
        """
        self.frames = []
        for frame in frames:
            if inverted:
                frame = pygame.transform.flip(frame, True, False)  # espelha na horizontal
            frame = pygame.transform.scale(
                frame,
                (int(frame.get_width() * tamanho), int(frame.get_height() * tamanho))
            )
            self.frames.append(frame)

        self.pos = posicao
        self.intervalo = intervalo
        self.duracao = duracao
        self.ao_terminar = ao_terminar
        self.loop = loop
        self.ping_pong = ping_pong

        self.index = 0
        self.direcao = 1
        self.ultimo_tempo = pygame.time.get_ticks()
        self.inicio = self.ultimo_tempo

        self.chamou_callback = False
        self.ativo = True

    def atualizar(self, tela, nova_pos=None, multiplicador=1):
        """
        Desenha a animação na tela.
        multiplicador: fator de escala temporário aplicado apenas no frame atual
        (agora com cache de frames escalados por multiplicador)
        """
        if not self.ativo or not self.frames:
            return

        agora = pygame.time.get_ticks()

        # --------- avanço de índice (inalterado) ----------
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

        # --------- seleção do frame com cache de escala ----------
        if 0 <= self.index < len(self.frames):
            # chave de cache arredondada para evitar thrash com floats tipo 1.999999
            try:
                m_key = 1.0 if multiplicador == 1 else round(float(multiplicador), 3)
            except Exception:
                m_key = 1.0

            # prepara atributos de cache se ainda não existirem
            if not hasattr(self, "_cache_mult"):
                self._cache_mult = None
            if not hasattr(self, "_cache_frames"):
                self._cache_frames = None

            if m_key == 1.0:
                # usa frames originais; limpa cache para economizar memória
                frames_to_use = self.frames
                if self._cache_mult is not None:
                    self._cache_mult = None
                    self._cache_frames = None
            else:
                # (re)gera cache somente se multiplicador mudou
                if self._cache_mult != m_key or self._cache_frames is None:
                    scaled = []
                    # usa o multiplicador exato para cálculo de tamanho
                    mul = float(multiplicador)
                    for f in self.frames:
                        w = max(1, int(round(f.get_width()  * mul)))
                        h = max(1, int(round(f.get_height() * mul)))
                        # se o tamanho é idêntico ao original, reaproveita o frame original
                        if (w, h) == f.get_size():
                            scaled.append(f)
                        else:
                            # scale é mais leve que smoothscale por frame
                            scaled.append(pygame.transform.scale(f, (w, h)))
                    self._cache_frames = scaled
                    self._cache_mult   = m_key
                frames_to_use = self._cache_frames

            frame = frames_to_use[self.index]

            pos_desenho = nova_pos if nova_pos is not None else self.pos
            rect = frame.get_rect(center=pos_desenho)
            tela.blit(frame, rect)

        # --------- finalização baseada em duração (inalterado) ----------
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
        