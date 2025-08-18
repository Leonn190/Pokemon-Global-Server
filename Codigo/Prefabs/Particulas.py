import pygame
import random
import math

class ParticleBurst:
    """
    Burst de partículas ancorado no MUNDO (px), mas criado a partir de uma
    posição de TELA (px). A posição de tela é convertida para mundo no
    primeiro update, usando o player no centro da câmera.
    """
    __slots__ = ("screen_pos", "orig_world_px", "inicializado",
                 "raio_px", "dur_ms", "grav_px_s2", "tamanho_px",
                 "pixel", "cores", "particulas", "alive")

    def __init__(self, screen_pos, raio_px, quantidade, cores,
                 duracao_ms=350, gravidade_px_s2=0.0, tamanho_px=2):
        # ancora inicial: posição na TELA (px). Converteremos para MUNDO no 1º update
        self.screen_pos = pygame.math.Vector2(screen_pos)
        self.orig_world_px = pygame.math.Vector2(0, 0)  # definido no 1º update
        self.inicializado = False

        self.raio_px = raio_px
        self.dur_ms = duracao_ms
        self.grav_px_s2 = gravidade_px_s2
        self.tamanho_px = tamanho_px

        if isinstance(cores, (list, tuple)) and cores and isinstance(cores[0], (list, tuple)):
            self.cores = list(cores)
        else:
            self.cores = [cores]

        self.pixel = pygame.Surface((self.tamanho_px, self.tamanho_px), pygame.SRCALPHA)

        # gera partículas (pos será definida no 1º update)
        self.particulas = []
        dur_s = self.dur_ms / 1000
        for _ in range(int(quantidade)):
            ang = random.random() * 2 * math.pi
            r_alvo = self.raio_px * (0.6 + 0.4 * random.random())  # 60%..100%
            vel_mod = r_alvo / dur_s                               # px/s
            vel = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * vel_mod
            cor = random.choice(self.cores)
            self.particulas.append({
                "pos": pygame.math.Vector2(0, 0),  # setado no 1º update
                "vel": vel,
                "age": 0.0,                         # ms
                "cor": cor,
            })

        self.alive = True

    def _inicializar_no_mundo(self, tela, player_tiles_now, tile_size):
        # player em tiles -> mundo (px)
        px_player = pygame.math.Vector2(player_tiles_now) * tile_size
        # centro da tela
        w, h = tela.get_size()
        center = pygame.math.Vector2(w * 0.5, h * 0.5)
        # tela -> mundo (px)
        self.orig_world_px = px_player + (self.screen_pos - center)
        # posiciona todas as partículas no mesmo ponto inicial
        for p in self.particulas:
            p["pos"].update(self.orig_world_px)
        self.inicializado = True

    def update_draw(self, tela, player_tiles_now, delta_time, tile_size):
        """
        player_tiles_now: (tx, ty) do player (tiles) — câmera centrada nele
        """
        if not self.alive:
            return

        if not self.inicializado:
            self._inicializar_no_mundo(tela, player_tiles_now, tile_size)

        # player em tiles -> pixels (mundo)
        px_player = pygame.math.Vector2(player_tiles_now) * tile_size
        # centro da tela
        w, h = tela.get_size()
        center = pygame.math.Vector2(w * 0.5, h * 0.5)

        vivos = 0
        for p in self.particulas:
            if p["age"] >= self.dur_ms:
                continue

            # tempo
            p["age"] += delta_time * 1000
            t = min(1.0, p["age"] / self.dur_ms)

            # física
            if self.grav_px_s2:
                p["vel"].y += self.grav_px_s2 * delta_time
            p["pos"] += p["vel"] * delta_time

            # fade
            alpha = int(255 * (1 - t))
            if alpha <= 0:
                continue

            # mundo(px) -> tela(px) com player no centro
            screen_pos = (p["pos"] - px_player) + center

            # cor + alpha
            cor = p["cor"]
            if len(cor) == 4:
                r, g, b, a0 = cor
                a = int(a0 * (alpha / 255))
            else:
                r, g, b = cor
                a = alpha

            self.pixel.fill((r, g, b, a))
            tela.blit(self.pixel, (int(screen_pos.x), int(screen_pos.y)))
            vivos += 1

        self.alive = vivos > 0


class BurstManager:
    """
    Gerencia bursts. API: adicionar passando posição em PIXELS DE TELA (centro).
    """
    def __init__(self, tile_size=70, debug=False):
        self._bursts = []
        self._tile_size = tile_size
        self._debug = debug

    @property
    def ativos(self):
        return len(self._bursts)

    def set_tile_size(self, tile_size):
        self._tile_size = tile_size

    def clear(self):
        self._bursts.clear()

    def adicionar_estouro(self, pos_tela, raio_px, quantidade, cores,
                          duracao_ms=500, gravidade_px_s2=0.0, tamanho_px=4):
        """
        pos_tela: (x,y) em pixels da TELA — centro do estouro.
        Não precisa passar player nem tamanho da tela aqui.
        """
        burst = ParticleBurst(
            pos_tela, raio_px, quantidade, cores,
            duracao_ms=duracao_ms, gravidade_px_s2=gravidade_px_s2, tamanho_px=tamanho_px
        )
        self._bursts.append(burst)
        if self._debug:
            print(f"[BurstManager] add -> total={len(self._bursts)} pos_tela={pos_tela}")

    def atualizar_e_desenhar_bursts(self, tela, player_tiles_atual, delta_time):
        if not self._bursts:
            return
        for b in self._bursts[:]:
            b.update_draw(tela, player_tiles_atual, delta_time, self._tile_size)
            if not b.alive:
                self._bursts.remove(b)
        if self._debug:
            print(f"[BurstManager] after draw -> total={len(self._bursts)}")
