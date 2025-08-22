# -*- coding: utf-8 -*-
# Gerador de mapa 2D em grade (tabletop)
# Dependências: numpy (pip install numpy), Pillow para salvar imagem (pip install pillow)

import random
import numpy as np
from collections import deque
from PIL import Image

# ===== Mapeamento numérico =====
# Biomas (matriz "biomas"):
# 0=oceano, 1=planície, 2=floresta, 3=neve, 4=deserto,
# 5=pântano (único), 6=mágico (único), 7=vulcânico (único)
BI_OCEANO, BI_PLANICIE, BI_FLORESTA, BI_NEVE, BI_DESERTO, BI_PANTANO, BI_MAGICO, BI_VULCANICO = 0,1,2,3,4,5,6,7

# Blocos (matriz "blocos"):
# 0=água, 1=água rasa, 2=mato, 3=matofloresta, 4=neve, 5=deserto, 6=praia,
# 7=terra morta (pântano), 8=terra mágica, 9=pedra vulcânica
BL_AGUA, BL_AGUARASA, BL_MATO, BL_MATOFLORESTA, BL_NEVE, BL_DESERTO, BL_PRAIA, BL_TERRAMORTA, BL_TERRAMAGICA, BL_PEDRAVULCANICA = 0,1,2,3,4,5,6,7,8,9

# ===== Paleta de cores para os BLOCOS (índices 0..9) =====
CORES_BLOCOS = np.array([
    [  0,  80, 200],  # 0 água
    [ 90, 170, 255],  # 1 água rasa
    [ 50, 160,  60],  # 2 mato
    [ 20, 110,  35],  # 3 matofloresta
    [235, 245, 255],  # 4 neve
    [235, 215, 130],  # 5 deserto
    [245, 230, 150],  # 6 praia
    [130, 130, 130],  # 7 terra morta (pântano)
    [205, 170, 255],  # 8 terra mágica
    [120,  20,  20],  # 9 pedra vulcânica
], dtype=np.uint8)

# ===== CONFIGURAÇÃO PADRÃO (fora das funções) =====
CFG_PADRAO = dict(
    # terreno/clima
    sea_level=0.48,
    temp_noise_amp=0.25,
    temp_lat_bias=1.00,
    humid_threshold_forest=0.55,

    # FAIXAS (somam ~1.0)
    band_top_pct=0.29,  # faixa fria (norte) onde neve pode existir
    band_mid_pct=0.36,  # faixa central
    band_bottom_pct=0.35,  # faixa quente (sul) onde deserto pode existir

    # parâmetros de transição (iguais para neve e deserto)
    band_power=1.7,
    temp_power=1.0,
    band_noise_amp=0.12,
    temp_mid=0.50,
    snow_score_min=0.30,
    desert_score_min=0.30,  # igual à neve; pode ajustar se quiser

    # limpeza
    smooth_passes_biome=1,
    min_region_desert_ratio=0.0009,
    min_region_snow_ratio=0.0009,

    # praia
    beach_on_any_coast=False,

    # ruído
    noise_scales=(64, 32, 16, 8),
    seed_offset_temp=113, seed_offset_humid=271,

    # === Biomas ÚNICOS (na faixa central) ===
    unique_enable=True,
    unique_min_cells=260,

    # tamanho por RATIO (fallback para todos)
    unique_area_ratio=0.006,  # ~0.25% do mapa

    # override por tipo (ratio) – opcionais
    # unique_area_ratio_swamp=..., unique_area_ratio_magic=..., unique_area_ratio_volcanic=...,

    # tamanho por CÉLULAS (tem prioridade sobre ratio) – opcionais
    unique_size_cells_swamp=None,
    unique_size_cells_magic=None,
    unique_size_cells_volcanic=None,
)

# ----------------- FUNÇÕES UTILITÁRIAS (renomeadas) -----------------

def _suavizar9(a):
    """Filtro média 3x3 via np.roll (wrap/toroidal)."""
    return (
        a +
        np.roll(a, 1, 0) + np.roll(a, -1, 0) +
        np.roll(a, 1, 1) + np.roll(a, -1, 1) +
        np.roll(np.roll(a, 1, 0),  1, 1) +
        np.roll(np.roll(a, 1, 0), -1, 1) +
        np.roll(np.roll(a,-1, 0),  1, 1) +
        np.roll(np.roll(a,-1, 0), -1, 1)
    ) / 9.0

def _ruido_fractal(h, w, escalas=(64, 32, 16, 8), decaimento=0.5, seed=None, suavizagens=2):
    """Ruído fractal (octaves) sem libs externas; usa np.kron + suavização."""
    rng = np.random.default_rng(seed)
    ruido = np.zeros((h, w), dtype=np.float32)
    peso = 1.0
    for s in escalas:
        gh, gw = h // s + 2, w // s + 2
        base = rng.random((gh, gw), dtype=np.float32)
        up = np.kron(base, np.ones((s, s), dtype=np.float32))[:h, :w]
        for _ in range(suavizagens):
            up = _suavizar9(up)
        ruido += peso * up
        peso *= decaimento
    mn, mx = ruido.min(), ruido.max()
    if mx - mn > 1e-6:
        ruido = (ruido - mn) / (mx - mn)
    else:
        ruido.fill(0.5)
    return ruido

def _soma_vizinhos(mask_bool):
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

def _filtro_maioria(rotulos, num_classes, passes=1):
    """Filtro de maioria 3x3 (suaviza fronteiras e reduz manchas)."""
    out = rotulos.copy()
    for _ in range(passes):
        contagens = []
        for k in range(num_classes):
            mk = (out == k)
            cnt = _soma_vizinhos(mk) + mk.astype(np.int16)  # inclui o centro
            contagens.append(cnt)
        contagens = np.stack(contagens, axis=-1)  # H x W x K
        out = contagens.argmax(axis=-1).astype(rotulos.dtype)
    return out

def _mesclar_regioes_pequenas(arr, label, tamanho_min, fill_label=None):
    """Remove/regrede regiões pequenas (8-conectadas) de um rótulo 'label'."""
    h, w = arr.shape
    visitado = np.zeros((h, w), dtype=bool)
    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    for y in range(h):
        for x in range(w):
            if not visitado[y, x] and arr[y, x] == label:
                q = deque([(y, x)])
                visitado[y, x] = True
                comp = [(y, x)]
                borda = []
                while q:
                    cy, cx = q.popleft()
                    for dy, dx in dirs:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            if arr[ny, nx] == label and not visitado[ny, nx]:
                                visitado[ny, nx] = True
                                q.append((ny, nx))
                                comp.append((ny, nx))
                            elif arr[ny, nx] != label:
                                borda.append(arr[ny, nx])
                if len(comp) < tamanho_min:
                    if fill_label is None:
                        if borda:
                            vals, cnts = np.unique(np.array(borda), return_counts=True)
                            fill = vals[cnts.argmax()]
                        else:
                            fill = BI_PLANICIE
                    else:
                        fill = fill_label
                    for (cy, cx) in comp:
                        arr[cy, cx] = fill

def _esculpir_bioma_unico(biomas, blocos, mascara_permitida, tamanho_alvo, rotulo_bioma, rotulo_bloco, rng):
    """Cria UMA região conectada (BFS) com ~tamanho_alvo células dentro de mascara_permitida."""
    H, W = biomas.shape
    candidatos = np.argwhere(mascara_permitida)
    if candidatos.size == 0:
        return False
    sy, sx = candidatos[rng.integers(0, len(candidatos))]

    q = deque([(sy, sx)])
    visit = np.zeros((H, W), dtype=bool)
    visit[sy, sx] = True
    cont = 0

    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    while q and cont < tamanho_alvo:
        y, x = q.popleft()
        if not mascara_permitida[y, x]:
            continue
        biomas[y, x] = rotulo_bioma
        blocos[y, x] = rotulo_bloco
        cont += 1

        rng.shuffle(dirs)
        for dy, dx in dirs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and not visit[ny, nx]:
                visit[ny, nx] = True
                if mascara_permitida[ny, nx]:
                    q.append((ny, nx))
    return cont > 0

def _tamanho_bioma_unico(total_celulas, C, chave_cells, chave_ratio, ratio_default, min_cells):
    """Escolhe tamanho do bioma único (células têm prioridade sobre ratio)."""
    if C.get(chave_cells, None) is not None:
        return max(min_cells, int(C[chave_cells]))
    ratio = C.get(chave_ratio, ratio_default)
    return max(min_cells, int(ratio * total_celulas))

# ----------------- GERAÇÃO (deserto = neve, simétricos) -----------------

def gerar_mapa(W=200, H=200, seed=None, cfg=None):
    """
    Retorna:
      biomas(HxW): 0 oceano, 1 planície, 2 floresta, 3 neve, 4 deserto, 5 pântano, 6 mágico, 7 vulcânico
      blocos(HxW): 0 água, 1 água rasa, 2 mato, 3 matofloresta, 4 neve, 5 deserto, 6 praia, 7 terra morta, 8 terra mágica, 9 pedra vulcânica
      debug: dict (relevo, umidade, temperatura, score_neve, score_deserto, bands)
    """
    C = dict(CFG_PADRAO)
    if cfg:
        C.update(cfg)

    rng = np.random.default_rng(seed)

    # Faixas normalizadas (apenas definem onde cada clima pode existir)
    bt, bm, bb = C['band_top_pct'], C['band_mid_pct'], C['band_bottom_pct']
    s = max(1e-6, bt + bm + bb)
    bt, bm, bb = bt/s, bm/s, bb/s
    fim_faixa_topo    = bt            # lat <= bt  -> faixa fria (norte)
    inicio_faixa_base = 1.0 - bb      # lat >= 1-bb -> faixa quente (sul)

    # Ruídos base
    relevo   = _ruido_fractal(H, W, escalas=C['noise_scales'], seed=seed, suavizagens=2)
    umidade  = _ruido_fractal(H, W, escalas=C['noise_scales'],
                              seed=(None if seed is None else seed + C['seed_offset_humid']), suavizagens=2)
    t_ruido  = _ruido_fractal(H, W, escalas=C['noise_scales'],
                              seed=(None if seed is None else seed + C['seed_offset_temp']),  suavizagens=1)

    lat = np.linspace(0, 1, H, dtype=np.float32).reshape(H, 1)  # 0=norte/topo, 1=sul/base
    temperatura = np.clip(C['temp_lat_bias'] * lat + C['temp_noise_amp'] * (t_ruido - 0.5), 0, 1)

    # Terreno
    oceano = relevo < C['sea_level']
    terra  = ~oceano

    # blocos inicial (precisa existir antes dos únicos)
    blocos = np.zeros((H, W), dtype=np.uint8)
    blocos[oceano] = BL_AGUA

    # Scores climáticos (SIMÉTRICOS: deserto = neve)
    atracao_sul   = np.clip((lat - inicio_faixa_base) / (1 - inicio_faixa_base + 1e-6), 0, 1) ** C['band_power']
    atracao_norte = np.clip((fim_faixa_topo - lat) / (fim_faixa_topo + 1e-6),           0, 1) ** C['band_power']

    t_meio   = C['temp_mid']
    t_quente = np.clip((temperatura - t_meio) / (1 - t_meio + 1e-6), 0, 1)
    t_frio   = np.clip((t_meio - temperatura) / (t_meio + 1e-6),     0, 1)
    ruido_banda = C['band_noise_amp'] * (t_ruido - 0.5)

    score_neve    = (atracao_norte * (t_frio   ** C['temp_power'])) + (0.6 * ruido_banda)
    score_deserto = (atracao_sul   * (t_quente ** C['temp_power'])) + (0.6 * ruido_banda)

    # Faixas explícitas
    faixa_norte = (lat <= fim_faixa_topo)      # onde neve pode existir
    faixa_sul   = (lat >= inicio_faixa_base)   # onde deserto pode existir

    # Biomas base
    biomas = np.full((H, W), BI_PLANICIE, dtype=np.uint8)
    biomas[oceano] = BI_OCEANO

    mask_neve     = (terra & faixa_norte & (score_neve    >= C['snow_score_min']))
    mask_deserto  = (terra & faixa_sul   & (score_deserto >= C['desert_score_min']))
    mask_floresta = (terra & ~mask_neve & ~mask_deserto & (umidade >= C['humid_threshold_forest']))

    biomas[mask_neve]     = BI_NEVE
    biomas[mask_deserto]  = BI_DESERTO
    biomas[mask_floresta] = BI_FLORESTA

    # Suaviza & limpa só neve/deserto
    if C['smooth_passes_biome'] > 0:
        biomas = _filtro_maioria(biomas, num_classes=8, passes=C['smooth_passes_biome'])

    total = H * W
    min_deserto = max(50, int(C['min_region_desert_ratio'] * total))
    min_neve    = max(50, int(C['min_region_snow_ratio']   * total))
    _mesclar_regioes_pequenas(biomas, BI_DESERTO, min_deserto, fill_label=BI_PLANICIE)
    _mesclar_regioes_pequenas(biomas, BI_NEVE,   min_neve,    fill_label=BI_PLANICIE)

    # Biomas ÚNICOS (só na faixa central)
    if C.get('unique_enable', True):
        faixa_meio = (lat > fim_faixa_topo) & (lat < inicio_faixa_base)
        permitido_meio_terra = (faixa_meio & terra & (biomas != BI_OCEANO))

        tam_pantano = _tamanho_bioma_unico(
            total, C,
            chave_cells='unique_size_cells_swamp',
            chave_ratio='unique_area_ratio_swamp',
            ratio_default=C['unique_area_ratio'],
            min_cells=C['unique_min_cells']
        )
        tam_magico = _tamanho_bioma_unico(
            total, C,
            chave_cells='unique_size_cells_magic',
            chave_ratio='unique_area_ratio_magic',
            ratio_default=C['unique_area_ratio'],
            min_cells=C['unique_min_cells']
        )
        tam_vulcanico = _tamanho_bioma_unico(
            total, C,
            chave_cells='unique_size_cells_volcanic',
            chave_ratio='unique_area_ratio_volcanic',
            ratio_default=C['unique_area_ratio'],
            min_cells=C['unique_min_cells']
        )

        base = permitido_meio_terra & (biomas != BI_PANTANO) & (biomas != BI_MAGICO) & (biomas != BI_VULCANICO)
        base = base & ~oceano

        if base.any():
            _esculpir_bioma_unico(
                biomas, blocos,
                mascara_permitida=base & (umidade >= np.median(umidade[base])),
                tamanho_alvo=tam_pantano,
                rotulo_bioma=BI_PANTANO,
                rotulo_bloco=BL_TERRAMORTA,
                rng=rng
            )
        if base.any():
            _esculpir_bioma_unico(
                biomas, blocos,
                mascara_permitida=base,
                tamanho_alvo=tam_magico,
                rotulo_bioma=BI_MAGICO,
                rotulo_bloco=BL_TERRAMAGICA,
                rng=rng
            )
        if base.any():
            _esculpir_bioma_unico(
                biomas, blocos,
                mascara_permitida=base & (relevo >= np.median(relevo[base])),
                tamanho_alvo=tam_vulcanico,
                rotulo_bioma=BI_VULCANICO,
                rotulo_bloco=BL_PEDRAVULCANICA,
                rng=rng
            )

    # Blocos (praia/água rasa e detalhamento por bioma)
    masc_terra = (biomas != BI_OCEANO)
    viz_terra  = _soma_vizinhos(masc_terra) > 0
    raso       = oceano & viz_terra
    blocos[raso] = BL_AGUARASA

    viz_oceano  = _soma_vizinhos(oceano) > 0
    costa_terra = masc_terra & viz_oceano
    if not C['beach_on_any_coast']:
        costa_terra = costa_terra & (biomas != BI_NEVE)
    blocos[costa_terra] = BL_PRAIA

    blocos[(biomas == BI_PLANICIE) & ~costa_terra]  = BL_MATO
    blocos[(biomas == BI_FLORESTA) & ~costa_terra]  = BL_MATOFLORESTA
    blocos[(biomas == BI_NEVE)     & ~costa_terra]  = BL_NEVE
    blocos[(biomas == BI_DESERTO)  & ~costa_terra]  = BL_DESERTO
    blocos[(biomas == BI_PANTANO)  & ~costa_terra]  = BL_TERRAMORTA
    blocos[(biomas == BI_MAGICO)   & ~costa_terra]  = BL_TERRAMAGICA
    blocos[(biomas == BI_VULCANICO)& ~costa_terra]  = BL_PEDRAVULCANICA

    debug = dict(
        relevo=relevo, umidade=umidade, temperatura=temperatura,
        score_neve=score_neve, score_deserto=score_deserto,
        bands=dict(top_end=float(fim_faixa_topo), bottom_start=float(inicio_faixa_base),
                   top_pct=float(bt), mid_pct=float(bm), bottom_pct=float(bb))
    )
    return biomas, blocos, debug

# ----------------- ESCALA REAL DA GRID -----------------

def scale(biomas, blocos, debug, fator=1):
    """
    Escala as grades (biomas, blocos e todas as matrizes em 'debug') por um fator inteiro,
    usando vizinho-mais-próximo na PRÓPRIA GRID (np.repeat). Não muda as regras.
    """
    if not isinstance(fator, int) or fator < 1:
        raise ValueError("fator deve ser inteiro >= 1")
    if fator == 1:
        return biomas, blocos, debug

    biomas_s = np.repeat(np.repeat(biomas, fator, axis=0), fator, axis=1)
    blocos_s = np.repeat(np.repeat(blocos, fator, axis=0), fator, axis=1)

    debug_s = {}
    for k, v in debug.items():
        if isinstance(v, np.ndarray) and v.ndim == 2:
            debug_s[k] = np.repeat(np.repeat(v, fator, axis=0), fator, axis=1)
        else:
            debug_s[k] = v
    return biomas_s, blocos_s, debug_s

# ----------------- IMAGEM (sem scale; só colore) -----------------

def imagem_dos_blocos(blocos, palette=None, save_path=None):
    """
    Converte a grid 'blocos' (H x W, uint8) em imagem RGB, 1 pixel = 1 célula.
    (Para zoom visual, use antes a função scale(...)).
    """
    if palette is None:
        palette = CORES_BLOCOS
    palette = np.asarray(palette, dtype=np.uint8)

    if blocos.min() < 0 or blocos.max() >= len(palette):
        raise ValueError(
            f"Valores em 'blocos' fora da paleta: min={int(blocos.min())} "
            f"max={int(blocos.max())} (paleta tem {len(palette)} cores)"
        )
    img_rgb = palette[blocos]  # (H, W, 3)
    img = Image.fromarray(img_rgb, mode='RGB')
    if save_path:
        img.save(save_path, format='PNG')
    return img

CORES_BIOMAS = np.array([
    [  0,  80, 200],  # 0 oceano (azul)
    [ 50, 160,  60],  # 1 planície (verde)
    [ 20, 110,  35],  # 2 floresta (verde escuro)
    [235, 245, 255],  # 3 neve (quase branco)
    [235, 215, 130],  # 4 deserto (areia)
    [130, 130, 130],  # 5 pântano (cinza)
    [205, 170, 255],  # 6 mágico (roxo claro)
    [120,  20,  20],  # 7 vulcânico (vermelho escuro)
], dtype=np.uint8)

def imagem_dos_biomas(biomas, palette=None, save_path=None):
    """
    Gera uma imagem RGB (1 pixel = 1 célula) representando a grid de BIOMAS.
    Use 'scale(...)' antes se quiser zoom/preview maior sem alterar as regras.
    - biomas: np.ndarray (H x W) com valores 0..7 (conforme BI_*).
    - palette: array Nx3 opcional (default: CORES_BIOMAS).
    - save_path: caminho opcional para salvar PNG.
    Retorna: PIL.Image
    """
    if palette is None:
        palette = CORES_BIOMAS
    palette = np.asarray(palette, dtype=np.uint8)

    if biomas.min() < 0 or biomas.max() >= len(palette):
        raise ValueError(
            f"Valores em 'biomas' fora da paleta: min={int(biomas.min())} "
            f"max={int(biomas.max())} (paleta tem {len(palette)} cores)"
        )

    img_rgb = palette[biomas]  # (H, W, 3), uint8
    img = Image.fromarray(img_rgb, mode='RGB')
    if save_path:
        img.save(save_path, format='PNG')
    return img

# ===== Objetos: metadados (0 é reservado para 'sem objeto' na grid) =====
# IDs de objetos na GRID: 1..13
OBJ_INFO = {
    1:  {"nome":"Árvore"},
    2:  {"nome":"Palmeira"},
    3:  {"nome":"Arvore2"},
    4:  {"nome":"Pinheiro"},
    5:  {"nome":"Ouro"},
    6:  {"nome":"Diamante"},
    7:  {"nome":"Esmeralda"},
    8:  {"nome":"Rubi"},
    9:  {"nome":"Ametista"},
    10: {"nome":"Cobre"},
    11: {"nome":"Pedra"},
    12: {"nome":"Arbusto"},
    13: {"nome":"Poça de Lava"},
}

TAXA_SPAWN_BIOMA_PADRAO = {
    0: 0.00,  # oceano
    1: 0.10,  # planície
    2: 0.16,  # floresta
    3: 0.12,  # neve
    4: 0.07,  # deserto
    5: 0.12,  # pântano
    6: 0.12,  # mágico
    7: 0.10,  # vulcânico
}

OBJ_POR_BIOMA_PADRAO = {
    # 0 OCEANO: vazio
    0: {},

    # 1 PLANÍCIE
    1: {
        1:  {"rate":0.060, "dist":5},  # Árvore
        12: {"rate":0.030, "dist":3},  # Arbusto
        11: {"rate":0.040, "dist":6},  # Pedra
        10: {"rate":0.010, "dist":6},  # Cobre
        5:  {"rate":0.002, "dist":6},  # Ouro
    },

    # 2 FLORESTA
    2: {
        3:  {"rate":0.090, "dist":3},  # Arvore2
        12: {"rate":0.050, "dist":3},  # Arbusto
        11: {"rate":0.030, "dist":6},  # Pedra
        10: {"rate":0.009, "dist":6},  # Cobre
        5:  {"rate":0.0025, "dist":6},  # Ouro
    },

    # 3 NEVE
    3: {
        4:  {"rate":0.070, "dist":4},  # Pinheiro
        12: {"rate":0.032, "dist":3},  # Arbusto
        11: {"rate":0.030, "dist":4},  # Pedra
        10: {"rate":0.008, "dist":5},  # Cobre
        6:  {"rate":0.001, "dist":5},  # Diamante
    },

    # 4 DESERTO
    4: {
        2:  {"rate":0.050, "dist":6},  # Palmeira
        12: {"rate":0.010, "dist":3},  # Arbusto
        11: {"rate":0.040, "dist":4},  # Pedra
        10: {"rate":0.012, "dist":5},  # Cobre
        7:  {"rate":0.0015,"dist":5},  # Esmeralda
    },

    # 5 PÂNTANO
    5: {
        12: {"rate":0.065, "dist":3},  # Arbusto
        11: {"rate":0.025, "dist":4},  # Pedra
        10: {"rate":0.015, "dist":5},  # Cobre
        5:  {"rate":0.002, "dist":5},  # Ouro
    },

    # 6 MÁGICO
    6: {
        9:  {"rate":0.004, "dist":5},  # Ametista
        12: {"rate":0.025, "dist":3},  # Arbusto
        11: {"rate":0.028, "dist":4},  # Pedra
    },

    # 7 VULCÂNICO
    7: {
        13: {"rate":0.025, "dist":10},  # Poça de Lava
        11: {"rate":0.060, "dist":4},  # Pedra
        10: {"rate":0.016, "dist":5},  # Cobre
        5:  {"rate":0.002, "dist":5},  # Ouro
        8:  {"rate":0.005, "dist":5},  # Rubi
    },
}

def gerar_objetos(biomas, blocos, cfg_bioma=None, taxa_bioma=None, seed=None, usar_pesos_por_obj=True):
    """
    Novo sistema:
      - Cada BIOMA tem uma taxa base p_bioma de tentar gerar ALGO no bloco.
      - Para o bloco (y,x), contamos quantos objetos desse bioma estão BLOQUEADOS pela dist.
      - A chance efetiva vira: p_eff = p_bioma * (1 - bloqueados / total_disponiveis).
      - Se passar em p_eff, escolhemos 1 entre os objetos NÃO bloqueados (uniforme por padrão;
        opcionalmente ponderado por 'rate' do objeto se usar_pesos_por_obj=True).
      - Distância mínima vale contra QUALQUER objeto já colocado (métrica de Chebyshev).

    Obs.:
      - 'rate' de OBJ_POR_BIOMA_PADRAO não é probabilidade de spawn; só pode servir
        como peso de escolha entre os objetos disponíveis se usar_pesos_por_obj=True.
    """
    H, W = biomas.shape
    objetos = np.zeros((H, W), dtype=np.uint8)

    rng = np.random.default_rng(seed)
    conf_obj = OBJ_POR_BIOMA_PADRAO if cfg_bioma is None else cfg_bioma
    taxa_base = TAXA_SPAWN_BIOMA_PADRAO if taxa_bioma is None else taxa_bioma

    # Processa bioma a bioma para ter controle fino
    biomas_unicos = sorted(set(int(b) for b in np.unique(biomas)))
    for b in biomas_unicos:
        # pula biomas sem config de objetos ou sem taxa base > 0
        if b not in conf_obj or not conf_obj[b]:
            continue
        p_bioma = float(taxa_base.get(b, 0.0))
        if p_bioma <= 0.0:
            continue

        # máscara e lista de células do bioma
        mask_b = (biomas == b)
        ys, xs = np.where(mask_b)
        if ys.size == 0:
            continue

        # visita as células do bioma em ordem aleatória
        ordem = rng.permutation(ys.size)
        ys = ys[ordem]; xs = xs[ordem]

        obj_ids = list(conf_obj[b].keys())
        total_disp = len(obj_ids)

        for y, x in zip(ys, xs):
            if objetos[y, x] != 0:
                continue

            # atalho: se o sorteio já falha na taxa base, nem calcula bloqueios
            u = rng.random()
            if u >= p_bioma:
                continue

            # avalia bloqueios por dist (contra QUALQUER objeto)
            disponiveis = []
            bloqueados = 0

            for obj_id in obj_ids:
                dist = int(conf_obj[b][obj_id].get("dist", 0))
                if dist <= 0:
                    # sem dist -> sempre disponível
                    disponiveis.append(obj_id)
                    continue

                y0 = max(0, y - dist); y1 = min(H, y + dist + 1)
                x0 = max(0, x - dist); x1 = min(W, x + dist + 1)
                # se houver QUALQUER objeto nessa janela, está bloqueado
                if (objetos[y0:y1, x0:x1] != 0).any():
                    bloqueados += 1
                else:
                    disponiveis.append(obj_id)

            if total_disp == 0 or not disponiveis:
                continue  # nada pode ser gerado aqui

            # aplica a penalidade pela fração bloqueada
            p_eff = p_bioma * (1.0 - (bloqueados / total_disp))
            if u >= p_eff:
                continue  # não passou no corte ajustado

            # escolhe 1 objeto entre os disponíveis
            if usar_pesos_por_obj:
                pesos = np.array([float(conf_obj[b][oid].get("rate", 0.0)) for oid in disponiveis], dtype=np.float64)
                soma = pesos.sum()
                if soma > 0:
                    probs = pesos / soma
                    escolhe_idx = rng.choice(len(disponiveis), p=probs)
                else:
                    escolhe_idx = rng.integers(0, len(disponiveis))
            else:
                escolhe_idx = rng.integers(0, len(disponiveis))

            objetos[y, x] = np.uint8(disponiveis[escolhe_idx])

    return objetos
# ----------------- Exemplo de uso -----------------
def GerarMundo(W=1000,H=1000,seed=random.randint(0,100000),img=False):
    # Gera com config global + overrides opcionais
    biomas, blocos, dbg = gerar_mapa(W=W, H=H, seed=seed)

    # Escala real da grid (ex.: 2x) para visual maior sem alterar regras
    biomas_s, blocos_s, dbg_s = scale(biomas, blocos, dbg, fator=1)
    objetos = gerar_objetos(biomas_s, blocos_s, seed=seed)

    from collections import Counter

    # Flatten a grid (transforma lista de listas em uma lista única)
    todos_objetos = [valor for linha in objetos for valor in linha]

    # Conta frequência de cada ID
    contagem = Counter(todos_objetos)

    # Mostra resultado
    for id_obj, qtde in contagem.items():
        print(f"ID {id_obj}: {qtde} ocorrências")

    # Gera imagem diretamente da grid (sem scale na imagem)
    if img:
        imgm = imagem_dos_blocos(blocos_s, save_path="mapa_blocos.png")
        img_biomas = imagem_dos_biomas(biomas_s, save_path="mapa_biomas.png")
        print("Imagem salva em mapa_blocos.png")

    return blocos_s, biomas_s, objetos

# GerarMundo(img=True)
