from collections import Counter
import pygame
import math

def extrair_cor_predominante(imagem):
    largura, altura = imagem.get_size()
    contador_cores = Counter()

    for y in range(altura):
        for x in range(largura):
            cor = imagem.get_at((x, y))
            if cor.a > 20:  # Ignora pixels transparentes
                contador_cores[(cor.r, cor.g, cor.b)] += 1

    if contador_cores:
        cor_mais_comum = contador_cores.most_common(1)[0][0]
        return pygame.Color(*cor_mais_comum)
    else:
        return pygame.Color("white")

_ANGLE_STEP = 4  # quantização do ângulo (5° = bom equilíbrio)
_ROT_CACHE = {}  # (id_surface, angulo_q, size) -> surface_rotacionada
_COLOR_CACHE = {}  # id_surface -> cor_predominante

def CacheExtrairCor(img):
    key = id(img)
    c = _COLOR_CACHE.get(key)
    if c is None:
        c = extrair_cor_predominante(img)
        _COLOR_CACHE[key] = c
    return c

def PegarRotaçao(img, angulo_correcao):
    # quantiza o ângulo pra reduzir quantidade de variantes
    ang = int((angulo_correcao % 360) / _ANGLE_STEP) * _ANGLE_STEP
    key = (id(img), ang, img.get_size())
    rot = _ROT_CACHE.get(key)
    if rot is None:
        # use -ang porque você já estava invertendo o sinal
        rot = pygame.transform.rotate(img, -ang)
        _ROT_CACHE[key] = rot
    return rot

def escurecer_cor(cor, fator=0.8):
    """Retorna uma cor mais escura baseada em um fator."""
    return pygame.Color(int(cor.r * fator), int(cor.g * fator), int(cor.b * fator))

def DesenharPlayer(tela, imagem_corpo, posicao):
    x, y = posicao

    # 1) Cor do braço: calcula só uma vez por imagem
    cor_braco = CacheExtrairCor(imagem_corpo)

    mouse_pos = pygame.mouse.get_pos()

    # Ângulo entre boneco e mouse
    dx, dy = mouse_pos[0] - x, mouse_pos[1] - y
    angulo = math.degrees(math.atan2(dy, dx))
    angulo_correcao = angulo - 90
    angulo_rad = math.radians(angulo)

    # 2) Rotacionar o corpo com cache
    corpo_rotacionado = PegarRotaçao(imagem_corpo, angulo_correcao)
    corpo_rect = corpo_rotacionado.get_rect(center=posicao)
    tela.blit(corpo_rotacionado, corpo_rect)

    # Respiração
    t = pygame.time.get_ticks() / 200
    respiracao = math.sin(t) * 4  # amplitude 4 px

    distancia_braco = 58
    profundidade = respiracao

    # pré-calcula seno/cosseno (evita repetir 4x)
    cos_a = math.cos(angulo_rad)
    sin_a = math.sin(angulo_rad)
    cos_perp = math.cos(angulo_rad + math.pi / 2)
    sin_perp = math.sin(angulo_rad + math.pi / 2)

    # Base dos braços (posição lateral)
    offset_x = cos_perp * distancia_braco
    offset_y = sin_perp * distancia_braco

    # Movimento respiratório (ao longo do corpo)
    depth_x = cos_a * profundidade
    depth_y = sin_a * profundidade

    pos_braco_esquerdo = (x - offset_x + depth_x, y - offset_y + depth_y)
    pos_braco_direito = (x + offset_x + depth_x, y + offset_y + depth_y)

    cor_borda = escurecer_cor(cor_braco)

    raio = 10
    raio_borda = 13

    # Desenha os braços com borda
    pygame.draw.circle(tela, cor_borda, pos_braco_esquerdo, raio_borda)
    pygame.draw.circle(tela, cor_braco, pos_braco_esquerdo, raio)
    pygame.draw.circle(tela, cor_borda, pos_braco_direito, raio_borda)
    pygame.draw.circle(tela, cor_braco, pos_braco_direito, raio)
