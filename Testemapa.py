import random
from collections import deque
from PIL import Image

# cores (bioma 1..7 -> index 0..6)
CORES_BIOMAS = [
    {"cor": (34, 139, 34),   "seeds": 3, "expand": 0.8, "nome": "Floresta"},
    {"cor": (237, 201, 175), "seeds": 2, "expand": 0.8, "nome": "Deserto"},
    {"cor": (0, 105, 148),   "seeds": 4, "expand": 0.8, "nome": "Oceano"},
    {"cor": (128, 0, 0),     "seeds": 1, "expand": 0.5, "nome": "Vulcânico"},
    {"cor": (154, 205, 50),  "seeds": 4, "expand": 0.7, "nome": "Planície"},
    {"cor": (205, 133, 63),  "seeds": 2, "expand": 0.6, "nome": "Savana"},
    {"cor": (169, 221, 118), "seeds": 1, "expand": 0.5, "nome": "Pântano"},
    {"cor": (138, 43, 226),  "seeds": 1, "expand": 0.4, "nome": "Terra Encantada"},
    {"cor": (255, 255, 255), "seeds": 2, "expand": 0.6, "nome": "Neve"}
]

def gerar_bloco_biomas(width=1200, height=1200, biomas=CORES_BIOMAS, use_diagonals=True, seed=None):
    if seed is not None:
        random.seed(seed)

    num_biomas = len(biomas)
    mapa = [[-1 for _ in range(width)] for _ in range(height)]

    # Gera seeds por bioma
    seeds_by_bioma = [[] for _ in range(num_biomas)]
    for b, info in enumerate(biomas):
        total_seeds = info["seeds"]
        for _ in range(total_seeds):
            while True:
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                if mapa[y][x] == -1:
                    mapa[y][x] = b
                    seeds_by_bioma[b].append((x, y))
                    break

    # Intercala as seeds na fila inicial
    queue = deque()
    max_seeds = max(len(s) for s in seeds_by_bioma)
    for s in range(max_seeds):
        for b in range(num_biomas):
            if s < len(seeds_by_bioma[b]):
                x, y = seeds_by_bioma[b][s]
                queue.append((x, y, b))

    # Vizinhança
    if use_diagonals:
        neigh = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    else:
        neigh = [(1,0),(-1,0),(0,1),(0,-1)]

    # Expansão por bioma
    while queue:
        x, y, b = queue.popleft()
        expand_chance = biomas[b]["expand"]
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= width or ny >= height:
                continue
            if mapa[ny][nx] != -1:
                continue
            if random.random() < expand_chance:
                mapa[ny][nx] = b
                queue.append((nx, ny, b))

    # Preencher buracos (-1)
    for y in range(height):
        for x in range(width):
            if mapa[y][x] == -1:
                counts = {}
                for dx, dy in neigh:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and mapa[ny][nx] != -1:
                        counts[mapa[ny][nx]] = counts.get(mapa[ny][nx], 0) + 1
                if counts:
                    mapa[y][x] = max(counts.items(), key=lambda it: it[1])[0]
                else:
                    mapa[y][x] = random.randrange(num_biomas)

    return mapa


def smooth_map(mapa, iterations=1, min_same_neighbors=2, use_diagonals=True):
    """Passada de limpeza: remove ilhas pequenas reatribuindo células
       cujo número de vizinhos do mesmo bioma seja menor que min_same_neighbors."""
    height = len(mapa)
    width = len(mapa[0])
    if use_diagonals:
        neigh = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    else:
        neigh = [(1,0),(-1,0),(0,1),(0,-1)]

    for _ in range(iterations):
        newmap = [row[:] for row in mapa]
        for y in range(height):
            for x in range(width):
                cur = mapa[y][x]
                same = 0
                counts = {}
                for dx, dy in neigh:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < width and 0 <= ny < height:
                        nb = mapa[ny][nx]
                        counts[nb] = counts.get(nb, 0) + 1
                        if nb == cur:
                            same += 1
                if same < min_same_neighbors:
                    # troca para o bioma majoritário dos vizinhos (suaviza ilhas)
                    if counts:
                        newmap[y][x] = max(counts.items(), key=lambda it: it[1])[0]
        mapa = newmap
    return mapa

def salvar_imagem_mapa(mapa, nome_arquivo="mapa.png"):
    height = len(mapa)
    width = len(mapa[0])
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    cores = [b["cor"] for b in CORES_BIOMAS]

    for y in range(height):
        for x in range(width):
            bi = mapa[y][x]
            if 0 <= bi < len(cores):
                pixels[x, y] = cores[bi]
            else:
                pixels[x, y] = (0, 0, 0)  # Cor fallback para biomas inválido
    img.save(nome_arquivo)

# ========== Exemplo de uso (teste rápido) ==========
if __name__ == "__main__":
    # test smaller for quick preview
    bloco = gerar_bloco_biomas(width=1200, height=1200, biomas=CORES_BIOMAS,use_diagonals=True, seed=60)
    bloco = smooth_map(bloco, iterations=2, min_same_neighbors=5)
    salvar_imagem_mapa(bloco, nome_arquivo="mapa.png")
    print("foi")

    # Para gerar bloco 1200x1200 e montar mapa 3600x3600 (pode demorar e usar memória)
    # bloco1200 = gerar_bloco_biomas(1200,1200, num_biomas=7, seeds_per_bioma=60, expand_chance=0.62, seed=123)
    # bloco1200 = smooth_map(bloco1200, iterations=2, min_same_neighbors=2)
    # mapa3600 = tile_block_to_map(bloco1200, 3, 3)
    # salvar_imagem_mapa(mapa3600, nome_arquivo="mapa_3600x3600.png")
