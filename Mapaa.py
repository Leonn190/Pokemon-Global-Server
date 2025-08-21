# -*- coding: utf-8 -*-
# Gerador de mapa 2D em grade (tabletop)
# Dependência: numpy  (pip install numpy)

import numpy as np
from collections import deque

# ===== Mapeamento numérico =====
# Biomas (matriz "biomas"):
# 0=oceano, 1=planície, 2=floresta, 3=neve, 4=deserto
# Blocos (matriz "blocos"):
# 0=água, 1=água rasa, 2=mato, 3=matofloresta, 4=neve, 5=deserto, 6=praia

def _smooth9(a):
    """Filtro média 3x3 via np.roll (com wrap/toroidal). Rápido e sem loops Python."""
    return (
        a +
        np.roll(a, 1, 0) + np.roll(a, -1, 0) +
        np.roll(a, 1, 1) + np.roll(a, -1, 1) +
        np.roll(np.roll(a, 1, 0),  1, 1) +
        np.roll(np.roll(a, 1, 0), -1, 1) +
        np.roll(np.roll(a,-1, 0),  1, 1) +
        np.roll(np.roll(a,-1, 0), -1, 1)
    ) / 9.0

def _fractal_noise(h, w, scales=(64, 32, 16, 8), weight_decay=0.5, seed=None, smooth_passes=2):
    """Ruído fractal simples (octaves) sem libs externas."""
    rng = np.random.default_rng(seed)
    noise = np.zeros((h, w), dtype=np.float32)
    weight = 1.0
    for s in scales:
        gh, gw = h // s + 2, w // s + 2
        base = rng.random((gh, gw), dtype=np.float32)
        up = np.kron(base, np.ones((s, s), dtype=np.float32))[:h, :w]
        for _ in range(smooth_passes):
            up = _smooth9(up)
        noise += weight * up
        weight *= weight_decay
    mn, mx = noise.min(), noise.max()
    if mx - mn > 1e-6:
        noise = (noise - mn) / (mx - mn)
    else:
        noise.fill(0.5)
    return noise

def _neighbor_sum(mask_bool):
    """Conta vizinhos 8-conectados (para máscara booleana)."""
    m = mask_bool.astype(np.int16)
    return (
        np.roll(m, 1, 0) + np.roll(m, -1, 0) +
        np.roll(m, 1, 1) + np.roll(m, -1, 1) +
        np.roll(np.roll(m, 1, 0),  1, 1) +
        np.roll(np.roll(m, 1, 0), -1, 1) +
        np.roll(np.roll(m,-1, 0),  1, 1) +
        np.roll(np.roll(m,-1, 0), -1, 1)
    )

def _majority_filter(labels, num_classes, passes=1):
    """Filtro de maioria 3x3 (suaviza fronteiras e reduz manchas)."""
    out = labels.copy()
    for _ in range(passes):
        counts = []
        for k in range(num_classes):
            mk = (out == k)
            cnt = _neighbor_sum(mk) + mk.astype(np.int16)  # inclui o próprio centro
            counts.append(cnt)
        counts = np.stack(counts, axis=-1)  # H x W x K
        out = counts.argmax(axis=-1).astype(labels.dtype)
    return out

def _merge_small_regions(arr, label, min_size, fill_label=None):
    """Remove/regrede regiões pequenas (8-conectadas) de um rótulo 'label'."""
    h, w = arr.shape
    visited = np.zeros((h, w), dtype=bool)
    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    for y in range(h):
        for x in range(w):
            if not visited[y, x] and arr[y, x] == label:
                q = deque([(y, x)])
                visited[y, x] = True
                comp = [(y, x)]
                border = []
                while q:
                    cy, cx = q.popleft()
                    for dy, dx in dirs:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            if arr[ny, nx] == label and not visited[ny, nx]:
                                visited[ny, nx] = True
                                q.append((ny, nx))
                                comp.append((ny, nx))
                            elif arr[ny, nx] != label:
                                border.append(arr[ny, nx])
                if len(comp) < min_size:
                    if fill_label is None:
                        if border:
                            vals, cnts = np.unique(np.array(border), return_counts=True)
                            fill = vals[cnts.argmax()]
                        else:
                            fill = 1  # planície como fallback
                    else:
                        fill = fill_label
                    for (cy, cx) in comp:
                        arr[cy, cx] = fill

def gerar_mapa(W=200, H=200, seed=None, cfg=None):
    """
    Retorna:
      biomas(HxW): 0 oceano, 1 planície, 2 floresta, 3 neve, 4 deserto
      blocos(HxW): 0 água, 1 água rasa, 2 mato, 3 matofloresta, 4 neve, 5 deserto, 6 praia
      debug: dict com 'relevo','umidade','temperatura'
    """
    # ----- Config padrão (pode passar overrides via cfg) -----
    C = dict(
        sea_level=0.50,
        temp_noise_amp=0.25,
        temp_lat_bias=1.00,
        humid_threshold_forest=0.55,

        # === NOVO: parâmetros “espelhados” de faixas polares ===
        band_power=1.6,           # força do “puxão” para os polos (↑ => mais faixa coesa)
        temp_power=1.0,           # peso da componente de temperatura nos scores
        dry_power=1.0,            # peso da secura no deserto
        band_noise_amp=0.12,      # ruído leve para quebrar linhas retas
        temp_mid=0.50,            # meio termo de temperatura para normalização
        desert_score_min=0.26,    # limiar do score para virar deserto
        snow_score_min=0.30,      # limiar do score para virar neve

        # limites de latitude onde pode haver cada bioma
        allow_desert_south_of=0.55,  # só abaixo disso (sul)
        allow_snow_north_of=0.45,    # só acima disso (norte)

        # filtros/limpeza
        smooth_passes_biome=1,
        min_region_desert_ratio=0.0008,
        min_region_snow_ratio=0.0008,

        beach_on_any_coast=False,
        noise_scales=(64, 32, 16, 8),
        seed_offset_temp=113,
        seed_offset_humid=271,
    )
    if cfg:
        C.update(cfg)

    BI_OCEANO, BI_PLANICIE, BI_FLORESTA, BI_NEVE, BI_DESERTO = 0, 1, 2, 3, 4
    BL_AGUA, BL_AGUARASA, BL_MATO, BL_MATOFLORESTA, BL_NEVE, BL_DESERTO, BL_PRAIA = 0, 1, 2, 3, 4, 5, 6

    # ----- Ruídos base -----
    relevo   = _fractal_noise(H, W, scales=C['noise_scales'], seed=seed, smooth_passes=2)
    umidade  = _fractal_noise(H, W, scales=C['noise_scales'],
                              seed=(None if seed is None else seed + C['seed_offset_humid']), smooth_passes=2)
    t_noise  = _fractal_noise(H, W, scales=C['noise_scales'],
                              seed=(None if seed is None else seed + C['seed_offset_temp']),  smooth_passes=1)

    # Gradiente latitudinal e temperatura
    lat = np.linspace(0, 1, H, dtype=np.float32).reshape(H, 1)  # 0=norte/topo, 1=sul/base
    temperatura = np.clip(C['temp_lat_bias'] * lat + C['temp_noise_amp'] * (t_noise - 0.5), 0, 1)

    # ----- Máscaras de terreno -----
    ocean = relevo < C['sea_level']
    land  = ~ocean

    # ----- Scores “espelhados” (compactação ao norte/sul) -----
    # puxões polares normalizados
    south_pull = np.clip((lat - C['allow_desert_south_of']) / (1 - C['allow_desert_south_of'] + 1e-6), 0, 1)
    north_pull = np.clip((C['allow_snow_north_of'] - lat) / (C['allow_snow_north_of'] + 1e-6), 0, 1)

    south_pull = south_pull ** C['band_power']
    north_pull = north_pull ** C['band_power']

    # componentes climáticas normalizadas
    temp_mid = C['temp_mid']
    temp_hot  = np.clip((temperatura - temp_mid) / (1 - temp_mid + 1e-6), 0, 1)  # 0..1 quanto mais quente
    temp_cold = np.clip((temp_mid - temperatura) / (temp_mid + 1e-6),       0, 1)  # 0..1 quanto mais frio
    dryness   = np.clip(1.0 - umidade, 0, 1)

    # ruído leve para orgânico
    noise = C['band_noise_amp'] * (t_noise - 0.5)

    # scores finais
    desert_score = (south_pull * (temp_hot ** C['temp_power']) * (dryness ** C['dry_power'])) + noise
    snow_score   = (north_pull * (temp_cold ** C['temp_power'])) + (0.6 * noise)  # um pouco menos ruído na neve

    # ----- Classificação de biomas (ordem: oceano > neve > deserto > floresta > planície) -----
    biomas = np.full((H, W), BI_PLANICIE, dtype=np.uint8)
    biomas[ocean] = BI_OCEANO

    snow_mask   = (land & (snow_score   >= C['snow_score_min']))
    desert_mask = (land & (desert_score >= C['desert_score_min']))

    # floresta no que sobrar, por umidade
    forest_mask = (land & ~snow_mask & ~desert_mask & (umidade >= C['humid_threshold_forest']))

    biomas[snow_mask]   = BI_NEVE
    biomas[desert_mask] = BI_DESERTO
    biomas[forest_mask] = BI_FLORESTA

    # Suaviza e remove ilhas pequenas (reduz salpicos)
    if C['smooth_passes_biome'] > 0:
        biomas = _majority_filter(biomas, num_classes=5, passes=C['smooth_passes_biome'])

    total = H * W
    min_desert = max(50, int(C['min_region_desert_ratio'] * total))
    min_snow   = max(50, int(C['min_region_snow_ratio']   * total))
    _merge_small_regions(biomas, BI_DESERTO, min_desert, fill_label=BI_PLANICIE)
    _merge_small_regions(biomas, BI_NEVE,   min_snow,   fill_label=BI_PLANICIE)

    # ----- Blocos -----
    blocos = np.zeros((H, W), dtype=np.uint8)
    blocos[ocean] = BL_AGUA

    # água rasa (oceano tocando terra)
    land_mask   = (biomas != BI_OCEANO)
    neigh_land  = _neighbor_sum(land_mask) > 0
    shallow     = ocean & neigh_land
    blocos[shallow] = BL_AGUARASA

    # praia (terra tocando oceano); opcionalmente evita praia na neve
    neigh_ocean = _neighbor_sum(ocean) > 0
    coast_land  = land_mask & neigh_ocean
    if not C['beach_on_any_coast']:
        coast_land = coast_land & (biomas != BI_NEVE)
    blocos[coast_land] = BL_PRAIA

    # demais blocos por bioma
    BI_OCEANO, BI_PLANICIE, BI_FLORESTA, BI_NEVE, BI_DESERTO = 0, 1, 2, 3, 4
    blocos[(biomas == BI_PLANICIE) & ~coast_land] = BL_MATO
    blocos[(biomas == BI_FLORESTA) & ~coast_land] = BL_MATOFLORESTA
    blocos[(biomas == BI_NEVE)     & ~coast_land] = BL_NEVE
    blocos[(biomas == BI_DESERTO)  & ~coast_land] = BL_DESERTO

    debug = dict(relevo=relevo, umidade=umidade, temperatura=temperatura,
                 snow_score=snow_score, desert_score=desert_score)
    return biomas, blocos, debug

# +++ ADIÇÕES +++
# Dependência extra: Pillow  (pip install pillow)
from PIL import Image

# Paleta de cores para os BLOCOS (índices 0..6)
# 0=água, 1=água rasa, 2=mato, 3=matofloresta, 4=neve, 5=deserto, 6=praia
CORES_BLOCOS = np.array([
    [  0,  80, 200],  # água (azul)
    [ 90, 170, 255],  # água rasa (azul claro)
    [ 50, 160,  60],  # mato (verde)
    [ 20, 110,  35],  # matofloresta (verde escuro)
    [235, 245, 255],  # neve (quase branco)
    [235, 215, 130],  # deserto (areia)
    [245, 230, 150],  # praia (areia clara)
], dtype=np.uint8)

def grid_blocos_para_imagem(blocos, scale=1, save_path=None, palette=None):
    """
    Converte a grid 'blocos' (H x W, uint8) em imagem RGB.
    - Cada pixel representa 1 bloco.
    - 'scale' aplica zoom inteiro usando vizinho-mais-próximo (mantém pixel art).
    - Se 'save_path' for informado, salva como PNG.
    - 'palette' pode ser um array Nx3 (RGB) para sobrescrever as cores.
    Retorna: PIL.Image
    """
    if palette is None:
        palette = CORES_BLOCOS
    palette = np.asarray(palette, dtype=np.uint8)

    if blocos.min() < 0 or blocos.max() >= len(palette):
        raise ValueError(
            f"Valores em 'blocos' fora da paleta: min={int(blocos.min())} "
            f"max={int(blocos.max())} (paleta tem {len(palette)} cores)"
        )

    # Mapeia cada índice de bloco para um RGB
    img_rgb = palette[blocos]  # shape (H, W, 3), dtype=uint8
    img = Image.fromarray(img_rgb, mode='RGB')

    # Zoom opcional
    if isinstance(scale, int) and scale > 1:
        img = img.resize((img.width * scale, img.height * scale), resample=Image.NEAREST)

    if save_path:
        img.save(save_path, format='PNG')
    return img
# +++ FIM DAS ADIÇÕES +++

# ---------- Exemplo de uso ----------
if __name__ == "__main__":
    biomas, blocos, dbg = gerar_mapa(W=1000, H=1000, seed=25)
    # Cria uma prévia 4x maior e salva
    img = grid_blocos_para_imagem(blocos, scale=2, save_path="mapa_blocos.png")
    print("Imagem salva em mapa_blocos.png")
