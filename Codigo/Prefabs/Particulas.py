import pygame, random, math

# === Config ===
TILE_SIZE = 70  # px por tile

# Lista global de bursts ativos
_BURSTS = []

class ParticleBurst:
    """
    Burst de partículas em coordenadas de MUNDO (em pixels).
    - pos_mundo: (x,y) em pixels (posição ABSOLUTA no mundo)
    - raio: px (alcance máximo aproximado)
    - quantidade: nº de partículas
    - cores: (r,g,b) OU lista de (r,g,b)/(r,g,b,a)
    - duracao_ms: duração total em ms
    - gravidade: px/s²
    - tamanho: px (lado do quadradinho)

    Observação: a conversão MUNDO->TELA é feita em update_draw, usando a posição
    atual do player (em tiles), assumindo câmera centrada no player.
    """
    __slots__ = ("orig_world", "raio", "dur_ms", "grav", "tamanho",
                 "pixel", "cores", "particulas", "alive")

    def __init__(self, pos_mundo,
                 raio, quantidade, cores, duracao_ms=350, gravidade=0.0, tamanho=2):

        # posição de mundo (px) do estouro
        self.orig_world = pygame.math.Vector2(float(pos_mundo[0]), float(pos_mundo[1]))

        self.raio = float(raio)
        self.dur_ms = float(duracao_ms)
        self.grav = float(gravidade)
        self.tamanho = int(tamanho)

        # normaliza cores para lista
        if isinstance(cores, (list, tuple)) and len(cores) > 0 and isinstance(cores[0], (list, tuple)):
            self.cores = list(cores)
        else:
            self.cores = [cores]

        self.pixel = pygame.Surface((self.tamanho, self.tamanho), pygame.SRCALPHA)

        self.particulas = []
        dur_s = self.dur_ms / 1000.0
        for _ in range(int(quantidade)):
            ang = random.random() * 2.0 * math.pi
            r_alvo = self.raio * (0.6 + 0.4 * random.random())  # 60%..100%
            vel_mod = r_alvo / dur_s  # px/s para chegar ~no raio ao fim
            vx = math.cos(ang) * vel_mod
            vy = math.sin(ang) * vel_mod

            cor = random.choice(self.cores)
            self.particulas.append({
                "pos": self.orig_world.copy(),          # px (mundo)
                "vel": pygame.math.Vector2(vx, vy),     # px/s
                "age": 0.0,                              # ms
                "cor": cor,
            })

        self.alive = True

    def update_draw(self, tela, player_tiles_now, delta_time):
        """
        - player_tiles_now: [tx,ty] (tiles) posição atual do player (câmera centrada nele)
        - delta_time: segundos desde o último frame
        """
        if not self.alive:
            return

        dt = float(delta_time)
        # tiles -> pixels (posição do player no mundo)
        ptx, pty = float(player_tiles_now[0]), float(player_tiles_now[1])
        px = ptx * TILE_SIZE
        py = pty * TILE_SIZE

        screen_w, screen_h = tela.get_size()
        cx, cy = screen_w * 0.5, screen_h * 0.5  # centro da tela

        vivos = 0
        for p in self.particulas:
            if p["age"] >= self.dur_ms:
                continue

            # tempo
            p["age"] += dt * 1000.0
            t = 1.0 if p["age"] >= self.dur_ms else (p["age"] / self.dur_ms)

            # física
            if self.grav != 0.0:
                p["vel"].y += self.grav * dt
            p["pos"] += p["vel"] * dt

            # fade
            alpha = int(255 * (1.0 - t))
            if alpha <= 0:
                continue

            # mundo(px) -> tela(px) com player no centro
            screen_x = p["pos"].x - px + cx
            screen_y = p["pos"].y - py + cy

            # cor + alpha
            cor = p["cor"]
            if len(cor) == 4:
                r, g, b, a0 = cor
                a = int(a0 * (alpha / 255.0))
            else:
                r, g, b = cor
                a = alpha

            self.pixel.fill((r, g, b, a))
            tela.blit(self.pixel, (int(screen_x), int(screen_y)))
            vivos += 1

        self.alive = (vivos > 0)


# ===================== API pública =====================

def adicionar_estouro(pos_mundo, raio, quantidade, cores,
                      duracao_ms=350, gravidade=0.0, tamanho=2):
    """
    Cria um burst a partir de uma posição em MUNDO (px).
    A conversão para a tela é feita em tempo de desenho (update_draw),
    usando a posição atual do player (assumido no centro da tela).
    """
    burst = ParticleBurst(
        pos_mundo,
        raio, quantidade, cores,
        duracao_ms=duracao_ms, gravidade=gravidade, tamanho=tamanho
    )
    _BURSTS.append(burst)


def atualizar_e_desenhar_bursts(tela, player_tiles_atual, delta_time):
    """
    Atualiza e desenha TODOS os bursts ativos (player em TILES).
    """
    if not _BURSTS:
        return
    for b in _BURSTS[:]:
        b.update_draw(tela, player_tiles_atual, delta_time)
        if not b.alive:
            _BURSTS.remove(b)

