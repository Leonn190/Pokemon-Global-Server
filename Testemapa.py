# -*- coding: utf-8 -*-
# Mapa 1200x1200 com relevo (noise), lagos e biomas (com 3 biomas especiais únicos sólidos).
# Dependências: numpy, Pillow
# pip install numpy pillow

import numpy as np
from PIL import Image
import math
import random
from collections import deque, defaultdict

# ===================== Parâmetros principais / TUNING =====================
W, H = 2000, 2000
SEED = random.randint(0,1000)
random.seed(SEED)
np.random.seed(SEED)

# ---------- LAND vs OCEAN ----------
SEA_LEVEL_BASE = 0.45     # nível do mar “neutro”
LAND_MASS_BIAS = 0.00     # + => MAIS OCEANO (sobe o mar) / - => MAIS TERRA (desce o mar)
SEA_LEVEL = float(np.clip(SEA_LEVEL_BASE + LAND_MASS_BIAS, 0.02, 0.98))

MOUNTAIN_LEVEL = 0.75     # chão alto

# ====== LAGOS (controle por rate) ======
LAKE_RATE = 0.45            # prob. bruta de um candidato virar lago
LAKE_MOISTURE_MIN = 0.70    # candidato precisa ser úmido
LAKE_MAX_ELEV = SEA_LEVEL + 0.08
LAKE_SMOOTH_RADIUS = 1      # 0=sem suavização; 1..2 fecha grãos

# ---- Tamanhos BASE (fração da ÁREA DE TERRA) e multiplicadores por BIOMA ----
# Mínimos para biomas comuns (o resto vira PLAIN)
MIN_FRAC_SNOW   = 0.03
MIN_FRAC_DESERT = 0.06
MIN_FRAC_FOREST = 0.12

# Especiais: blob único por bioma (alvo como fração da TERRA)
SPECIAL_RATES_VOLCAN = 0.01
SPECIAL_RATES_MAGIC  = 0.01
SPECIAL_RATES_SWAMP  = 0.01

# >>> Multiplicadores de tamanho (um por bioma). 1.0 = padrão; >1 aumenta; <1 reduz.
SIZE_MULT = {
    "LAKE":         1.00,
    "SNOW":         1.00,
    "DESERT":       1.00,
    "FOREST":       1.00,
    "VULCANO":      1.00,
    "TERRA_MAGICA": 1.00,
    "PANTANO":      1.00,
}

# Critérios auxiliares dos especiais
VOLCAN_MIN_COAST_DIST   = 6    # “distância” do mar (dilatação)
SWAMP_NEAR_LAKE_RADIUS  = 2    # pântano prefere borda de lago
SWAMP_NEAR_COAST_RADIUS = 3    # fallback: perto da costa
SWAMP_LOWLAND_MAX       = SEA_LEVEL + 0.06
SWAMP_MOIST_MIN         = 0.60

# Solidez dos especiais (morfologia)
SPECIAL_SOLID_CLOSE_RADIUS = 2
SPECIAL_SOLID_OPEN_RADIUS  = 0

# ---- KNOBS dos biomas comuns ----
TEMP_SNOW_MAX = 0.25
MOIST_FOREST_MIN = 0.55
MOIST_DESERT_MAX = 0.35
TEMP_HOT_MIN = 0.65

# --------- Limpeza de “manchinhas” (componentes muito pequenos) ----------
MIN_PATCH_SIZE_SNOW   = 1500   # pixels
MIN_PATCH_SIZE_DESERT = 1500   # pixels

# Paleta
COLORS = {
    "OCEAN":        (20, 60, 150),
    "LAKE":         (40, 90, 170),
    "DESERT":       (238, 214, 87),
    "PLAIN":        (120, 190, 90),
    "FOREST":       (50, 120, 60),
    "SNOW":         (235, 240, 245),
    "HIGH":         (160, 150, 140),  # debug opcional
    # Especiais (1 blob cada):
    "VULCANO":      (150, 20, 20),
    "TERRA_MAGICA": (150, 60, 200),
    "PANTANO":      (110, 110, 110),
}

# ===================== Utilidades de noise (FBM caseiro) =====================
def value_noise(shape, cell=64, rng=np.random):
    h, w = shape
    gw = max(2, int(math.ceil(w / cell)) + 1)
    gh = max(2, int(math.ceil(h / cell)) + 1)
    grid = rng.rand(gh, gw)
    yy = np.linspace(0, gh - 1, h)
    xx = np.linspace(0, gw - 1, w)
    X, Y = np.meshgrid(xx, yy)
    x0 = np.floor(X).astype(int); y0 = np.floor(Y).astype(int)
    x1 = np.clip(x0 + 1, 0, gw - 1); y1 = np.clip(y0 + 1, 0, gh - 1)
    sx = X - x0; sy = Y - y0
    v00 = grid[y0, x0]; v10 = grid[y0, x1]
    v01 = grid[y1, x0]; v11 = grid[y1, x1]
    i1 = v00 * (1 - sx) + v10 * sx
    i2 = v01 * (1 - sx) + v11 * sx
    out = i1 * (1 - sy) + i2 * sy
    return out

def fbm(shape, octaves=6, lacunarity=2.0, gain=0.5, base_cell=256, rng=np.random):
    h, w = shape
    total = np.zeros((h, w), dtype=np.float32)
    amp = 1.0
    freq_cell = base_cell
    for _ in range(octaves):
        n = value_noise((h, w), cell=max(4, int(freq_cell)), rng=rng)
        total += amp * n
        amp *= gain
        freq_cell /= lacunarity
    total -= total.min()
    total /= (total.max() + 1e-9)
    return total

def normalize01(arr):
    arr = arr.astype(np.float32)
    arr -= arr.min()
    m = arr.max()
    if m > 0: arr /= m
    return arr

# ===================== Gera campos base =====================
def generate_elevation(shape):
    base = fbm(shape, octaves=7, lacunarity=2.1, gain=0.52, base_cell=220, rng=np.random)
    h, w = shape
    yy = np.linspace(-1, 1, h)
    xx = np.linspace(-1, 1, w)
    X, Y = np.meshgrid(xx, yy)
    r = np.sqrt(X*X + Y*Y)
    radial = np.clip(1.0 - r*0.9, 0.0, 1.0)  # centro mais alto, bordas mais baixas (continente)
    elev = 0.75*base + 0.25*radial
    return normalize01(elev)

def generate_moisture(shape):
    return fbm(shape, octaves=5, lacunarity=2.0, gain=0.5, base_cell=300, rng=np.random)

def generate_temperature(shape):
    h, w = shape
    lat = np.linspace(1.0, 0.0, h).reshape(h,1)  # topo frio
    noise = fbm(shape, octaves=4, lacunarity=2.0, gain=0.55, base_cell=260, rng=np.random)
    temp = 0.75*lat + 0.25*noise
    temp = normalize01(1.0 - temp)  # topo mais frio, base mais quente
    return temp

def classify_relief(elev):
    relief = np.zeros_like(elev, dtype=np.uint8)
    relief[elev < SEA_LEVEL] = 0
    relief[(elev >= SEA_LEVEL) & (elev < MOUNTAIN_LEVEL)] = 1
    relief[elev >= MOUNTAIN_LEVEL] = 2
    return relief

# ===================== Morfologia booleana =====================
def dilate_bool(mask, radius=1):
    if radius <= 0: return mask.copy()
    h, w = mask.shape
    out = mask.copy()
    for dy in range(-radius, radius+1):
        for dx in range(-radius, radius+1):
            if dy == 0 and dx == 0: continue
            shifted = np.zeros_like(mask)
            y0 = max(0,  dy); y1 = min(h, h + dy)
            x0 = max(0,  dx); x1 = min(w, w + dx)
            yy0 = max(0, -dy); yy1 = yy0 + (y1 - y0)
            xx0 = max(0, -dx); xx1 = xx0 + (x1 - x0)
            if (y1-y0) > 0 and (x1-x0) > 0:
                shifted[y0:y1, x0:x1] = mask[yy0:yy1, xx0:xx1]
                out |= shifted
    return out

def erode_bool(mask, radius=1):
    if radius <= 0: return mask.copy()
    return ~dilate_bool(~mask, radius)

def close_bool(mask, radius=1):
    if radius <= 0: return mask.copy()
    return erode_bool(dilate_bool(mask, radius), radius)

def open_bool(mask, radius=1):
    if radius <= 0: return mask.copy()
    return dilate_bool(erode_bool(mask, radius), radius)

def fill_holes(mask):
    h, w = mask.shape
    outside = np.zeros_like(mask, dtype=bool)
    dq = deque()
    for x in range(w):
        if not mask[0, x]: outside[0, x] = True; dq.append((0, x))
        if not mask[h-1, x]: outside[h-1, x] = True; dq.append((h-1, x))
    for y in range(h):
        if not mask[y, 0]: outside[y, 0] = True; dq.append((y, 0))
        if not mask[y, w-1]: outside[y, w-1] = True; dq.append((y, w-1))
    while dq:
        y, x = dq.popleft()
        for ny, nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0 <= ny < h and 0 <= nx < w and not outside[ny, nx] and not mask[ny, nx]:
                outside[ny, nx] = True
                dq.append((ny, nx))
    holes = (~mask) & (~outside)
    return mask | holes

# ===================== Lagos (com LAKE_RATE * SIZE_MULT["LAKE"]) =====================
def place_lakes(elev, moisture):
    rate = float(np.clip(LAKE_RATE * SIZE_MULT.get("LAKE", 1.0), 0.0, 1.0))
    cand = (elev >= SEA_LEVEL) & (elev <= LAKE_MAX_ELEV) & (moisture >= LAKE_MOISTURE_MIN)
    if rate <= 0.0:
        lakes = np.zeros_like(elev, dtype=bool)
    elif rate >= 1.0:
        lakes = cand.copy()
    else:
        rnd = np.random.rand(*elev.shape)
        lakes = cand & (rnd < rate)
    if LAKE_SMOOTH_RADIUS > 0:
        lakes = close_bool(lakes, LAKE_SMOOTH_RADIUS)
        lakes = open_bool(lakes, 1)
    return lakes

# ===================== Biomas comuns =====================
def assign_biomes_base(elev, lakes, temp, moist):
    h, w = elev.shape
    biomes = np.full((h, w), fill_value="PLAIN", dtype=object)
    ocean = elev < SEA_LEVEL
    biomes[ocean] = "OCEAN"
    biomes[lakes & ~ocean] = "LAKE"
    land = ~ocean & ~lakes

    mask_snow = (temp <= TEMP_SNOW_MAX) & land
    biomes[mask_snow] = "SNOW"

    mask_desert = (temp >= TEMP_HOT_MIN) & (moist <= MOIST_DESERT_MAX) & land
    biomes[mask_desert] = "DESERT"

    mask_forest = (moist >= MOIST_FOREST_MIN) & land & ~mask_desert & ~mask_snow
    biomes[mask_forest] = "FOREST"

    return biomes

# ===================== Enforce mínimos para (SNOW, DESERT, FOREST) =====================
def enforce_min_biomes(biomes, elev, temp, moist):
    out = biomes.copy()
    ocean = (out == "OCEAN")
    lakes = (out == "LAKE")
    land = ~ocean & ~lakes
    land_area = int(np.count_nonzero(land)) + 1

    targets = {
        "SNOW":   int(np.clip(MIN_FRAC_SNOW   * SIZE_MULT.get("SNOW", 1.0),   0, 0.95) * land_area),
        "DESERT": int(np.clip(MIN_FRAC_DESERT * SIZE_MULT.get("DESERT", 1.0), 0, 0.95) * land_area),
        "FOREST": int(np.clip(MIN_FRAC_FOREST * SIZE_MULT.get("FOREST", 1.0), 0, 0.95) * land_area),
    }

    def expand_into_plain(name, base_cond, score, need):
        nonlocal out
        if need <= 0: return 0
        plain = (out == "PLAIN") & land
        cand = plain & base_cond
        if not np.any(cand):
            return 0
        sc = score.copy()
        sc[~cand] = -1e9
        # pega os top-N
        take = min(need, int(np.count_nonzero(cand)))
        if take <= 0: return 0
        flat_idx = np.argpartition(sc.ravel(), -take)[-take:]
        yy, xx = np.unravel_index(flat_idx, sc.shape)
        sel = cand[yy, xx]
        out[yy[sel], xx[sel]] = name
        return int(sel.sum())

    counts = {k: int(np.count_nonzero(out == k)) for k in targets}
    for biome_name in ["SNOW", "DESERT", "FOREST"]:
        need = targets[biome_name] - counts[biome_name]
        if need <= 0:
            continue
        if biome_name == "SNOW":
            base = (temp <= (TEMP_SNOW_MAX + 0.08))
            score = (TEMP_SNOW_MAX + 0.08 - temp)
        elif biome_name == "DESERT":
            base = (temp >= (TEMP_HOT_MIN - 0.08)) & (moist <= (MOIST_DESERT_MAX + 0.08))
            score = (temp - (moist*0.5))
        else:  # FOREST
            base = (moist >= (MOIST_FOREST_MIN - 0.08))
            score = moist
        need -= expand_into_plain(biome_name, base, score, need)
        if need > 0:
            if biome_name == "SNOW":
                base = (temp <= (TEMP_SNOW_MAX + 0.16))
                score = (TEMP_SNOW_MAX + 0.16 - temp)
            elif biome_name == "DESERT":
                base = (temp >= (TEMP_HOT_MIN - 0.16)) & (moist <= (MOIST_DESERT_MAX + 0.16))
                score = (temp - (moist*0.4))
            else:
                base = (moist >= (MOIST_FOREST_MIN - 0.16))
                score = moist
            expand_into_plain(biome_name, base, score, need)

    return out

# ===================== Limpeza de “manchinhas” (snow/desert) =====================
def prune_small_patches(biomes):
    """
    Remove componentes muito pequenos de SNOW e DESERT.
    Substitui pelo bioma vizinho majoritário (ou PLAIN).
    """
    h, w = biomes.shape

    def process(target_name, min_size):
        visited = np.zeros((h, w), dtype=bool)
        mask = (biomes == target_name)
        for y in range(h):
            for x in range(w):
                if not mask[y, x] or visited[y, x]:
                    continue
                # BFS componente
                q = deque([(y, x)])
                comp = []
                visited[y, x] = True
                border_neighbors = []
                while q:
                    cy, cx = q.popleft()
                    comp.append((cy, cx))
                    for dy in (-1,0,1):
                        for dx in (-1,0,1):
                            if dy == 0 and dx == 0: continue
                            ny, nx = cy+dy, cx+dx
                            if 0 <= ny < h and 0 <= nx < w:
                                if biomes[ny, nx] != target_name:
                                    border_neighbors.append(biomes[ny, nx])
                                elif not visited[ny, nx]:
                                    visited[ny, nx] = True
                                    q.append((ny, nx))
                if len(comp) < min_size:
                    # escolhe vizinho majoritário (evitar OCEAN/LAKE se possível)
                    counts = defaultdict(int)
                    for n in border_neighbors:
                        counts[n] += 1
                    # preferências
                    avoid = {"OCEAN", "LAKE", target_name}
                    best = None
                    bestc = -1
                    for k, v in counts.items():
                        if k in avoid: continue
                        if v > bestc:
                            best, bestc = k, v
                    if best is None:
                        best = "PLAIN"
                    for (cy, cx) in comp:
                        biomes[cy, cx] = best

    if MIN_PATCH_SIZE_SNOW > 0:
        process("SNOW", MIN_PATCH_SIZE_SNOW)
    if MIN_PATCH_SIZE_DESERT > 0:
        process("DESERT", MIN_PATCH_SIZE_DESERT)
    return biomes

# ===================== Especiais (1 cada, sólidos) =====================
def neighbors8(y, x, h, w):
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if dy==0 and dx==0: continue
            ny, nx = y+dy, x+dx
            if 0 <= ny < h and 0 <= nx < w:
                yield ny, nx

def grow_blob_one_component(candidate_mask, target_area, rng, organic_field, avoid_mask=None, max_iter=10_000):
    h, w = candidate_mask.shape
    cand = candidate_mask.copy()
    if avoid_mask is not None:
        cand &= ~avoid_mask

    ys, xs = np.where(cand)
    if len(ys) == 0:
        return np.zeros_like(candidate_mask, dtype=bool)

    # ✅ escolher (y,x) com o MESMO índice ponderado
    vals = organic_field[ys, xs]
    probs = vals + 1e-6
    probs /= probs.sum()
    idx = rng.choice(len(ys), p=probs)
    sy, sx = int(ys[idx]), int(xs[idx])

    region = np.zeros_like(cand, dtype=bool)
    region[sy, sx] = True
    frontier = [(sy, sx)]
    visited = set([(sy, sx)])
    steps = 0

    while frontier and region.sum() < target_area and steps < max_iter:
        steps += 1
        if len(frontier) > 8:
            sample = rng.choice(len(frontier), size=min(8, len(frontier)), replace=False)
            pick = max(sample, key=lambda i: organic_field[frontier[i]])
        else:
            pick = rng.integers(0, len(frontier))
        y, x = frontier.pop(pick)

        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dy == 0 and dx == 0: 
                    continue
                ny, nx = y+dy, x+dx
                if 0 <= ny < h and 0 <= nx < w:
                    if (ny, nx) in visited:
                        continue
                    visited.add((ny, nx))
                    if not cand[ny, nx]:
                        continue
                    p = 0.55 + 0.4 * organic_field[ny, nx]
                    if rng.random() < p:
                        region[ny, nx] = True
                        frontier.append((ny, nx))
        random.shuffle(frontier)

    # solidificação
    if SPECIAL_SOLID_CLOSE_RADIUS > 0:
        region = close_bool(region, SPECIAL_SOLID_CLOSE_RADIUS)
    region = fill_holes(region)
    if SPECIAL_SOLID_OPEN_RADIUS > 0:
        region = open_bool(region, SPECIAL_SOLID_OPEN_RADIUS)
    return region

def place_special_biomes(elev, relief, moist, biomes):
    """
    VULCANO, PANTANO, TERRA_MAGICA: 1 blob sólido de cada, garantidos.
    Mantém seus critérios + fallbacks; se ainda falhar, força o spawn em terra.
    """
    h, w = elev.shape
    rng = np.random.default_rng(SEED + 1337)
    out = biomes.copy()

    ocean = elev < SEA_LEVEL
    land = ~ocean & (biomes != "LAKE")
    organic = fbm((h, w), octaves=5, lacunarity=2.0, gain=0.5, base_cell=180, rng=np.random)
    land_area = int(np.count_nonzero(land)) + 1
    far_from_ocean = ~dilate_bool(ocean, radius=VOLCAN_MIN_COAST_DIST)
    used = np.zeros((h, w), dtype=bool)

    def force_special(name, target_area):
        """Se ainda não nasceu, força nascer onde couber."""
        nonlocal out, used
        avail = land & (~used)
        avail_count = int(np.count_nonzero(avail))
        if avail_count == 0:
            # último recurso: permite sobrepor (mantemos a estética orgânica)
            avail = land.copy()
            avail_count = int(np.count_nonzero(avail))
            if avail_count == 0:
                return  # sem terra nenhuma, nada a fazer
        take = max(1, min(target_area, avail_count))
        blob = grow_blob_one_component(avail, take, rng, organic, avoid_mask=None)
        out[blob] = name
        used |= blob

    # ---------- VULCANO ----------
    volcan_target = max(1, int(SPECIAL_RATES_VOLCAN * SIZE_MULT.get("VULCANO", 1.0) * land_area))
    volcano_cand = (relief == 2) & land & far_from_ocean & (~used)
    volcano_blob = grow_blob_one_component(volcano_cand, volcan_target, rng, organic, avoid_mask=used)
    if volcano_blob.any():
        out[volcano_blob] = "VULCANO"; used |= volcano_blob
    else:
        # relaxa: qualquer montanha em terra; depois força
        cand_relax = (relief == 2) & land & (~used)
        volcano_blob = grow_blob_one_component(cand_relax, volcan_target, rng, organic, avoid_mask=used)
        if volcano_blob.any():
            out[volcano_blob] = "VULCANO"; used |= volcano_blob
        else:
            force_special("VULCANO", volcan_target)

    # ---------- PANTANO ----------
    swamp_target = max(1, int(SPECIAL_RATES_SWAMP * SIZE_MULT.get("PANTANO", 1.0) * land_area))
    lakes_mask = (out == "LAKE")
    near_lake = dilate_bool(lakes_mask, radius=SWAMP_NEAR_LAKE_RADIUS)
    swamp_cand = land & near_lake & (elev <= SWAMP_LOWLAND_MAX) & (moist >= SWAMP_MOIST_MIN) & (~used)
    swamp_blob = grow_blob_one_component(swamp_cand, swamp_target, rng, organic, avoid_mask=used)

    if not swamp_blob.any():
        near_coast = dilate_bool(ocean, radius=SWAMP_NEAR_COAST_RADIUS) & land
        swamp_cand2 = near_coast & (elev <= SWAMP_LOWLAND_MAX) & (moist >= SWAMP_MOIST_MIN) & (~used)
        swamp_blob = grow_blob_one_component(swamp_cand2, swamp_target, rng, organic, avoid_mask=used)

    if not swamp_blob.any():
        swamp_cand3 = land & (elev <= SWAMP_LOWLAND_MAX) & (moist >= (SWAMP_MOIST_MIN + 0.05)) & (~used)
        swamp_blob = grow_blob_one_component(swamp_cand3, swamp_target, rng, organic, avoid_mask=used)

    if not swamp_blob.any():
        swamp_cand4 = land & (moist >= (SWAMP_MOIST_MIN + 0.02)) & (~used)
        swamp_blob = grow_blob_one_component(swamp_cand4, swamp_target, rng, organic, avoid_mask=used)

    if swamp_blob.any():
        out[swamp_blob] = "PANTANO"; used |= swamp_blob
    else:
        # força pântano (qualquer terra), garantindo existência
        force_special("PANTANO", swamp_target)

    # ---------- TERRA MÁGICA ----------
    magic_target = max(1, int(SPECIAL_RATES_MAGIC * SIZE_MULT.get("TERRA_MAGICA", 1.0) * land_area))
    not_extremes = land & (out != "PANTANO") & (out != "VULCANO")
    magic_cand = not_extremes & (moist >= 0.58) & (elev >= SEA_LEVEL + 0.02) & (elev <= MOUNTAIN_LEVEL) & (~used)
    magic_blob = grow_blob_one_component(magic_cand, magic_target, rng, organic, avoid_mask=used)
    if magic_blob.any():
        out[magic_blob] = "TERRA_MAGICA"; used |= magic_blob
    else:
        # relaxa: qualquer terra úmida; depois força
        magic_relax = land & (moist >= 0.55) & (~used)
        magic_blob = grow_blob_one_component(magic_relax, magic_target, rng, organic, avoid_mask=used)
        if magic_blob.any():
            out[magic_blob] = "TERRA_MAGICA"; used |= magic_blob
        else:
            force_special("TERRA_MAGICA", magic_target)

    # sanity check final (sempre presentes)
    for name, target in [
        ("VULCANO", volcan_target),
        ("PANTANO", swamp_target),
        ("TERRA_MAGICA", magic_target),
    ]:
        if not np.any(out == name):
            force_special(name, target)

    return out

# ===================== Grade / Render =====================
def make_block_grid(biomes):
    return biomes.copy()

def render_map(biomes, out_path="mapa.png"):
    h, w = biomes.shape
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for name, rgb in COLORS.items():
        mask = (biomes == name)
        img[mask] = rgb
    Image.fromarray(img, mode="RGB").save(out_path)
    return img

def save_debug_grids(elev, relief, temp, moist, prefix="debug_"):
    def to_img(a):
        a = normalize01(a) * 255
        return Image.fromarray(a.astype(np.uint8), mode="L")
    to_img(elev).save(prefix + "elevation.png")
    to_img(temp).save(prefix + "temperature.png")
    to_img(moist).save(prefix + "moisture.png")
    Image.fromarray((relief * 127).astype(np.uint8)).save(prefix + "relief.png")

def print_biome_percentages(biomes):
    """Imprime a porcentagem de cada bioma no mapa inteiro (W*H)."""
    total = biomes.size
    # conta só o que aparece (>0), na ordem dos COLORS
    counts = []
    for name in COLORS.keys():
        cnt = int(np.count_nonzero(biomes == name))
        if cnt > 0:
            counts.append((name, cnt))
    # ordena por maior área
    counts.sort(key=lambda x: x[1], reverse=True)

    print(f"\n=== Distribuição de biomas (SEED={SEED}) ===")
    for name, cnt in counts:
        pct = 100.0 * cnt / total
        print(f"{name:<12}: {pct:6.2f}%  ({cnt}/{total})")

# ===================== Pipeline =====================
def main():
    print("começou")
    shape = (H, W)
    elev = generate_elevation(shape)
    moist = generate_moisture(shape)
    temp = generate_temperature(shape)

    relief = classify_relief(elev)
    lakes = place_lakes(elev, moist)  # controlado por LAKE_RATE * SIZE_MULT["LAKE"]

    # Biomas "base" (comuns)
    biomes = assign_biomes_base(elev, lakes, temp, moist)

    # Garante mínimos de neve/deserto/floresta (ajustáveis + multiplicadores)
    biomes = enforce_min_biomes(biomes, elev, temp, moist)

    # Remove manchinhas muito pequenas de neve/deserto
    biomes = prune_small_patches(biomes)

    # Biomas especiais (1 mancha sólida de cada)
    biomes = place_special_biomes(elev, relief, moist, biomes)

    blocks = make_block_grid(biomes)
    render_map(biomes, out_path="mapa_1200x1200.png")

    # Grades de exemplo
    relief_grid = relief
    biome_grid = biomes
    block_grid = blocks

    print_biome_percentages(biomes)

    # np.save("grid_relief.npy", relief_grid)
    # np.save("grid_biomes.npy", biome_grid)
    # np.save("grid_blocks.npy", block_grid)

main()