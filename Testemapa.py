from perlin_noise import PerlinNoise
import random
import math
from collections import deque

import random
from collections import deque

def GeradorGridBiomasAvancado(largura, altura, seed=None):
    if seed is not None:
        random.seed(seed)

    total_celulas = largura * altura

    biomas_percentuais = [
        ("oceano", 0.25),
        ("praia", 0.05),
        ("campo", 0.16),
        ("floresta", 0.145),
        ("deserto", 0.095),
        ("neve", 0.085),
        ("rochoso", 0.065),
        ("pantano", 0.06),
        ("terra morta", 0.045),
        ("terreno encantado", 0.045),
    ]

    # Calcular a quantidade de células por bioma
    biomas_com_contagem = []
    soma = 0
    for nome, p in biomas_percentuais:
        quantidade = int(p * total_celulas)
        biomas_com_contagem.append([nome, quantidade])
        soma += quantidade

    # Corrigir diferença de arredondamento
    diferenca = total_celulas - soma
    if diferenca != 0:
        biomas_com_contagem[0][1] += diferenca

    grid = [[None for _ in range(largura)] for _ in range(altura)]
    celulas_livres = {(x, y) for x in range(largura) for y in range(altura)}

    def vizinhos(x, y):
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < largura and 0 <= ny < altura:
                yield (nx, ny)

    mapa_biomas = {nome: qtd for nome, qtd in biomas_com_contagem}

    def espalha_bioma(nome_bioma, quantidade, fontes=None, condicao_vizinho=None, forcar=False):
        colocados = 0
        if not fontes:
            fontes = [random.choice(list(celulas_livres))]
        fila = deque(fontes)

        while fila and colocados < quantidade:
            x, y = fila.popleft()
            if (x, y) not in celulas_livres:
                continue

            if condicao_vizinho and not any(grid[vy][vx] == condicao_vizinho for vx, vy in vizinhos(x, y)):
                if not forcar:
                    continue

            grid[y][x] = nome_bioma
            celulas_livres.remove((x, y))
            colocados += 1

            for viz in vizinhos(x, y):
                if viz in celulas_livres:
                    fila.append(viz)

        return colocados

    # 1. Oceano
    centro_oceano = random.choice(list(celulas_livres))
    colocados = espalha_bioma("oceano", mapa_biomas["oceano"], fontes=[centro_oceano])
    mapa_biomas["oceano"] -= colocados

    # 2. Praia (sempre ao lado do oceano)
    candidatos_praia = [(x, y) for x, y in celulas_livres if any(grid[vy][vx] == "oceano" for vx, vy in vizinhos(x, y))]
    random.shuffle(candidatos_praia)
    colocados = espalha_bioma("praia", mapa_biomas["praia"], fontes=candidatos_praia, condicao_vizinho="oceano", forcar=True)
    mapa_biomas["praia"] -= colocados

    # 3. Demais biomas
    for nome in [b[0] for b in biomas_com_contagem if b[0] not in ("oceano", "praia")]:
        if mapa_biomas[nome] > 0:
            espalha_bioma(nome, mapa_biomas[nome])

    # 4. Preencher qualquer célula restante com o bioma mais comum (ajuste final)
    mais_comum = max(biomas_com_contagem, key=lambda b: b[1])[0]
    for x, y in list(celulas_livres):
        grid[y][x] = mais_comum

    return grid


# Exemplo de uso:
if __name__ == "__main__":
    largura = 100
    altura = 100
    seed = 23

    grid_biomas = GeradorGridBiomasAvancado(largura, altura, seed)

    from collections import Counter
    flat = [b for linha in grid_biomas for b in linha]
    contagem = Counter(flat)
    print("Contagem de biomas gerados:", contagem)

from PIL import Image

from PIL import Image

def desenhar_mapa_imagem(grid_biomas, tamanho_bloco=4, arquivo_saida="mapa.png"):
    """
    Gera uma imagem do mapa a partir da grid de biomas.

    Args:
        grid_biomas (list[list[str]]): grid 2D com nomes dos biomas
        tamanho_bloco (int): tamanho em pixels de cada bloco na imagem
        arquivo_saida (str): nome do arquivo PNG gerado
    """

    altura = len(grid_biomas)
    largura = len(grid_biomas[0]) if altura > 0 else 0

    # Cores definidas para todos os 10 biomas
    cores = {
        "campo": (150, 220, 150),           # verde claro
        "floresta": (30, 100, 30),          # verde escuro
        "pantano": (90, 110, 90),           # verde acinzentado
        "praia": (255, 230, 180),           # areia clara
        "deserto": (255, 200, 100),         # laranja claro
        "neve": (240, 240, 240),            # branco sujo
        "oceano": (30, 60, 150),            # azul profundo
        "terra morta": (100, 80, 60),       # marrom escuro
        "terreno encantado": (180, 100, 255), # roxo mágico
        "rochoso": (120, 120, 120),         # cinza médio
    }

    img = Image.new("RGB", (largura * tamanho_bloco, altura * tamanho_bloco))

    for y in range(altura):
        for x in range(largura):
            bioma = grid_biomas[y][x]
            cor = cores.get(bioma, (0, 0, 0))  # Preto se bioma não for reconhecido

            for py in range(tamanho_bloco):
                for px in range(tamanho_bloco):
                    img.putpixel((x * tamanho_bloco + px, y * tamanho_bloco + py), cor)

    img.save(arquivo_saida)
    print(f"Imagem salva em {arquivo_saida}")

desenhar_mapa_imagem(grid_biomas)