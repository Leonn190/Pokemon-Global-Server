import pygame
import math

from Codigo.Prefabs.FunçõesPrefabs import Barra, Scrolavel, Slider, BarraMovel, SurfaceAtaque
from Codigo.Prefabs.BotoesPrefab import Botao, Botao_invisivel, Botao_Surface, Botao_Selecao
from Codigo.Prefabs.Animações import Animação
from Codigo.Prefabs.Arrastavel import Arrastavel
from Codigo.Modulos.DesenhoPlayer import DesenharPlayer
from Codigo.Geradores.GeradorPokemon import CarregarAnimacaoPokemon, CarregarPokemon

cores = None
fontes = None
texturas = None
fundos = None
outros = None
pokemons = None
estruturas = None
equipaveis = None
consumiveis = None
animaçoes = None
icones = None

def BarraDeItens(tela, player, eventos): 
    from Codigo.Cenas.Mundo import Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes, Icones
    global cores, fontes, texturas, fundos, outros, pokemons, estruturas, equipaveis, consumiveis, animaçoes, icones

    if cores == None:
        cores = Cores
        fontes = Fontes
        texturas = Texturas
        fundos = Fundos
        outros = Outros
        pokemons = Pokemons
        estruturas = Estruturas
        equipaveis = Equipaveis
        consumiveis = Consumiveis
        animaçoes = Animaçoes
        icones = Icones

    TAMANHO_SLOT = 60
    ESPACO = 4
    QUANTIDADE = 10

    largura_total = TAMANHO_SLOT * QUANTIDADE + ESPACO * (QUANTIDADE - 1)
    altura_total = TAMANHO_SLOT + 8

    largura_tela = tela.get_width()
    altura_tela = tela.get_height()

    x_inicial = (largura_tela - largura_total) // 2
    y_inicial = altura_tela - altura_total - 8

    # === Trata scroll do mouse (MOUSEWHEEL) ===
    for evento in eventos:
        if evento.type == pygame.MOUSEWHEEL:
            inventario_util = player.Inventario[:QUANTIDADE]
            if inventario_util:
                player.Selecionado = (player.Selecionado - evento.y) % len(inventario_util)

    # Desenha fundo da barra inteira
    barra_rect = pygame.Rect(x_inicial - 4, y_inicial - 4, largura_total + 8, altura_total + 8)
    pygame.draw.rect(tela, (0, 0, 0), barra_rect, border_radius=6)

    itens_visiveis = player.Inventario[:QUANTIDADE]
    fonte = Fontes[20]
    fundo_slot = pygame.transform.scale(fundos["FundoSlots"], (TAMANHO_SLOT, TAMANHO_SLOT))

    for i in range(QUANTIDADE):
        x = x_inicial + i * (TAMANHO_SLOT + ESPACO)
        y = y_inicial

        pygame.draw.rect(tela, (0, 0, 0), (x - 1, y - 1, TAMANHO_SLOT + 2, TAMANHO_SLOT + 2))  # borda preta
        tela.blit(fundo_slot, (x, y))

        index_in_inventario = i
        if 0 <= index_in_inventario < len(player.Inventario):
            item = player.Inventario[index_in_inventario]
            if item:
                nome = item.get("nome")
                numero = item.get("numero", 1)
                imagem = consumiveis.get(nome)

                if imagem:
                    imagem_redimensionada = pygame.transform.scale(imagem, (TAMANHO_SLOT - 10, TAMANHO_SLOT - 10))
                    img_rect = imagem_redimensionada.get_rect(center=(x + TAMANHO_SLOT // 2, y + TAMANHO_SLOT // 2))
                    tela.blit(imagem_redimensionada, img_rect)

                # Número do item
                texto = fonte.render(str(numero), True, (0, 0, 0))
                texto_rect = texto.get_rect(bottomright=(x + TAMANHO_SLOT - 4, y + TAMANHO_SLOT - 4))
                tela.blit(texto, texto_rect)

        # Borda amarela no item selecionado
        if i == player.Selecionado and i < len(itens_visiveis):
            pygame.draw.rect(tela, (255, 255, 0), (x - 2, y - 2, TAMANHO_SLOT + 4, TAMANHO_SLOT + 4), 2)

def PainelItem(tela, pos, item):
    if item is None:
        return

    x, y = pos
    largura = 350
    altura = 610
    cor_fundo = (139, 69, 19)
    raio_borda = 6
    espacamento = 32

    # === Painel de fundo com borda arredondada ===
    pygame.draw.rect(tela, cor_fundo, (x, y, largura, altura), border_radius=raio_borda)

    # === Cabeçalho ===
    nome = item["nome"]
    fonte_nome = fontes[50]
    texto_nome = fonte_nome.render(nome, True, (255, 255, 255))
    nome_x = x + (largura - texto_nome.get_width()) // 2
    nome_y = y + espacamento
    tela.blit(texto_nome, (nome_x, nome_y))

    # === Imagem do item ===
    imagem_item = pygame.transform.scale(consumiveis[nome], (95, 95))
    imagem_x = x + (largura - 80) // 2
    imagem_y = nome_y + texto_nome.get_height() + espacamento
    tela.blit(imagem_item, (imagem_x, imagem_y))

    # === Descrição ===
    descricao = item.get("descrição", "")
    fonte_descricao = fontes[101]
    largura_texto = round(largura * 0.85)
    inicio_texto_y = imagem_y + 80 + espacamento
    cor_texto = (230, 230, 230)

    def quebrar_texto(texto, fonte, largura_max):
        palavras = texto.split(" ")
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste_linha = linha_atual + (" " if linha_atual else "") + palavra
            if fonte.size(teste_linha)[0] <= largura_max:
                linha_atual = teste_linha
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    linhas = quebrar_texto(descricao, fonte_descricao, largura_texto)
    for i, linha in enumerate(linhas):
        render = fonte_descricao.render(linha, True, cor_texto)
        render_x = x + (largura - render.get_width()) // 2
        render_y = inicio_texto_y + i * (fonte_descricao.get_height() + 5)
        tela.blit(render, (render_x, render_y))

    # === Quarto setor: Raridade, Estilo, Quantidade (alinhados) ===
    raridades = ["Comum", "Incomum", "Raro", "Épico", "Mítico", "Lendário"]
    raridade_index = max(1, min(6, int(item.get("raridade", 1)))) - 1
    raridade_str = raridades[raridade_index]

    estilo = item.get("estilo", "Neutro").capitalize()
    quantidade = item.get("numero", 1)

    info_dict = {
        "Raridade": raridade_str,
        "Estilo": estilo,
        "Quantidade": str(quantidade)
    }

    fonte_info = fontes[25]
    y_info_inicio = inicio_texto_y + len(linhas) * (fonte_descricao.get_height() + 5) + espacamento
    margem_lateral = x + int(largura * 0.1)
    largura_info_total = int(largura * 0.85)

    for i, (chave, valor) in enumerate(info_dict.items()):
        label = f"{chave}:"
        texto_label = fonte_info.render(label, True, (255, 255, 255))
        texto_valor = fonte_info.render(valor, True, (255, 255, 255))

        y_linha = y_info_inicio + i * (fonte_info.get_height() + 5)
        tela.blit(texto_label, (margem_lateral, y_linha))

        valor_x = margem_lateral + largura_info_total - texto_valor.get_width()
        tela.blit(texto_valor, (valor_x, y_linha))

pokemon_cache = None 
pokemon_refresh = False
pokemon_atributos_salvos = []
idle = None

# ---- Estado global desta UI (mesma ideia do inventário) ----
arrastaveis_movelist = []
arrastaveis_memo = []
areas_moves = []      # rects dos 4 slots (coluna MoveList)
areas_memoria = []    # rects dos 8 slots (coluna Memoria)
areas_hab_ativas = []
areas_hab_memoria = []
_moves_cache = None
_mem_cache = None
_hab_a_cache = None
_hab_m_cache = None
pokemon_ref = None   # referência ao pokemon sendo editado (para o executor saber onde trocar)

areas_build = []
arrastaveis_build = []
_build_cache_list = None
_build_cache_n = None

PAINEL_ATAQUE_CACHE = {}

def PainelPokemon(tela, pos, pokemon, estado_barra, eventos, parametros):
    global pokemon_cache, pokemon_refresh, pokemon_atributos_salvos

    # ========= PALETA =========
    PALETA = {
        # painel
        "fundo": (20, 20, 20),
        "cabecalho": (35, 35, 35),
        "linha_separadora": (0, 0, 0),
        "borda_painel": (0, 0, 0),

        # textos
        "texto_cabecalho": (255, 255, 255),
        "texto": (255, 255, 255),

        # tipagem
        "tipagem_area_bg": (35, 35, 35),
        "tipagem_pill_bg": (50, 50, 50),
        "tipagem_circulo": (255, 255, 255),
        "tipagem_pct": (235, 235, 235),

        # barras de atributos (12 cores)
        "barras": [
            (255, 0, 0),      # Vida
            (255, 128, 0),    # Atk
            (255, 255, 0),    # Def
            (128, 255, 0),    # SpA
            (0, 255, 0),      # SpD
            (0, 255, 128),    # Vel
            (0, 255, 255),    # Mag
            (0, 128, 255),    # Per
            (0, 0, 255),      # Ene
            (128, 0, 255),    # EnR
            (255, 0, 255),    # CrD
            (255, 0, 128),    # CrC
        ],

        # blocos informativos
        "caixa_info_bg": (70, 70, 70),
        "caixa_info_borda": (0, 0, 0),
    }

    atributos = [
        ("Vida", "IV_Vida"),
        ("Atk", "IV_Atk"),
        ("Def", "IV_Def"),
        ("SpA", "IV_SpA"),
        ("SpD", "IV_SpD"),
        ("Vel", "IV_Vel"),
        ("Mag", "IV_Mag"),
        ("Per", "IV_Per"),
        ("Ene", "IV_Ene"),
        ("EnR", "IV_EnR"),
        ("CrD", "IV_CrD"),
        ("CrC", "IV_CrC"),
    ]

    # ========= Parâmetros base =========
    largura_painel = 1300
    altura_painel  = 700
    x0, y0 = pos

    # ========= Fundo do painel =========
    cor_fundo      = PALETA["fundo"]
    cor_cabecalho  = PALETA["cabecalho"]
    altura_cabecalho = 70
    pygame.draw.rect(tela, cor_fundo, (x0, y0, largura_painel, altura_painel))

    # trecho para animar a barra de status sempre que o pokemon trocar
    if pokemon_refresh:
        for i, (attr, _) in enumerate(atributos):
            pokemon[attr] = pokemon_atributos_salvos[i]
            pokemon_refresh = False

    if pokemon_cache != pokemon.get("ID"):
        pokemon_cache = pokemon.get("ID")
        pokemon_atributos_salvos.clear()
        for attr, _ in atributos:
            pokemon_atributos_salvos.append(pokemon.get(attr, 0))
            pokemon[attr] = 0
        pokemon_refresh = True

    fonte_nome = fontes[24]
    fonte_valor = fontes[25]
    fonte_iv = fontes[16]

    def _desenhar_cabecalho():
        """
        Desenha o cabeçalho à esquerda da área de tipagem (400px).
        """
        AREA_W_TIPAGEM = 400
        cab_x   = x0
        cab_y   = y0
        cab_w   = largura_painel - AREA_W_TIPAGEM
        cab_h   = altura_cabecalho
        sep_x   = x0 + largura_painel - AREA_W_TIPAGEM  # divisor vertical com a tipagem

        # fundo do cabeçalho (apenas na área à esquerda)
        pygame.draw.rect(tela, cor_cabecalho, (cab_x, cab_y, cab_w, cab_h))

        # botão (canto esquerdo)
        botao_tam = min(60, cab_h - 4)
        botao_x = cab_x + 8
        botao_y = cab_y + 8
        Botao_Surface(
            tela, (botao_x, botao_y, botao_tam, botao_tam),
            icones["Voltar"], lambda: parametros.update({"PokemonSelecionado": None}),eventos)

        # imagem do Pokémon (canto direito do cabeçalho, antes do divisor vertical)
        nome_poke = str(pokemon.get("Nome", ""))
        if pokemon_refresh:
            imagem = pokemons.get(nome_poke.lower(), CarregarPokemon(nome_poke.lower(), pokemons))
        else:
            imagem = pokemons.get(nome_poke.lower())

        img_pad = 2
        img_size = botao_tam
        img_x = sep_x - img_size - img_pad
        img_y = cab_y + img_pad
        if imagem:
            imagem_redim = pygame.transform.smoothscale(imagem, (img_size, img_size))
            tela.blit(imagem_redim, (img_x, img_y))

        # nome centralizado dentro da área do cabeçalho
        try:
            fonte_cabecalho = fontes[35] if 35 < len(fontes) and fontes[35] else fontes[0]
        except Exception:
            fonte_cabecalho = fontes[0]
        txt_nome = fonte_cabecalho.render(nome_poke, True, PALETA["texto_cabecalho"])
        cx = cab_x + cab_w // 2
        cy = cab_y + cab_h // 2
        txt_nome_rect = txt_nome.get_rect(center=(cx, cy))
        tela.blit(txt_nome, txt_nome_rect)

        # divisor vertical entre cabeçalho e tipagem
        pygame.draw.line(tela, PALETA["linha_separadora"], (sep_x, cab_y), (sep_x, cab_y + cab_h), 3)

    def _desenhar_tipagem():
        # Área reservada (400px à direita)
        AREA_W = 400
        area_x = x0 + largura_painel - AREA_W
        area_y = y0
        area_h = altura_cabecalho

        # Fundo cinza escuro "sobre esse terreno"
        pygame.draw.rect(tela, PALETA["tipagem_area_bg"], (area_x, area_y, AREA_W, area_h))

        # Pílula (350x50)
        PILL_W, PILL_H = 350, 50
        pill_x = area_x + (AREA_W - PILL_W) // 2
        pill_y = area_y + (area_h - PILL_H) // 2
        pill_rect = pygame.Rect(pill_x, pill_y, PILL_W, PILL_H)
        pygame.draw.rect(tela, PALETA["tipagem_pill_bg"], pill_rect, border_radius=PILL_H // 2)

        # Layout interno
        inner_pad   = 16
        item_gap    = 21
        icon_size   = 33
        circle_r    = icon_size // 2 + 1
        center_y    = pill_y + PILL_H // 2
        cursor_x    = pill_x + inner_pad

        # Render por tipo
        for idx in (1, 2, 3):
            tipo = pokemon.get(f"Tipo{idx}")
            if not tipo:
                continue

            icon = icones.get(tipo)
            if icon is None and isinstance(tipo, str):
                icon = icones.get(tipo.lower()) or icones.get(tipo.capitalize())
            if icon is None:
                continue

            pct_val = pokemon.get(f"%{idx}", 0)
            try:
                if isinstance(pct_val, str) and pct_val.strip().endswith("%"):
                    pct_txt = pct_val.strip()
                else:
                    v = float(pct_val)
                    pct_txt = f"{int(round(v))}%"
            except Exception:
                pct_txt = f"{pct_val}%" if str(pct_val).strip() != "" else "0%"

            txt_surf = fontes[20].render(pct_txt, True, PALETA["tipagem_pct"])
            needed_w = circle_r * 2 + 8 + txt_surf.get_width()
            if cursor_x + needed_w + inner_pad > pill_rect.right:
                break

            # círculo branco + ícone
            cx = cursor_x + circle_r
            pygame.draw.circle(tela, PALETA["tipagem_circulo"], (cx, center_y), circle_r)
            ic = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            tela.blit(ic, (cx - icon_size // 2, center_y - icon_size // 2))

            # percentual
            txt_x = cx + circle_r + 8
            tela.blit(txt_surf, (txt_x, center_y - txt_surf.get_height() // 2))

            cursor_x = txt_x + txt_surf.get_width() + item_gap

    def _desenhar_animacao():
        global idle

        ANIM_W, ANIM_H = 175, 175
        LEFT = x0 + 50
        TOP  = y0 + 100

        CX = LEFT + ANIM_W // 2
        CY = TOP  + ANIM_H // 2

        nome_poke = pokemon.get("Nome") or pokemon.get("Name") or str(pokemon.get("ID", ""))
        frames = animaçoes.get(nome_poke)

        if pokemon_refresh:
            frames = animaçoes.get(nome_poke, CarregarAnimacaoPokemon(nome_poke, animaçoes))
            idle = Animação(frames=frames, posicao=(CX, CY), intervalo=28, tamanho=1.2)

        nivel = int(pokemon.get("Nivel", 1))
        txt_nivel = fonte_nome.render(f"Nível {nivel}", True, PALETA["texto"])
        txt_nivel_rect = txt_nivel.get_rect(center=(CX, CY - ANIM_H // 2 - 12))
        tela.blit(txt_nivel, txt_nivel_rect)

        idle.atualizar(tela)

        xp_atual = int(pokemon.get("XP", 0))
        xp_max = max(1, nivel * 10)

        BAR_W, BAR_H = ANIM_W, 18
        bar_x = CX - BAR_W // 2
        bar_y = CY + ANIM_H // 2 + 10
        cor_xp = cores["verde"]  # mantido: usa paleta global 'cores'

        Barra(
            tela,
            (bar_x, bar_y),
            (BAR_W, BAR_H),
            xp_atual,
            xp_max,
            cor_xp,
            estado_barra,
            "XP",
            vertical=False
        )

        txt_xp = fontes[16].render(f"XP: {xp_atual} / {xp_max}", True, PALETA["texto"])
        txt_xp_rect = txt_xp.get_rect(center=(CX, bar_y + BAR_H + 16))
        tela.blit(txt_xp, txt_xp_rect)

    def _desenhar_moves_memoria(pos):

        # ========= Globais / Estado =========
        global arrastaveis_movelist, arrastaveis_memo, areas_moves, areas_memoria
        global areas_hab_ativas, areas_hab_memoria
        global _moves_cache, _mem_cache, _hab_a_cache, _hab_m_cache, pokemon_ref

        pokemon_ref = pokemon

        # ========= Cores =========
        COR_HEAD         = (52, 52, 52)
        COR_SLOT         = (40, 40, 40)
        COR_SLOT_HAB     = (56, 40, 40)
        COR_TEXTO        = (230, 230, 230)

        # ========= Fontes =========
        fonte_head = fontes[16] if 16 < len(fontes) and fontes[16] else (fontes[0] if fontes else None)
        if fonte_head is None:
            raise RuntimeError("Lista 'fontes' inválida ou vazia.")

        # ========= Geometria base =========
        x0, y0 = pos
        PAD_EXTERNO      = 10   # bordas do fundo
        COL_GAP          = 8   # gap entre as colunas (entre cabeçalhos)
        HEAD_H           = 24   # altura da barra de cabeçalho
        HEAD_TO_ROWS_GAP = 10    # << NOVO: distância do cabeçalho até o início das linhas
        ROW_GAP          = 12   # distância vertical entre linhas
        SLOT_H           = 28   # altura dos slots (mesma para todos)
        SLOT_MOV_W       = 175  # largura slot MoveList
        SLOT_MEM_W       = 145  # largura slot Memoria

        # Larguras fixas de "colunas" conforme cabeçalhos
        W_MOV_HEAD       = 195
        W_MEM_HEAD       = 345

        # Linhas: 4 (moves) + habilidades (1 ou 2)
        hab_nivel   = int(pokemon.get("Habilidades", 1))
        linhas_hab  = 2 if hab_nivel >= 2 else 1

        # Colunas
        col_mov_x = x0 + PAD_EXTERNO
        col_mov_y = y0 + PAD_EXTERNO
        col_mem_x = col_mov_x + W_MOV_HEAD + COL_GAP
        col_mem_y = col_mov_y

        # Cabeçalhos
        head_mov_rect = pygame.Rect(col_mov_x, col_mov_y, W_MOV_HEAD, HEAD_H)
        head_mem_rect = pygame.Rect(col_mem_x, col_mem_y, W_MEM_HEAD, HEAD_H)
        pygame.draw.rect(tela, COR_HEAD, head_mov_rect, border_radius=8)
        pygame.draw.rect(tela, COR_HEAD, head_mem_rect, border_radius=8)

        tela.blit(fonte_head.render("MoveList", True, COR_TEXTO), (head_mov_rect.x + 8, head_mov_rect.y + 2))
        tela.blit(fonte_head.render("Memoria",  True, COR_TEXTO), (head_mem_rect.x + 8, head_mem_rect.y + 2))

        # ========= Lacunas =========
        # Y inicial agora considera o GAP extra após o cabeçalho
        base_y = col_mov_y + HEAD_H + HEAD_TO_ROWS_GAP

        # MoveList
        areas_moves.clear()
        mov_margin_x = (W_MOV_HEAD - SLOT_MOV_W) // 2
        slot_rad = 10

        for i in range(4):
            atk = pokemon_ref["MoveList"][i]
            sy = base_y + i * (SLOT_H + ROW_GAP)
            sx = col_mov_x + mov_margin_x
            r = pygame.Rect(sx, sy, SLOT_MOV_W, SLOT_H)
            pygame.draw.rect(tela, COR_SLOT, r, border_radius=slot_rad)
            if atk is not None:
                Botao_invisivel((r.x, r.y, r.width, r.height),lambda: parametros.update({"AtaqueSelecionado": atk}))
            areas_moves.append(r)

        # Memoria
        areas_memoria.clear()
        m_float = (W_MEM_HEAD - 2 * SLOT_MEM_W) / 3.0
        m_left  = int(round(m_float))
        m_mid   = int(round(m_float))
        used    = m_left + SLOT_MEM_W + m_mid + SLOT_MEM_W
        m_right = W_MEM_HEAD - used
        col1_x  = col_mem_x + m_left
        col2_x  = col_mem_x + m_left + SLOT_MEM_W + m_mid

        for row in range(4):
            idx1 = row * 2
            idx2 = row * 2 + 1
            atk  = pokemon_ref["Memoria"][idx1]
            atk2 = pokemon_ref["Memoria"][idx2]
            sy = base_y + row * (SLOT_H + ROW_GAP)
            r1 = pygame.Rect(col1_x, sy, SLOT_MEM_W, SLOT_H)
            r2 = pygame.Rect(col2_x, sy, SLOT_MEM_W, SLOT_H)
            pygame.draw.rect(tela, COR_SLOT, r1, border_radius=slot_rad)
            pygame.draw.rect(tela, COR_SLOT, r2, border_radius=slot_rad)
            if atk is not None:
                Botao_invisivel((r1.x, r1.y, r1.width, r1.height),lambda atk=atk: parametros.update({"AtaqueSelecionado": atk}))
            if atk2 is not None:
                Botao_invisivel((r2.x, r2.y, r2.width, r2.height),lambda atk2=atk2: parametros.update({"AtaqueSelecionado": atk2}))
            areas_memoria.extend([r1, r2])

        # Habilidades
        areas_hab_ativas.clear()
        areas_hab_memoria.clear()
        for hlin in range(linhas_hab):
            row_index = 4 + hlin
            sy = base_y + row_index * (SLOT_H + ROW_GAP)

            r_ativa = pygame.Rect(col_mov_x + mov_margin_x, sy, SLOT_MOV_W, SLOT_H)
            pygame.draw.rect(tela, COR_SLOT_HAB, r_ativa, border_radius=slot_rad)
            areas_hab_ativas.append(r_ativa)

            r_m1 = pygame.Rect(col1_x, sy, SLOT_MEM_W, SLOT_H)
            r_m2 = pygame.Rect(col2_x, sy, SLOT_MEM_W, SLOT_H)
            pygame.draw.rect(tela, COR_SLOT_HAB, r_m1, border_radius=slot_rad)
            pygame.draw.rect(tela, COR_SLOT_HAB, r_m2, border_radius=slot_rad)
            areas_hab_memoria.extend([r_m1, r_m2])

        # ========= Função utilitária =========
        def build_surface_from_attack(atk, slot_rect, main_flag):
            return SurfaceAtaque(
                {
                    "nome":  atk.get("nome") or atk.get("Ataque", "") or atk.get("Nome", ""),
                    "tipo":  (atk.get("tipo") or atk.get("Tipo") or "normal"),
                    "custo": atk.get("custo") or atk.get("Custo", 0),
                    "dano":  atk.get("dano")  or atk.get("Dano", 0),
                    "estilo":atk.get("estilo") or atk.get("Estilo", "n"),
                    "alvo":  atk.get("alvo")  or atk.get("Alvo", "-"),
                    "descrição": atk.get("descrição") or atk.get("Descrição", ""),
                },
                fontes=fontes, icones=icones,
                main=main_flag
            )

        # ========= Executor (inalterado) =========
        def executar_moves_memoria(arr):
            interno = arr.interno
            pos     = arr.pos
            dados   = arr.dados

            if interno:
                origem = pokemon_ref["MoveList"].index(dados)

                # Soltou em alguma lacuna da MoveList -> swap dentro da própria lista
                for i, area in enumerate(areas_moves):
                    if area.collidepoint(pos):
                        if i >= len(pokemon_ref["MoveList"]):            # slot sem item correspondente
                            return False
                        if pokemon_ref["MoveList"][origem] == pokemon_ref["MoveList"][i]:
                            return False
                        pokemon_ref["MoveList"][origem], pokemon_ref["MoveList"][i] = (
                            pokemon_ref["MoveList"][i], pokemon_ref["MoveList"][origem]
                        )
                        return True

                # Soltou em alguma lacuna da Memoria -> swap entre listas
                for i, area in enumerate(areas_memoria):
                    if area.collidepoint(pos):
                        if i >= len(pokemon_ref["Memoria"]):
                            return False
                        pokemon_ref["Memoria"][i], pokemon_ref["MoveList"][origem] = (
                            pokemon_ref["MoveList"][origem], pokemon_ref["Memoria"][i]
                        )
                        return True

                return False

            else:
                origem = pokemon_ref["Memoria"].index(dados)
                # Soltou em alguma lacuna da Memoria -> swap dentro da própria lista
                for i, area in enumerate(areas_memoria):
                    if area.collidepoint(pos):
                        if i >= len(pokemon_ref["Memoria"]):
                            return False
                        if pokemon_ref["Memoria"][origem] == pokemon_ref["Memoria"][i]:
                            return False
                        pokemon_ref["Memoria"][origem], pokemon_ref["Memoria"][i] = (
                            pokemon_ref["Memoria"][i], pokemon_ref["Memoria"][origem]
                        )
                        return True

                # Soltou em alguma lacuna da MoveList -> swap entre listas
                for i, area in enumerate(areas_moves):
                    if area.collidepoint(pos):
                        if i >= len(pokemon_ref["MoveList"]):
                            return False
                        pokemon_ref["MoveList"][i], pokemon_ref["Memoria"][origem] = (
                            pokemon_ref["Memoria"][origem], pokemon_ref["MoveList"][i]
                        )
                        return True

                return False

        if _moves_cache != pokemon_ref["MoveList"]:
            _moves_cache = list(pokemon_ref["MoveList"])
            # primeiro remove arrastáveis dessa área
            arrastaveis_movelist.clear()
            # recria os novos
            for i in range(min(4, len(pokemon_ref["MoveList"]))):
                atk = pokemon_ref["MoveList"][i]
                if atk is not None:
                    r   = areas_moves[i]
                    surf = build_surface_from_attack(atk, r, main_flag=True)
                    px, py = r.centerx - surf.get_width()//2, r.centery - surf.get_height()//2
                    arrastaveis_movelist.append(
                        Arrastavel(surf, (px, py), dados=atk, interno=True, funcao_execucao=executar_moves_memoria)
                    )

        # ========= Memoria =========
        if _mem_cache != pokemon_ref["Memoria"]:
            _mem_cache = list(pokemon_ref["Memoria"])
            arrastaveis_memo.clear()
            for i in range(min(8, len(pokemon_ref["Memoria"]))):
                atk = pokemon_ref["Memoria"][i]
                if atk is not None:
                    r   = areas_memoria[i]
                    surf = build_surface_from_attack(atk, r, main_flag=False)
                    px, py = r.centerx - surf.get_width()//2, r.centery - surf.get_height()//2
                    arrastaveis_memo.append(
                        Arrastavel(surf, (px, py), dados=atk, interno=False, funcao_execucao=executar_moves_memoria)
                    )

        # hab_ativas  = pokemon_ref["HabilidadesAtivas"]
        # hab_memoria = pokemon_ref["HabilidadesMemoria"]

        # # ========= Habilidades Ativas =========
        # if _hab_a_cache is not hab_ativas:
        #     _hab_a_cache = hab_ativas
        #     arrastaveis_moves_mem = [a for a in arrastaveis_moves_mem if a.dados not in _hab_a_cache]
        #     for i, r in enumerate(areas_hab_ativas):
        #         if i < len(hab_ativas):
        #             hab = hab_ativas[i]
        #             surf = build_surface_from_attack(hab, r, main_flag=True)
        #             px, py = r.centerx - surf.get_width()//2, r.centery - surf.get_height()//2
        #             arrastaveis_moves_mem.append(
        #                 Arrastavel(surf, (px, py), dados=hab, interno=True, funcao_execucao=None)
        #             )

        # # ========= Habilidades Memória =========
        # if _hab_m_cache is not hab_memoria:
        #     _hab_m_cache = hab_memoria
        #     arrastaveis_moves_mem = [a for a in arrastaveis_moves_mem if a.dados not in _hab_m_cache]
        #     for i, r in enumerate(areas_hab_memoria):
        #         if i < len(hab_memoria):
        #             hab = hab_memoria[i]
        #             surf = build_surface_from_attack(hab, r, main_flag=False)
        #             px, py = r.centerx - surf.get_width()//2, r.centery - surf.get_height()//2
        #             arrastaveis_moves_mem.append(
        #                 Arrastavel(surf, (px, py), dados=hab, interno=True, funcao_execucao=None)
        #             )

        # ========= Atualização/desenho arrastáveis =========
        mouse_pos = pygame.mouse.get_pos()
        for arr in arrastaveis_memo + arrastaveis_movelist:
            arr.atualizar(eventos)
            arr.arrastar(mouse_pos)

        for arr in arrastaveis_memo + arrastaveis_movelist:
            if not getattr(arr, "esta_arrastando", False):
                arr.desenhar(tela)
        for arr in arrastaveis_memo + arrastaveis_movelist:
            if getattr(arr, "esta_arrastando", False):
                arr.desenhar(tela)

    def desenha_build(pos):

        # ======= Globais/estado =======
        global areas_build, arrastaveis_build, _build_cache_list, _build_cache_n

        # ======= Paleta (similar à desenhar_moves_memoria) =======
        COR_HEAD   = (52, 52, 52)
        COR_SLOT   = (40, 40, 40)
        COR_TEXTO  = (230, 230, 230)
        COR_PLUS   = (200, 200, 200)

        # ======= Geometria base (forçada) =======
        x0, y0 = pos
        W, H = 100, 260  # sempre 100x270
        PAD_EXTERNO      = 10
        HEAD_H           = 24
        GAP_HEAD_TO_ROW  = 12
        RAD              = 10
        SLOT_SIDE        = 50  # sempre 64x64
        SLOT_GAP         = 14   # << novo: espaçamento fixo entre slots

        # Cabeçalho
        head_rect = pygame.Rect(x0 + PAD_EXTERNO, y0 + PAD_EXTERNO, W - 2*PAD_EXTERNO, HEAD_H)
        pygame.draw.rect(tela, COR_HEAD, head_rect, border_radius=8)
        try:
            fonte_head = fontes[16] if 16 < len(fontes) and fontes[16] else fontes[0]
        except Exception:
            fonte_head = fontes[0]
        txt = fonte_head.render("Build", True, COR_TEXTO)
        tela.blit(txt, (head_rect.x + 8, head_rect.y + (HEAD_H - txt.get_height()) // 2))

        # Área útil das lacunas
        inner_x = x0 + PAD_EXTERNO
        inner_y = head_rect.bottom + GAP_HEAD_TO_ROW
        inner_w = W - 2*PAD_EXTERNO
        # inner_h = H - (inner_y - y0) - PAD_EXTERNO  # (não usado mais)

        # ======= Quantidade e distribuição vertical =======
        n_slots = int(max(1, min(3, pokemon.get("Equipaveis", 1))))
        slot_x = inner_x + (inner_w - SLOT_SIDE) // 2  # mantém centralização horizontal
        cy = inner_y                                   # começa logo após o cabeçalho

        # ======= Desenho das lacunas (empilhadas) =======
        areas_build.clear()
        for i in range(n_slots):
            r = pygame.Rect(slot_x, cy, SLOT_SIDE, SLOT_SIDE)
            pygame.draw.rect(tela, COR_SLOT, r, border_radius=RAD)

            # Sinal de '+'
            cx, cy_mid = r.center
            arm = int(SLOT_SIDE * 0.32)
            lw  = max(2, SLOT_SIDE // 12)
            pygame.draw.line(tela, COR_PLUS, (cx - arm, cy_mid), (cx + arm, cy_mid), lw)
            pygame.draw.line(tela, COR_PLUS, (cx, cy_mid - arm), (cx, cy_mid + arm), lw)

            areas_build.append(r)
            cy = r.bottom + SLOT_GAP  # próxima lacuna desce fixo

        # ======= Arrastáveis da build =======
        build_list = pokemon.get("Build", []) or []
        needs_rebuild = (_build_cache_list != build_list) or (_build_cache_n != n_slots)
        if needs_rebuild:
            _build_cache_list = list(build_list)
            _build_cache_n = n_slots
            arrastaveis_build.clear()

            for i in range(min(n_slots, len(build_list))):
                item = build_list[i]
                if not item:
                    continue
                nome_item = item.get("nome") or item.get("Nome")
                if not nome_item:
                    continue
                img = equipaveis.get(nome_item)
                if not img:
                    continue

                slot_r = areas_build[i]
                pad_img = max(4, SLOT_SIDE // 10)
                target = (SLOT_SIDE - 2 * pad_img, SLOT_SIDE - 2 * pad_img)
                surf_item = pygame.transform.smoothscale(img, target)

                px = slot_r.centerx - surf_item.get_width() // 2
                py = slot_r.centery - surf_item.get_height() // 2

                arrastaveis_build.append(
                    Arrastavel(
                        surf_item,
                        (px, py),
                        dados=item,
                        interno=True,
                        funcao_execucao=None
                    )
                )

        # ======= Atualização/desenho dos arrastáveis =======
        mouse_pos = pygame.mouse.get_pos()
        for arr in arrastaveis_build:
            arr.atualizar(eventos)
            arr.arrastar(mouse_pos)

        for arr in arrastaveis_build:
            if not getattr(arr, "esta_arrastando", False):
                arr.desenhar(tela)
        for arr in arrastaveis_build:
            if getattr(arr, "esta_arrastando", False):
                arr.desenhar(tela)

    def _desenhar_barras():
        cores_barras = PALETA["barras"]

        largura_barra = 30
        altura_maxima = 250
        espacamento_horizontal = 75

        margem_inferior = 50
        margem_superior = 60

        valores_ajustados = []
        for attr, _ in atributos:
            v = pokemon.get(attr, 0)
            if attr == "Vida":
                v /= 2
            elif attr == "EnR":
                v *= 2
            elif attr in ("CrD", "CrC"):
                v *= 1.5
            valores_ajustados.append(v)
        valor_max = max(valores_ajustados) if valores_ajustados else 1

        for i, (attr, iv_attr) in enumerate(atributos):
            cor = cores_barras[i]
            valor_atual = pokemon.get(attr, 0)
            valor_iv = pokemon.get(iv_attr, 0)

            if attr == "Vida":
                valor_para_barra = valor_atual / 2
            elif attr == "EnR":
                valor_para_barra = valor_atual * 2
            elif attr in ("CrD", "CrC"):
                valor_para_barra = valor_atual * 1.5
            else:
                valor_para_barra = valor_atual

            x_barra = x0 + i * espacamento_horizontal + 30
            y_base = y0 + altura_painel - margem_inferior + 5

            Barra(
                tela,
                (x_barra, y_base - altura_maxima),
                (largura_barra, altura_maxima),
                valor_para_barra,
                valor_max,
                cor,
                estado_barra,
                attr,
                vertical=True
            )

            texto_nome = fonte_nome.render(attr, True, PALETA["texto"])
            texto_nome_rect = texto_nome.get_rect(center=(x_barra + largura_barra // 2,
                                                          y_base - altura_maxima - margem_superior + 10))
            tela.blit(texto_nome, texto_nome_rect)

            texto_valor = fonte_valor.render(str(int(valor_atual)), True, PALETA["texto"])
            texto_valor_rect = texto_valor.get_rect(center=(x_barra + largura_barra // 2,
                                                            texto_nome_rect.bottom + 10))
            tela.blit(texto_valor, texto_valor_rect)

            texto_iv = fonte_iv.render(f"IV: {int(valor_iv)}%", True, PALETA["texto"])
            texto_iv_rect = texto_iv.get_rect(center=(x_barra + largura_barra // 2, y_base + 20))
            tela.blit(texto_iv, texto_iv_rect)

    def _desenhar_blocos_informativos():
        def calcular_poder_relativo(p):
            stats_relativos = {
                "Vida": p.get("Vida", 0) / 2,
                "Atk": p.get("Atk", 0),
                "Def": p.get("Def", 0),
                "SpA": p.get("SpA", 0),
                "SpD": p.get("SpD", 0),
                "Vel": p.get("Vel", 0),
                "Mag": p.get("Mag", 0),
                "Per": p.get("Per", 0),
                "Ene": p.get("Ene", 0),
                "EnR": p.get("EnR", 0) * 2,
                "CrD": p.get("CrD", 0) * 1.5,
                "CrC": p.get("CrC", 0) * 1.5
            }
            top6 = sorted(stats_relativos.values(), reverse=True)[:6]
            return round(sum(top6) * 4)

        info_caixas = [
            ("Sinergia", pokemon.get("Sinergia", "")),
            ("Habilidades", pokemon.get("Habilidades", "")),
            ("Equipáveis", pokemon.get("Equipaveis", "")),
            ("IV", f"{pokemon.get('IV', 0)}%"),
            ("Poder", round(pokemon.get("Total", 0))),
            ("Amizade", f"{pokemon.get('Amizade', 0)}%"),
            ("Fruta Favorita", pokemon.get("Fruta Favorita", "")),
            ("Peso", pokemon.get("Peso", "")),
            ("Altura", pokemon.get("Altura", "")),
            ("Poder Relativo", calcular_poder_relativo(pokemon)),
        ]

        largura_caixa = 170
        altura_caixa = 72
        espacamento_caixa = 15

        x_base = x0 + len(atributos) * 75 + 25
        y_base = y0 + 265

        for i, (titulo, valor) in enumerate(info_caixas):
            coluna = i // 5
            linha = i % 5

            x_caixa = x_base + coluna * (largura_caixa + espacamento_caixa)
            y_caixa = y_base + linha * (altura_caixa + espacamento_caixa)

            pygame.draw.rect(tela, PALETA["caixa_info_bg"], (x_caixa, y_caixa, largura_caixa, altura_caixa))
            pygame.draw.rect(tela, PALETA["caixa_info_borda"], (x_caixa, y_caixa, largura_caixa, altura_caixa), 2)

            txt_titulo = fonte_nome.render(str(titulo), True, PALETA["texto"])
            txt_titulo_rect = txt_titulo.get_rect(center=(x_caixa + largura_caixa // 2, y_caixa + 20))
            tela.blit(txt_titulo, txt_titulo_rect)

            txt_valor = fonte_valor.render(str(valor), True, PALETA["texto"])
            txt_valor_rect = txt_valor.get_rect(center=(x_caixa + largura_caixa // 2, y_caixa + altura_caixa - 25))
            tela.blit(txt_valor, txt_valor_rect)

    # ========= CABEÇALHO (à esquerda) + TIPAGEM (à direita) =========
    _desenhar_cabecalho()
    _desenhar_tipagem()

    # ========= Linha separadora inferior (cobre cabeçalho e tipagem) =========
    pygame.draw.line(
        tela, PALETA["linha_separadora"],
        (x0, y0 + altura_cabecalho),
        (x0 + largura_painel - 1, y0 + altura_cabecalho),
        3
    )

    # ========= Painel de Moves/Memória =========
    _desenhar_moves_memoria((x0 + 350, y0 + 70))
    desenha_build((x0 + 255,  y0 + 70))
    
    if parametros.get("AtaqueSelecionado") is not None:
        atk = parametros["AtaqueSelecionado"]
        nome_atk = atk.get("Ataque") or atk.get("nome") or atk.get("Nome") or ""

        surf = PAINEL_ATAQUE_CACHE.get(nome_atk)
        if surf is None:
            # gera 1x a surface do painel e guarda
            surf = CriarSurfacePainelAtaque(atk, tamanho=(360, 180))
            PAINEL_ATAQUE_CACHE[nome_atk] = surf

        tela.blit(surf, (x0 + 920, y0 + 75))

    _desenhar_barras()
    _desenhar_blocos_informativos()
    _desenhar_animacao()

    # ========= Borda externa do painel =========
    pygame.draw.rect(tela, PALETA["borda_painel"], (x0, y0, largura_painel, altura_painel), width=4)

# --- coloque no topo do módulo (fora de funções) ---
_mini_arrastaveis = []
_mini_areas_pokemons = []
_mini_areas_time = []
_mini_pokemons_cache = None
_mini_time0_cache = None

_mini_rect_pokemons = None
_mini_rect_time = None

idxP = 0
idxT = 0

def PainelPokemonAuxiliar(tela, pos, player, eventos, parametros):

    def executar_pokemon(arr):

        interno = arr.interno
        pos = arr.pos
        dados = arr.dados
        timeOrigem = arr.infoExtra1

        if interno:
            for i, area in enumerate(_mini_areas_pokemons):
                if area.collidepoint(pos):
                    origem = player.Pokemons.index(dados)
                    if player.Pokemons[origem] == player.Pokemons[i + idxP]:
                        return False
                    else:
                        player.Pokemons[origem], player.Pokemons[i + idxP] = player.Pokemons[i + idxP], player.Pokemons[origem]
                        return True
                    
            for i, area in enumerate(_mini_areas_time):
                if area.collidepoint(pos):
                    origem = player.Pokemons.index(dados)
                    time = idxT
                    if dados in player.Equipes[time]:
                        return False
                    else:
                        player.Equipes[time][i - (time * 6)] = player.Pokemons[origem]
                        pokemons_cache = []
                        return True
            return False
        
        else:
            for i, area in enumerate(_mini_areas_time):
                if area.collidepoint(pos):
                    origem = player.Equipes[timeOrigem].index(dados)
                    timeAlvo = idxT
                    if player.Equipes[timeOrigem][origem] == player.Equipes[timeAlvo][i - (timeAlvo * 6)]:
                        return False
                    else:
                        if timeAlvo != timeOrigem:
                            if dados in player.Equipes[timeAlvo]:
                                return False
                        player.Equipes[timeOrigem][origem], player.Equipes[timeAlvo][i - (timeAlvo * 6)] = player.Equipes[timeAlvo][i - (timeAlvo * 6)], player.Equipes[timeOrigem][origem]
                        pokemons_cache = []
                        return True
            
            origem = player.Equipes[timeOrigem].index(dados)
            player.Equipes[timeOrigem][origem] = None
            pokemons_cache = []                       

    # --- dimensões do painel mini ---
    largura = 250
    altura  = 700
    x0, y0 = pos

    # --- aparência ---
    cor_fundo = (139, 69, 19)  # marrom
    cor_borda = (0, 0, 0)

    # --- constantes do mini grid ---
    COLS = 3
    ROWS = 6
    PADDING = 10
    ESPACO  = 10

    # Calcula tamanho do slot para caber na largura disponível (você já fixou 70)
    TAMANHO_SLOT = 70

    # área Time 1 (3x2)
    TEAM_COLS = 3
    TEAM_ROWS = 2

    # ------------------------------------------------------------------
    # [NOVO] Não desenhar fundo geral. Vamos separar em 2 áreas com borda
    # ------------------------------------------------------------------

    # --- imagens dos slots (opcional, se tiver "fundos") ---
    fundo_slot_img = None
    try:
        fundo_slot_img = pygame.transform.scale(fundos["FundoSlots"], (TAMANHO_SLOT, TAMANHO_SLOT))
    except Exception:
        pass  # se não houver, desenhamos um retângulo simples

    # --- limpar áreas de colisão (sempre antes de redesenhar) ---
    _mini_areas_pokemons.clear()
    _mini_areas_time.clear()

    # =======================
    # 1) GRID 3x6 (topo)
    # =======================
    pos_grid_x = x0 + PADDING
    pos_grid_y = y0 + PADDING

    qtd_grid = min(len(player.Pokemons), COLS * ROWS)
    # quantas linhas realmente visíveis (pode ser < ROWS)
    linhas_visiveis = max(1, (qtd_grid + COLS - 1) // COLS)

    grid_w = COLS * TAMANHO_SLOT + (COLS - 1) * ESPACO
    grid_h = linhas_visiveis * TAMANHO_SLOT + (linhas_visiveis - 1) * ESPACO

    # [NOVO] fundo e borda da ÁREA DE POKÉMONS
    padding_area = 8
    grid_rect = pygame.Rect(
        pos_grid_x - padding_area,
        pos_grid_y - padding_area,
        grid_w + 2 * padding_area,
        grid_h + 2 * padding_area
    )
    pygame.draw.rect(tela, cor_fundo, grid_rect, border_radius=6)
    pygame.draw.rect(tela, cor_borda, grid_rect, width=2, border_radius=6)

    # salvar o rect para uso posterior
    global _mini_rect_pokemons, idxP, idxT
    _mini_rect_pokemons = grid_rect

    pokes_grid, idxP = Scrolavel(_mini_rect_pokemons,eventos,player.Pokemons,True,18,indice_atual=idxP,sensibilidade=3,loop=False)

    # desenhar slots do grid
    for idx in range(qtd_grid):
        c = idx % COLS
        r = idx // COLS
        x = pos_grid_x + c * (TAMANHO_SLOT + ESPACO)
        y = pos_grid_y + r * (TAMANHO_SLOT + ESPACO)
        rect = pygame.Rect(x, y, TAMANHO_SLOT, TAMANHO_SLOT)
        _mini_areas_pokemons.append(rect)

        if fundo_slot_img:
            tela.blit(fundo_slot_img, rect.topleft)
        else:
            pygame.draw.rect(tela, (160, 82, 45), rect, border_radius=4)
            pygame.draw.rect(tela, cor_borda, rect, width=1, border_radius=4)

        # botão invisível (se existir) para seleção rápida
        poke = pokes_grid[idx]
        if poke:
            Botao_invisivel((x, y, TAMANHO_SLOT, TAMANHO_SLOT),
                            lambda p=poke: parametros.update({"PokemonSelecionado": p}),
                            clique_duplo=True)
    
    BarraMovel(tela, (grid_rect.right + 4, grid_rect.y, 6, 1), player.Pokemons, idxP, tamanho=grid_rect.height, orientacao="vertical")

    # =======================
    # 2) ÁREA DO TIME 1 (3x2)
    # =======================
    # topo do time fica logo abaixo da área do grid, com um espaçamento
    espacamento_entre_areas = 40
    pos_team_x = x0 + PADDING
    pos_team_y = grid_rect.bottom + espacamento_entre_areas  # topo dos slots do time

    # título "Time 1"
    fonte_titulo = fontes[16]
    titulo_surface = fonte_titulo.render(f"Time {idxT + 1}", True, (255, 255, 255)) if fonte_titulo else None
    titulo_h = titulo_surface.get_height() if titulo_surface else 18
    titulo_gap = 4  # espaço entre o título e os slots

    team_w = TEAM_COLS * TAMANHO_SLOT + (TEAM_COLS - 1) * ESPACO
    team_h = TEAM_ROWS * TAMANHO_SLOT + (TEAM_ROWS - 1) * ESPACO

    # [NOVO] fundo e borda da ÁREA DO TIME (inclui o título)
    team_rect = pygame.Rect(
        pos_team_x - padding_area,
        pos_team_y - (titulo_h + titulo_gap) - padding_area,
        team_w + 2 * padding_area,
        (titulo_h + titulo_gap) + team_h + 2 * padding_area
    )
    pygame.draw.rect(tela, cor_fundo, team_rect, border_radius=6)
    pygame.draw.rect(tela, cor_borda, team_rect, width=2, border_radius=6)

    # salvar o rect para uso posterior
    global _mini_rect_time
    _mini_rect_time = team_rect

    equipe0, idxT = Scrolavel(_mini_rect_time,eventos,player.Equipes,indice_atual=idxT)

    # desenhar título dentro da área do time
    if titulo_surface:
        tela.blit(titulo_surface, (pos_team_x, team_rect.top + padding_area))

    # alinhar o topo dos slots logo após o título
    pos_slots_time_y = (team_rect.top + padding_area) + titulo_h + titulo_gap

    # desenhar 3x2 slots
    for r in range(TEAM_ROWS):
        for c in range(TEAM_COLS):
            x = pos_team_x + c * (TAMANHO_SLOT + ESPACO)
            y = pos_slots_time_y + r * (TAMANHO_SLOT + ESPACO)
            rect = pygame.Rect(x, y, TAMANHO_SLOT, TAMANHO_SLOT)
            _mini_areas_time.append(rect)
            if fundo_slot_img:
                tela.blit(fundo_slot_img, rect.topleft)
            else:
                pygame.draw.rect(tela, (160, 82, 45), rect, border_radius=4)
                pygame.draw.rect(tela, cor_borda, rect, width=1, border_radius=4)

    # =======================
    # 3) (Re)criar arrastáveis SÓ quando mudar
    # =======================
    global _mini_arrastaveis, _mini_pokemons_cache, _mini_time0_cache

    # detecta mudanças
    if _mini_pokemons_cache != pokes_grid or _mini_time0_cache != equipe0:
        _mini_pokemons_cache = list(pokes_grid)
        _mini_time0_cache = list(equipe0)
        _mini_arrastaveis.clear()

        # a) arrastáveis da grade 3x6
        for idx, poke in enumerate(pokes_grid):
            if not poke:
                continue
            c = idx % COLS
            r = idx // COLS
            x = pos_grid_x + c * (TAMANHO_SLOT + ESPACO)
            y = pos_grid_y + r * (TAMANHO_SLOT + ESPACO)

            nome = poke.get("Nome", "").lower()
            img = pokemons.get(nome)
            if img:
                img_adj = pygame.transform.scale(img, (TAMANHO_SLOT + 2, TAMANHO_SLOT + 2))
                arr = Arrastavel(
                    img_adj,
                    (x - 1, y - 1),
                    dados=poke,
                    interno=True,
                    funcao_execucao=executar_pokemon
                )
                _mini_arrastaveis.append(arr)

        # b) arrastáveis do Time 1 (3x2), infoExtra1=0 para indicar o time
        for slot_idx, poke in enumerate(equipe0):
            if not poke:
                continue
            c = slot_idx % TEAM_COLS
            r = slot_idx // TEAM_COLS
            x = pos_team_x + c * (TAMANHO_SLOT + ESPACO)
            y = pos_slots_time_y + r * (TAMANHO_SLOT + ESPACO)

            nome = poke.get("Nome", "").lower()
            img = pokemons.get(nome)
            if img:
                img_adj = pygame.transform.scale(img, (TAMANHO_SLOT + 2, TAMANHO_SLOT + 2))
                arr = Arrastavel(
                    img_adj,
                    (x - 1, y - 1),
                    dados=poke,
                    interno=False,
                    infoExtra1=idxT,
                    funcao_execucao=executar_pokemon
                )
                _mini_arrastaveis.append(arr)

    # =======================
    # 4) Atualizar e desenhar arrastáveis (igual)
    # =======================
    for arr in _mini_arrastaveis:
        arr.atualizar(eventos)
        arr.arrastar(pygame.mouse.get_pos())

    for arr in _mini_arrastaveis:
        if not getattr(arr, "esta_arrastando", False):
            arr.desenhar(tela)
    for arr in _mini_arrastaveis:
        if getattr(arr, "esta_arrastando", False):
            arr.desenhar(tela)

def PainelPlayer(tela, pos, player, eventos, parametros):
    # ---------------- Layout base ----------------
    x, y = pos
    largura = 1570
    altura = 450
    rect_painel = pygame.Rect(x, y, largura, altura)

    # Paleta básica
    cor_borda = (50, 50, 60)
    cor_fundo = (18, 18, 22)
    cor_div = (72, 72, 84)
    cor_texto = (235, 235, 235)
    cor_texto_suave = (180, 180, 190)

    # Fundo do painel
    pygame.draw.rect(tela, cor_fundo, rect_painel, border_radius=16)
    pygame.draw.rect(tela, cor_borda, rect_painel, width=2, border_radius=16)

    # Fontes
    font = fontes[20]
    font_titulo = fontes[25]

    # ---------------- Helpers ----------------
    def draw_kv(label, valor, x0, y0):
        tela.blit(font.render(str(label), True, cor_texto_suave), (x0, y0))
        tela.blit(font_titulo.render(str(valor), True, cor_texto), (x0, y0 + 22))

    def seconds_to_hhmmss(seg):
        try:
            seg = int(seg)
        except:
            seg = 0
        h = seg // 3600
        m = (seg % 3600) // 60
        s = seg % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def maior_poder_pokemon(pokes):
        maior = 0
        for p in pokes:
            if not p:
                continue
            try:
                tot = p.get("Total", 0)
            except:
                try:
                    tot = getattr(p, "Total", 0)
                except:
                    tot = 0
            if tot > maior:
                maior = tot
        return round(maior)

    def maior_poder_time(equipes):
        maior = 0
        for team in (equipes or []):
            soma = 0
            for p in (team or []):
                if not p:
                    continue
                try:
                    soma += p.get("Total", 0)
                except:
                    try:
                        soma += getattr(p, "Total", 0)
                    except:
                        soma += 0
            if soma > maior:
                maior = soma
        return round(maior)

    def draw_pill(surface, rect, base_color, alpha, label, val, big=False,
              *, xp=None, nivel_for_xp=None, estado_barra=None, chave_xp="xp_nivel"):
        # rect: pygame.Rect; base_color: (r,g,b); alpha: 0..255
        pill_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # fundo semitransparente
        r, g, b = base_color
        pygame.draw.rect(
            pill_surf, (r, g, b, max(0, min(255, alpha))),
            pygame.Rect(0, 0, rect.width, rect.height), border_radius=rect.height // 2
        )

        # texto principal
        texto = f"{label}: {val}"
        f_lab = fontes[20] if big else font
        txt_surf = f_lab.render(texto, True, (255, 255, 255))
        txt_x = 12
        txt_y = (rect.height - txt_surf.get_height()) // 2
        pill_surf.blit(txt_surf, (txt_x, txt_y))

        # --- barra de XP ao lado do texto (opcional) ---
        if (xp is not None) and (nivel_for_xp is not None) and (estado_barra is not None):
            # caso seja nível máximo
            if int(nivel_for_xp) >= 15:
                needed = 1  # evita divisão por zero
                xp_val = 1  # barra cheia
                mostrar_texto = "Nível Máximo"
            else:
                needed = 100 + int(nivel_for_xp) * 20
                xp_val = float(xp)
                mostrar_texto = f"XP: {int(xp)}/{needed}"

            # barra ao lado do texto:
            margem_h   = 12
            espaco     = 10  # gap entre texto e barra
            bar_x      = txt_x + txt_surf.get_width() + espaco
            bar_h      = max(10, rect.height // 6)
            bar_y      = (rect.height - bar_h) // 2 + 8
            bar_w      = max(20, rect.width - margem_h - bar_x)

            if bar_x + bar_w > rect.width - margem_h:
                bar_w = max(20, (rect.width - margem_h) - bar_x)

            # texto de xp levemente acima da barra
            mini_font = fontes[14]
            mini_surf = mini_font.render(mostrar_texto, True, (255, 255, 255))
            mini_x = bar_x
            mini_y = max(0, bar_y - mini_surf.get_height() - 2)
            pill_surf.blit(mini_surf, (mini_x, mini_y))

            # cor da barra
            cor_barra = (80, 200, 120)

            # desenha a barra (horizontal) ao lado do texto
            Barra(
                pill_surf,
                (bar_x, bar_y),
                (bar_w, bar_h),
                xp_val,
                needed,
                cor_barra,
                estado_barra,
                chave_xp,
                vertical=False
            )

        # desenha a pílula pronta na tela
        surface.blit(pill_surf, rect.topleft)

    # ---------------- Esquerda: informações em TRÊS colunas ----------------
    padding = 20
    col_w = 280   # largura de cada coluna (ajustada para caber 3 colunas)
    gap_colunas = 24
    top_info = y + padding + 10

    col1_x = x + padding
    col2_x = col1_x + col_w + gap_colunas
    col3_x = col2_x + col_w + gap_colunas

    tela.blit(font_titulo.render("Perfil do Jogador", True, cor_texto), (col1_x, y + padding))

    # Dados do jogador (com defaults seguros)
    nome = getattr(player, "Nome", getattr(player, "name", "Jogador"))
    pokes_capt = getattr(player, "PokemonsCapturados", 0)
    total_pokes = len([p for p in player.Pokemons if p is not None]) 
    total_itens = getattr(player, "Itens", [])
    baus_abertos = getattr(player, "BausAbertos", 0)
    maior_poke = maior_poder_pokemon(getattr(player, "Pokemons", []))
    maior_time = maior_poder_time(getattr(player, "Equipes", []))
    tempo_jogo = seconds_to_hhmmss(getattr(player, "TempoDeJogo", 0))
    passos = round(getattr(player, "Passos", 0))

    # Três colunas, quatro linhas cada (preenche na ordem pedida)
    linha_h = 65
    base_y = top_info + 35

    # Coluna 1
    draw_kv("Nome do Jogador", nome, col1_x, base_y + 0 * linha_h)
    # Coluna 3 (reservada para crescer; mantemos 4 linhas para padronização visual)
    draw_kv("Vitórias (Total)", getattr(player, "BatalhasVencidasPVP", 0) + getattr(player, "BatalhasVencidasBOT", 0),
            col1_x, base_y + 1 * linha_h)
    draw_kv("Vitórias vs Jogadores", getattr(player, "BatalhasVencidasPVP", 0),
            col1_x, base_y + 2 * linha_h)
    draw_kv("Vitórias vs BOT", getattr(player, "BatalhasVencidasBOT", 0),
            col1_x, base_y + 3 * linha_h)

    draw_kv("Numero de Pokémons", total_pokes, col2_x, base_y + 0 * linha_h)
    draw_kv("Numero de Itens", total_itens, col2_x, base_y + 1 * linha_h)
    draw_kv("Pokémons Capturados", pokes_capt, col2_x, base_y + 2 * linha_h)
    draw_kv("Baús Abertos", baus_abertos, col2_x, base_y + 3 * linha_h)

    draw_kv("Maior poder Pokémon", maior_poke, col3_x, base_y + 0 * linha_h)
    draw_kv("Maior poder Time", maior_time, col3_x, base_y + 1 * linha_h)
    draw_kv("Tempo de Jogo", tempo_jogo, col3_x, base_y + 2 * linha_h)
    draw_kv("Passos", passos, col3_x, base_y + 3 * linha_h)

    # ---------------- Direita: área do player ----------------
    area_player_w = 430
    area_player_h = 350
    area_player_x = x + largura - area_player_w - padding
    area_player_y = y + padding

    largura_quadrado = area_player_w
    altura_quadrado = area_player_h
    x_quadrado = area_player_x
    y_quadrado = area_player_y

    if "FundoQuadradoNeutro" in fundos:
        imagem_quadrado = pygame.transform.scale(
            fundos["FundoQuadradoNeutro"], (largura_quadrado, altura_quadrado)
        )
        tela.blit(imagem_quadrado, (x_quadrado, y_quadrado))
    else:
        pygame.draw.rect(
            tela, (26, 26, 30),
            pygame.Rect(x_quadrado, y_quadrado, largura_quadrado, altura_quadrado),
            border_radius=12
        )
        pygame.draw.rect(
            tela, cor_div,
            pygame.Rect(x_quadrado, y_quadrado, largura_quadrado, altura_quadrado),
            width=2, border_radius=12
        )

    # ---------------- Pílulas (à ESQUERDA do fundo do player, grudadas) ----------------
    # Cores base
    COR_ROXO = (138, 43, 226)   # Nivel
    COR_VERM = (220, 20, 60)    # Maestria
    COR_AZUL = (30, 144, 255)   # Velocidade
    COR_AMAR = (255, 215, 0)    # Mochila
    COR_ALERTA = (40, 200, 120) # Verde atenção

    nivel = getattr(player, "Nivel", 0)
    maestria = getattr(player, "Maestria", 0)
    velocidade = getattr(player, "Velocidade", 0)
    mochila = getattr(player, "Mochila", 0)

    soma_sec = (maestria or 0) + (velocidade or 0) + (mochila or 0)
    mismatch = (soma_sec != (nivel or 0))

    # Alpha base das pílulas
    alpha_base = 150
    # Alpha pulsante (para alerta)
    t = pygame.time.get_ticks() / 1000.0
    alpha_pulse = int(100 + 80 * (0.5 + 0.5 * math.sin(2.2 * t)))  # ~100..180

    # Dimensões e posicionamento: empilhadas, a direita das pílulas encosta no x_quadrado
    pill_gap = 12
    pill_h = 50
    # Larguras decrescentes (a 1ª é a maior)
    w1, w2, w3, w4 = 240, 180, 180, 180

    # Topo para centralizar verticalmente na área do player
    start_y = y_quadrado + 5

    # Cada pílula encosta o lado direito no x_quadrado - 6 (um leve afastamento)
    right_edge = x_quadrado - 6

    # 1) Nível (maior)
    r1 = pygame.Rect(right_edge - w1, start_y + 0 * (pill_h + pill_gap), w1, pill_h)
    draw_pill(
        tela, r1, COR_ROXO, alpha_base,
        "Nível", nivel, big=True,
        xp=player.Xp,                     # XP atual do jogador
        nivel_for_xp=nivel,              # nível atual para calcular o necessário
        estado_barra={},   # dicionário persistente p/ animação suave
        chave_xp="xp_nivel"              # chave única desta barra
    )

    # 2) Maestria
    color2 = COR_ALERTA if mismatch else COR_VERM
    alpha2 = alpha_pulse if mismatch else alpha_base
    r2 = pygame.Rect(right_edge - w2, start_y + 1 * (pill_h + pill_gap), w2, pill_h)
    draw_pill(tela, r2, color2, alpha2, "Maestria", maestria)
    if mismatch:
        Botao_invisivel((r2.x, r2.y, r2.w, r2.h),
            lambda: setattr(player, "Maestria", getattr(player, "Maestria") + 1)
        )

    # 3) Velocidade
    color3 = COR_ALERTA if mismatch else COR_AZUL
    alpha3 = alpha_pulse if mismatch else alpha_base
    r3 = pygame.Rect(right_edge - w3, start_y + 2 * (pill_h + pill_gap), w3, pill_h)
    draw_pill(tela, r3, color3, alpha3, "Velocidade", velocidade)
    if mismatch:
        Botao_invisivel((r3.x, r3.y, r3.w, r3.h),
            lambda: setattr(player, "Velocidade", getattr(player, "Velocidade") + 1)
        )

    # 4) Mochila
    color4 = COR_ALERTA if mismatch else COR_AMAR
    alpha4 = alpha_pulse if mismatch else alpha_base
    r4 = pygame.Rect(right_edge - w4, start_y + 3 * (pill_h + pill_gap), w4, pill_h)
    draw_pill(tela, r4, color4, alpha4, "Mochila", mochila)
    if mismatch:
        Botao_invisivel((r4.x, r4.y, r4.w, r4.h),
            lambda: setattr(player, "Mochila", getattr(player, "Mochila") + 1)
        )

    # ---------------- Slider de Skin (inferior) ----------------
    slider_x = x + padding
    slider_y = y + altura - 30
    slider_w = largura - 2 * padding

    NovoNumero = (player.SkinsLiberadas.index(player.SkinNumero) + 1)
    NovoNumero = Slider(
        tela, "Skin", slider_x, slider_y, slider_w,
        NovoNumero, 1, max(0, len(getattr(player, "SkinsLiberadas", []))),
        (180, 180, 180), (255, 255, 255), eventos,
        "", Mostrar=False)

    if NovoNumero != player.SkinNumero:
        player.SkinNumero = round(NovoNumero)
        player.Skin = outros["SkinsTodas"][player.SkinNumero]
        player.SkinRedimensionada = pygame.transform.scale(player.Skin, (83, 66))

    tela.blit(font.render("Use o slider para trocar a skin do jogador", True, cor_texto_suave),
              (slider_x, slider_y - 45))

    # ---------------- Desenhar o player (canto direito superior) ----------------
    centro_x = x_quadrado + largura_quadrado / 2
    centro_y = y_quadrado + altura_quadrado / 2
    DesenharPlayer(tela, player.Skin, (centro_x, centro_y))

def CriarSurfacePainelAtaque(ataque, tamanho=(360, 180)):

    # ================== VARIÁVEIS DE EDIÇÃO ==================
    W, H = tamanho
    RADIUS_BG = 12

    # Cores
    COR_FUNDO_GERAL   = (40, 40, 40)
    COR_DIVISOR       = (0, 0, 0)            # << linhas pretas, sem alpha
    COR_TEXTO         = (230, 230, 230)
    COR_TEXTO_CLARO   = (245, 245, 245)
    COR_INFO_BG       = (55, 55, 55)
    COR_CIRCULO_TIPO  = (255, 255, 255)
    OVERLAY_ALPHA     = 60                   # overlay do header (apenas dentro da forma)

    # Estilo → cor do texto no rodapé
    COR_ESTILO = {"Normal": (255,165,0), "Especial": (160,80,255), "Status": (220,60,60)}

    # Layout
    HEADER_H, FOOTER_H = 40, 24
    P_IN, GAP_X, DIVISOR_H = 10, 10, 1

    # Ícone de tipo/infos
    TAM_ICONE_TIPO, CIRC_INC = 26, 1
    INFO_BOX_W, INFO_BOX_H, INFO_BOX_RADIUS = 75, 27, 8
    INFO_BOX_GAP, INFO_ICON_SIZE, INFO_TXT_OFFSET_X = 5, 18, 6

    # Tipografia (índices na lista global 'fontes')
    FONT_NOME_IDX, FONT_DESC_IDX, FONT_INFO_IDX, FONT_FOOTER_IDX = 18, 14, 14, 14

    # ================== DADOS ==================
    nome  = ataque.get("Ataque") or ataque.get("nome") or ataque.get("Nome") or "—"
    tipo  = ataque.get("Tipo")   or ataque.get("tipo")  or "normal"
    desc  = ataque.get("descrição") or ataque.get("Descrição") or ""
    dano  = ataque.get("Dano", ataque.get("dano", 0))
    custo = ataque.get("Custo", ataque.get("custo", 0))
    asser = ataque.get("Assertividade", ataque.get("assertividade", "—"))
    alvo  = ataque.get("Alvo", ataque.get("alvo", "-"))
    estilo_raw = (ataque.get("Estilo") or ataque.get("estilo") or "n").lower()
    estilo = {"s": "Status", "e": "Especial", "n": "Normal"}.get(estilo_raw, estilo_raw.capitalize())

    # normalizações
    dano_show  = str(int(round(float(dano) * 100))) if isinstance(dano,(int,float)) else str(dano)
    custo_show = str(int(round(float(custo)))) if isinstance(custo,(int,float)) else str(int(round(float(str(custo)))))
    asser_show = asser if (isinstance(asser,str) and asser.strip().endswith("%")) else f"{int(round(float(asser)))}%"

    # Fontes
    fonte_nome   = fontes[FONT_NOME_IDX]
    fonte_desc   = fontes[FONT_DESC_IDX]
    fonte_info   = fontes[FONT_INFO_IDX]
    fonte_footer = fontes[FONT_FOOTER_IDX]

    # Retângulos base (origem local 0,0)
    x0, y0 = 0, 0
    card_rect   = pygame.Rect(x0, y0, W, H)
    header_rect = pygame.Rect(x0, y0, W, HEADER_H)
    body_rect   = pygame.Rect(x0, y0 + HEADER_H + DIVISOR_H, W, H - HEADER_H - DIVISOR_H - FOOTER_H)
    footer_rect = pygame.Rect(x0, y0 + H - FOOTER_H, W, FOOTER_H)

    # ================== HELPERS ==================
    def wrap_text(texto, fonte, largura):
        if not texto: return []
        palavras, linhas, atual = str(texto).split(), [], ""
        for p in palavras:
            tentativa = p if not atual else (atual + " " + p)
            if fonte.size(tentativa)[0] <= largura:
                atual = tentativa
            else:
                if atual: linhas.append(atual)
                while fonte.size(p)[0] > largura and len(p) > 1:
                    i = len(p)
                    while i > 0 and fonte.size(p[:i])[0] > largura: i -= 1
                    if i <= 0: break
                    linhas.append(p[:i]); p = p[i:]
                atual = p
        if atual: linhas.append(atual)
        return linhas

    def draw_text_with_stroke(dest, text, fonte, pos_xy, color=(245,245,245), stroke=(0,0,0)):
        base = fonte.render(str(text), True, color)
        sx, sy = pos_xy
        outline = fonte.render(str(text), True, stroke)
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
            dest.blit(outline, (sx+dx, sy+dy))
        dest.blit(base, (sx, sy))

    # Cria surface final
    surf = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha()

    # Fundo arredondado do cartão
    pygame.draw.rect(surf, COR_FUNDO_GERAL, card_rect, border_radius=RADIUS_BG)

    # Header com cantos superiores ARREDONDADOS **transparentes**
    nome_textura = "Fundo" + str(tipo).capitalize()
    textura = texturas.get(nome_textura)
    if textura:
        tex_scaled = pygame.transform.smoothscale(textura, (W, HEADER_H)).convert_alpha()
    else:
        tex_scaled = pygame.Surface((W, HEADER_H), pygame.SRCALPHA); tex_scaled.fill((50,50,50))

    # Máscara da forma do header (apenas cantos superiores)
    shape = pygame.Surface((W, HEADER_H), pygame.SRCALPHA)
    pygame.draw.rect(
        shape, (255,255,255,255), shape.get_rect(),
        border_top_left_radius=RADIUS_BG, border_top_right_radius=RADIUS_BG,
        border_bottom_left_radius=0, border_bottom_right_radius=0
    )

    # Aplica a máscara para que fora da forma fique alpha=0
    masked = tex_scaled.copy()
    masked.blit(shape, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

    # Overlay escuro **apenas dentro da forma** (não toca nas quinas transparentes)
    overlay = pygame.Surface((W, HEADER_H), pygame.SRCALPHA)
    pygame.draw.rect(
        overlay, (0,0,0,OVERLAY_ALPHA), overlay.get_rect(),
        border_top_left_radius=RADIUS_BG, border_top_right_radius=RADIUS_BG,
        border_bottom_left_radius=0, border_bottom_right_radius=0
    )
    masked.blit(overlay, (0,0))  # blend normal dentro da mesma forma

    # Cola o header pronto
    surf.blit(masked, header_rect.topleft)

    # Título com “stroke” preto
    nome_pos_x = header_rect.x + P_IN
    nome_pos_y = header_rect.y + (HEADER_H - fonte_nome.get_height()) // 2
    draw_text_with_stroke(surf, str(nome), fonte_nome, (nome_pos_x, nome_pos_y),
                          color=COR_TEXTO_CLARO, stroke=(0,0,0))

    # Ícone do tipo com círculo branco
    tipo_icon = icones.get(tipo)
    if tipo_icon:
        icon_img = pygame.transform.smoothscale(tipo_icon, (TAM_ICONE_TIPO, TAM_ICONE_TIPO)).convert_alpha()
        circ_r = max(icon_img.get_width(), icon_img.get_height()) // 2 + CIRC_INC
        circle_surf = pygame.Surface((circ_r*2, circ_r*2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surf, COR_CIRCULO_TIPO, (circ_r, circ_r), circ_r)
        cx = header_rect.right - (P_IN + circ_r)
        cy = header_rect.centery
        surf.blit(circle_surf, (cx - circ_r, cy - circ_r))
        surf.blit(icon_img, (cx - icon_img.get_width()//2, cy - icon_img.get_height()//2))

    # Divisor (preto, sem alpha)
    pygame.draw.rect(surf, COR_DIVISOR, (x0, y0 + HEADER_H, W, DIVISOR_H))

    # ============ CORPO ============
    right_w = INFO_BOX_W
    right_x = body_rect.right - P_IN - right_w
    right_y = body_rect.top + P_IN

    left_x = body_rect.left + P_IN
    left_w = right_x - GAP_X - left_x
    left_y = body_rect.top + P_IN

    for linha in wrap_text(desc, fonte_desc, left_w):
        ls = fonte_desc.render(linha, True, COR_TEXTO)
        surf.blit(ls, (left_x, left_y))
        left_y += ls.get_height() + 2

    info_data = [(dano_show, "Dano"), (custo_show, "Custo"), (asser_show, "Assertividade")]
    y_box = right_y
    for valor, icon_key in info_data:
        box_rect = pygame.Rect(right_x, y_box, right_w, INFO_BOX_H)
        pygame.draw.rect(surf, COR_INFO_BG, box_rect, border_radius=INFO_BOX_RADIUS)
        icon_img = icones.get(icon_key)
        text_x = box_rect.x + P_IN
        if icon_img:
            icon_img = pygame.transform.smoothscale(icon_img, (INFO_ICON_SIZE, INFO_ICON_SIZE)).convert_alpha()
            icon_y = box_rect.y + (box_rect.height - INFO_ICON_SIZE) // 2
            surf.blit(icon_img, (box_rect.x + P_IN, icon_y))
            text_x = box_rect.x + P_IN + INFO_ICON_SIZE + INFO_TXT_OFFSET_X
        vs = fonte_info.render(str(valor), True, COR_TEXTO_CLARO)
        surf.blit(vs, (text_x, box_rect.y + (box_rect.height - vs.get_height()) // 2))
        y_box += INFO_BOX_H + INFO_BOX_GAP

    # ============ RODAPÉ ============
    pygame.draw.rect(surf, COR_DIVISOR, (x0, footer_rect.y - DIVISOR_H, W, DIVISOR_H))

    cor_estilo = COR_ESTILO.get(estilo, COR_TEXTO)
    fs_alvo   = fonte_footer.render(f"Alvo: {alvo}", True, COR_TEXTO)
    fs_estilo = fonte_footer.render(f"Estilo: {estilo}", True, cor_estilo)

    total_infos_w = fs_alvo.get_width() + fs_estilo.get_width()
    free_w = max(0, W - 2*P_IN - total_infos_w)
    space = free_w // 3

    y_base = footer_rect.y + (FOOTER_H - fs_alvo.get_height()) // 2
    x_alvo   = x0 + P_IN + space
    x_estilo = x_alvo + fs_alvo.get_width() + space

    surf.blit(fs_alvo,   (x_alvo,   y_base))
    surf.blit(fs_estilo, (x_estilo, y_base))

    return surf

ATTACK_SURF_CACHE = {}

def PainelPokemonBatalha(pokemon, tela, pos, eventos, parametros, anima):

    if pokemon == None:
        return

    # Quais chaves exibem "%" junto do valor
    PERCENT_KEYS = {"CrC", "CrD", "Vamp", "Asse"}

    # =================== VARIÁVEIS DE LAYOUT (tunáveis) ===================
    # Painel
    PANEL_W, PANEL_H   = 920, 180   # largura/altura totais do painel
    RADIUS             = 12         # raio dos cantos arredondados do fundo/borda
    BORDER_W           = 2          # espessura (px) da borda do painel
    PAD_OUTER          = 10         # margem interna geral entre borda e conteúdo

    # Setores (larguras)
    LEFT_W             = 120        # largura do setor esquerdo (nome/sprite/poder)
    ATTACK_W           = 190
    RIGHT_IN_PAD       = 5
    EXTRA_BTN_SZ       = 32   # novo: tamanho dos botões extras (quadrados)
    EXTRA_BTN_GAP      = 8    # novo: espaço entre ataques e a coluna extra
    RIGHT_W            = ATTACK_W + RIGHT_IN_PAD*2 + EXTRA_BTN_GAP + EXTRA_BTN_SZ
    ATK_SHIFT_LEFT     = 0    # <<< antes 15; reduzimos 15px da margem direita para dar +15px ao centro

    # Relação de alturas do bloco central
    CS_RATIO           = 0.56       # fração de altura do centro dedicada à parte superior
    GAP_CS_CI          = 4          # espaçamento vertical entre centro sup. e inf.

    # Margens internas por setor
    SECTOR_PAD_LEFT    = 8          # padding interno esquerdo dos setores centrais
    SECTOR_PAD_RIGHT   = 8          # padding interno direito dos setores centrais
    SECTOR_PAD_TOP     = 4          # padding interno superior dos setores centrais
    SECTOR_PAD_BOTTOM  = 4          # padding interno inferior dos setores centrais

    # Status (Central Superior)
    ICON_SZ            = 30         # tamanho (px) do ícone dos status
    STAT_NUM_SIZE      = 20         # tamanho da fonte dos números dos status
    STAT_TXT_GAP       = 6          # distância entre ícone e número do status
    STAT_ROW_GAP       = 40         # distância vertical entre as 2 linhas de cada coluna
    STAT_COL_GAP       = 13         # <<< +1 px entre colunas de status (antes 12)
    STAT_COL_GAP_EXTRA_PERCENT = 7  # <<< +2 px entre [CrC/CrD] e [Vamp/Asse] (antes 5)
    ATTR_SHIFT_LEFT    = 10         # empurra todos os atributos 10px p/ esquerda

    # Build + Barras + TIPOS (Central Inferior)
    CI_SHIFT_LEFT      = 3          # desloca TODO o central inferior para a esquerda
    BUILD_SLOTS        = 3          # quantos slots de build
    BUILD_SIZE         = 64         # tamanho (px) de cada slot da build
    BUILD_GAP          = 8          # gap entre slots da build
    BUILD_TO_BARRAS_GAP= 12         # distância entre build e bloco de barras

    BARRA_W            = 238        # <<< 250 - 12 px: barras começam 12px mais à direita
    BARRA_H            = 22         # altura das barras
    BARRA_GAP_Y        = 8          # distância vertical entre as duas barras
    BARRAS_TOP_OFFSET  = 6          # deslocamento do topo do setor até a 1ª barra

    # Coluna de TIPOS/SINERGIA (2x2: Tipo1 + Sinergia, abaixo: Tipo2 + Tipo3)
    TYPE_IN_PAD        = 4          # padding interno esquerdo da faixa de tipos
    TYPE_COL_GAP       = 6          # distância horizontal entre “células” (ícone/círculo)
    TYPE_ROW_GAP       = 6          # distância vertical entre as duas linhas
    TYPE_Y_BASE_SHIFT  = -4         # antes era +2; agora 5px mais alto => -3
    TYPE_COL_W         = ICON_SZ*2 + TYPE_COL_GAP + TYPE_IN_PAD + 6  # 2 colunas (Tipo/Sinergia)
    BARRA_TO_TYPE_GAP  = 10         # distância entre barras e faixa de tipos

    # Esquerda (nome/sprite/poder)
    LEFT_NAME_TOP_GAP    = 2
    LEFT_NAME_SPRITE_GAP = 6
    LEFT_SPRITE_MAX_H    = 80
    LEFT_SPRITE_SIDE_PAD = 10
    LEFT_SPRITE_PODER_GAP= 6
    LEFT_PODER_NUM_GAP   = 2

    # Ataques (setor direito)
    ATK_BTN_H          = 32         # altura do botão de ataque
    ATK_BTN_GAP        = 8          # distância vertical entre os botões de ataque
    ATK_Y_EXTRA_UP     = 4          # margem entre o y inicial dos ataques 4px menor
    # =====================================================================

    x0, y0 = pos
    W, H = PANEL_W, PANEL_H

    if pokemon in parametros["EquipeAliada"]:
        if pokemon["Ativo"]:
            ALIADO = True
        else:
            ALIADO = False
    else:
        ALIADO = False

    # --------- FUNDO ARREDONDADO ----------
    fundo = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(fundo, (35, 35, 35, 190), (0, 0, W, H), border_radius=RADIUS)                # fundo
    pygame.draw.rect(fundo, (255, 255, 255, 255), (1, 1, W-2, H-2), BORDER_W, border_radius=RADIUS)  # borda
    tela.blit(fundo, (x0, y0))

    # fontes
    f_nome  = fontes[20] if len(fontes) > 20 else fontes[-1]
    f_texto = fontes[16] if len(fontes) > 16 else fontes[0]
    f_mini  = fontes[14] if len(fontes) > 14 else fontes[0]
    f_num   = fontes[STAT_NUM_SIZE] if len(fontes) > STAT_NUM_SIZE else fontes[-1]

    # --------- Recortes dos setores ----------
    inner_x = x0 + PAD_OUTER
    inner_y = y0 + PAD_OUTER
    inner_w = W  - PAD_OUTER*2
    inner_h = H  - PAD_OUTER*2

    R_left  = pygame.Rect(inner_x, inner_y, LEFT_W, inner_h)
    R_right = pygame.Rect(x0 + W - PAD_OUTER - RIGHT_W - ATK_SHIFT_LEFT, inner_y, RIGHT_W, inner_h)

    mid_x   = R_left.right + PAD_OUTER
    mid_w   = (x0 + W - PAD_OUTER) - ATK_SHIFT_LEFT - RIGHT_W - (R_left.right + PAD_OUTER)
    cs_h    = int(inner_h * CS_RATIO)
    ci_h    = inner_h - cs_h - GAP_CS_CI

    R_csup  = pygame.Rect(mid_x, inner_y,                mid_w, cs_h)
    R_cinf  = pygame.Rect(mid_x, inner_y + cs_h + GAP_CS_CI, mid_w, ci_h)

    # cores
    COR_OK = (255, 255, 255)
    COR_UP = (255, 180, 90)
    COR_DN = (220, 70, 70)

    # ---------------- helpers ----------------
    def _get_val_and_color(lbl_key):
        key_map = {"EnE": "Ene"}
        k = key_map.get(lbl_key, lbl_key)
        base_k = f"{k}Base"
        if k == "Vida":
            val = pokemon.get("Vida", pokemon.get("VidaMax", 0))
        else:
            val = pokemon.get(k, 0)

        def _to_float(v):
            try:
                return float(v)
            except Exception:
                try:
                    return float(str(v).replace(",", "."))
                except Exception:
                    return 0.0

        v = _to_float(val)
        b = _to_float(pokemon.get(base_k, v))
        cor = COR_UP if v > b else (COR_DN if v < b else COR_OK)
        return (int(round(v)) if k == "Vida" else int(round(v))), cor

    def _draw_icon_value(label_key, x, y, icon_sz=ICON_SZ, font=f_num):
        # ícone/label
        icon_key = {"EnE": "Ene"}.get(label_key, label_key)
        icon = icones.get(icon_key)
        if isinstance(icon, pygame.Surface):
            if icon.get_width() != icon_sz or icon.get_height() != icon_sz:
                icon = pygame.transform.scale(icon, (icon_sz, icon_sz))
            tela.blit(icon, (x, y))
            tx = x + icon_sz + STAT_TXT_GAP
            ty = y + (icon_sz - font.get_height()) // 2
        else:
            lab = f_mini.render(label_key, True, (220, 220, 220))
            tela.blit(lab, (x, y))
            tx = x + lab.get_width() + STAT_TXT_GAP
            ty = y

        # valor + sufixo %
        val, cor = _get_val_and_color(label_key)
        txt_val = f"{val}%" if label_key in PERCENT_KEYS else str(val)
        tela.blit(font.render(txt_val, True, cor), (tx, ty))

    # ================== Setor: ESQUERDA ==================
    def setor_esquerda():
        nome_key = str(pokemon.get("Nome","???")).lower()
        sprite = pokemons.get(nome_key)
        if sprite is None:
            sprite = CarregarPokemon(nome_key, pokemons)

        # margens internas
        lw = R_left.w - (SECTOR_PAD_LEFT + SECTOR_PAD_RIGHT)

        # Nome
        nome_surf = f_nome.render(nome_key, True, (255, 255, 255))
        nx = R_left.x + (R_left.w - nome_surf.get_width()) // 2
        ny = R_left.y + SECTOR_PAD_TOP + LEFT_NAME_TOP_GAP
        tela.blit(nome_surf, (nx, ny))

        # Sprite (sem cache; scale rápido)
        sp_top = ny + nome_surf.get_height() + LEFT_NAME_SPRITE_GAP
        used_h = 0
        if isinstance(sprite, pygame.Surface):
            max_sw = lw - LEFT_SPRITE_SIDE_PAD*2
            max_sh = LEFT_SPRITE_MAX_H
            sw, sh = sprite.get_size()
            scale = min(max_sw / max(1, sw), max_sh / max(1, sh), 1.0)
            sp = pygame.transform.scale(sprite, (int(sw*scale), int(sh*scale))) if scale < 1.0 else sprite
            sp_x = R_left.x + (R_left.w - sp.get_width()) // 2
            tela.blit(sp, (sp_x, sp_top))
            used_h = sp.get_height()

        # Poder
        total_val = pokemon.get("Total")
        if total_val is None:
            stats_keys = ["Vida","Atk","Def","SpA","SpD","Vel","Mag","Per","Ene","EnR","CrD","CrC","Vamp","Asse"]
            acc = 0
            for k in stats_keys:
                if k == "Vida":
                    acc += int(pokemon.get("Vida", pokemon.get("VidaMax", 0)) or 0)
                else:
                    try:
                        acc += int(float(pokemon.get(k, 0) or 0))
                    except Exception:
                        pass
            total_val = acc

        poder_lbl = f_texto.render("Poder", True, (230, 230, 230))
        py = sp_top + used_h + LEFT_SPRITE_PODER_GAP
        px = R_left.x + (R_left.w - poder_lbl.get_width()) // 2
        tela.blit(poder_lbl, (px, py))

        num_lbl = f_nome.render(str(int(round(total_val))), True, (255, 255, 255))
        ny2 = py + poder_lbl.get_height() + LEFT_PODER_NUM_GAP
        nx2 = R_left.x + (R_left.w - num_lbl.get_width()) // 2
        tela.blit(num_lbl, (nx2, ny2))

    # ============ Setor: CENTRAL SUPERIOR (status) ============
    def setor_central_superior():
        cols = [
            ("Vida", "Mag"),
            ("Atk",  "SpA"),
            ("Def",  "SpD"),
            ("Per",  "Vel"),
            ("EnE",  "EnR"),
            ("CrC",  "CrD"),
            ("Vamp", "Asse"),
        ]
        rx = R_csup.x + SECTOR_PAD_LEFT - ATTR_SHIFT_LEFT  # empurra 10px p/ esquerda
        ry = R_csup.y + SECTOR_PAD_TOP
        rw = R_csup.w - (SECTOR_PAD_LEFT + SECTOR_PAD_RIGHT)

        ncols = len(cols)
        # inclua o gap extra entre a col 5 (CrC/CrD) e 6 (Vamp/Asse)
        total_gaps = STAT_COL_GAP * (ncols - 1) + STAT_COL_GAP_EXTRA_PERCENT
        col_w = max(1, (rw - total_gaps) // ncols)
        top_y = ry

        # índice da coluna de Vamp/Asse (0-based)
        vamp_col_idx = 6
        for c, (k1, k2) in enumerate(cols):
            # offset adicional para colunas após o gap extra
            extra = STAT_COL_GAP_EXTRA_PERCENT if c >= vamp_col_idx else 0
            cx = rx + c*(col_w + STAT_COL_GAP) + extra
            _draw_icon_value(k1, cx, top_y, ICON_SZ, f_num)
            _draw_icon_value(k2, cx, top_y + STAT_ROW_GAP, ICON_SZ, f_num)

    # ===== Setor: CENTRAL INFERIOR (build + barras + TIPOS/SINERGIA) =====
    def setor_central_inferior():
        rx_base = R_cinf.x + SECTOR_PAD_LEFT
        rx = rx_base - CI_SHIFT_LEFT
        ry = R_cinf.y + SECTOR_PAD_TOP
        rw = R_cinf.w - (SECTOR_PAD_LEFT + SECTOR_PAD_RIGHT)
        rh = R_cinf.h - (SECTOR_PAD_TOP + SECTOR_PAD_BOTTOM)

        # Faixa de tipos/sinergia à direita (2 colunas)
        R_types = pygame.Rect(rx + rw - TYPE_COL_W, ry, TYPE_COL_W, rh)

        # --- BARRAS à esquerda da faixa de tipos ---
        vida_atual = int(pokemon.get("Vida", 0) or 0)
        vida_max   = int(pokemon.get("VidaMax", pokemon.get("Vida", 1)) or 1)
        ene_atual  = int(pokemon.get("Energia", pokemon.get("EneAtual", 0)) or 0)
        ene_max    = int(pokemon.get("Ene", 1) or 1)
        estado_barras = pokemon.setdefault("_estado_barras", {})

        # novas variações
        barreira = int(pokemon.get("Barreira", 0) or 0)                  # pode ser 0+
        custo_ene = int(parametros.get("CustoAtualEnergia", 0) or 0)     # custo sempre tratado como desgaste

        # posições das barras (vida em cima, energia embaixo)
        bx = R_types.left - BARRA_TO_TYPE_GAP - BARRA_W
        by1 = ry + BARRAS_TOP_OFFSET
        by2 = by1 + BARRA_H + BARRA_GAP_Y

        # VIDA: variacao = +barreira (overlay branco)
        Barra(
            tela, (bx, by1), (BARRA_W, BARRA_H),
            valor_atual=vida_atual, valor_maximo=vida_max,
            cor=(190, 60, 60), estado_barra=estado_barras,
            chave=f"vida_{pokemon.get('Nome','')}",
            vertical=False, variacao=max(0, barreira)
        )
        # exibição inclui a barreira (ex.: 115/100)
        tv_val = vida_atual + max(0, barreira)
        tv = f_mini.render(f"{tv_val}/{vida_max}", True, (255, 255, 255))
        tela.blit(tv, (bx + (BARRA_W - tv.get_width()) // 2, by1 + (BARRA_H - tv.get_height()) // 2))

        # ENERGIA: variacao = -custo (desgaste -> pisca branco/vermelho)
        if ALIADO:
            vari_ene = -abs(custo_ene)
        else: 
            vari_ene = 0
        Barra(
            tela, (bx, by2), (BARRA_W, BARRA_H),
            valor_atual=ene_atual, valor_maximo=ene_max,
            cor=(60, 120, 200), estado_barra=estado_barras,
            chave=f"ene_{pokemon.get('Nome','')}",
            vertical=False, variacao=vari_ene
        )
        # exibição considera o custo (ex.: 30-10 -> 20/ene_max)
        te_val = ene_atual + vari_ene  # vari_ene é negativo quando há custo
        te = f_mini.render(f"{te_val}/{ene_max}", True, (255, 255, 255))
        tela.blit(te, (bx + (BARRA_W - te.get_width()) // 2, by2 + (BARRA_H - te.get_height()) // 2))

        # --- BUILD à esquerda das barras ---
        start_x_right = bx - BUILD_TO_BARRAS_GAP
        x = start_x_right - BUILD_SIZE
        y = ry + max(0, (rh - BUILD_SIZE)//2)

        build_items = (pokemon.get("Build") or [])[:BUILD_SLOTS]
        for i in range(BUILD_SLOTS):
            item = build_items[i] if i < len(build_items) and build_items[i] else None
            nome_item = (str(item.get("Nome", "")).strip() if isinstance(item, dict) else "")
            surf_item = equipaveis.get(nome_item) if nome_item else None
            if not isinstance(surf_item, pygame.Surface):
                # placeholder simples sem cache
                surf_item = pygame.Surface((BUILD_SIZE, BUILD_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(surf_item, (255,255,255,28), (0,0,BUILD_SIZE,BUILD_SIZE), border_radius=8)
                if nome_item:
                    txt = f_mini.render(nome_item, True, (230,230,230))
                    surf_item.blit(txt, ((BUILD_SIZE - txt.get_width())//2, (BUILD_SIZE - txt.get_height())//2))

            Botao_Selecao(
                tela, "", (x, y, BUILD_SIZE, BUILD_SIZE), f_mini,
                surf_item, (200,200,200),
                id_botao=f"build_{i}_{pokemon.get('Nome','')}",
                estado_global=parametros["EstadoBotoesPainelPokemonBatalha"], eventos=eventos,
                cor_borda_esquerda=(120,220,120), cor_borda_direita=(220,120,120),
                cor_passagem=(230,230,230),
                branco=True, Surface=False, grossura=2,
                funcao_esquerdo=[lambda: parametros.update({"AtaqueAliadoSelecionado": None, "AtaqueInimigoSelecionado": None, "ItemSelecionado": item, "ModoAlvificando": False, "CustoAtualEnergia": 0}), lambda: anima.update({"Y5": 1080, "Y6": 900, "_anima_painel_conteudo": pygame.time.get_ticks()})],
                desfazer_esquerdo=[lambda: parametros.update({"AtaqueAliadoSelecionado": None, "AtaqueInimigoSelecionado": None, "ItemSelecionado": None, "ModoAlvificando": False, "CustoAtualEnergia": 0}),  lambda: anima.update({"Y5": 900, "Y6": 1080, "_anima_painel_conteudo": pygame.time.get_ticks()})]
            )
            x -= (BUILD_SIZE + BUILD_GAP)

        # --- TIPOS + SINERGIA (grade 2x2) ---
        def _valido(t):
            if t is None: return False
            s = str(t).strip()
            if not s: return False
            return s.lower() not in ("nan","none","null")

        t1 = pokemon.get("Tipo1"); t1 = t1 if _valido(t1) else None
        t2 = pokemon.get("Tipo2"); t2 = t2 if _valido(t2) else None
        t3 = pokemon.get("Tipo3"); t3 = t3 if _valido(t3) else None

        # sinergia (número)
        def _get_sinergia():
            cand = pokemon.get("Sinergia")
            try:
                if str(cand).lower() in ("nan","none","null",""): return 0
            except Exception:
                pass
            try: return int(round(float(cand)))
            except Exception: return 0
        sin_val = _get_sinergia()

        tx0 = R_types.x + TYPE_IN_PAD
        ty0 = R_types.y + TYPE_Y_BASE_SHIFT  # 5px mais alto que antes

        # círculos: raio 2px menor que o ícone
        circle_radius = max(1, (ICON_SZ - 2) // 2)
        cx_off = ICON_SZ // 2
        cy_off = ICON_SZ // 2

        def draw_type_icon(key, tx, ty):
            # círculo branco por trás
            pygame.draw.circle(tela, (255,255,255), (tx + cx_off, ty + cy_off), circle_radius)
            ic = icones.get(str(key).strip())
            if isinstance(ic, pygame.Surface):
                if ic.get_width() != ICON_SZ or ic.get_height() != ICON_SZ:
                    ic = pygame.transform.scale(ic, (ICON_SZ, ICON_SZ))
                tela.blit(ic, (tx, ty))
            else:
                lab = f_mini.render(str(key), True, (40,40,40))
                tela.blit(lab, (tx + max(0, (ICON_SZ - lab.get_width())//2),
                                ty + max(0, (ICON_SZ - lab.get_height())//2)))

        # (col=0,row=0): Tipo1
        if t1:
            draw_type_icon(t1, tx0, ty0)

        # (col=1,row=0): Sinergia (círculo + número)
        sx = tx0 + ICON_SZ + TYPE_COL_GAP
        sy = ty0
        pygame.draw.circle(tela, (255,255,255), (sx + cx_off, sy + cy_off), circle_radius)
        sin_surf = f_mini.render(str(sin_val), True, (30,30,30))
        tela.blit(sin_surf, (sx + cx_off - sin_surf.get_width()//2,
                             sy + cy_off - sin_surf.get_height()//2))

        # linha 2
        ty1 = ty0 + ICON_SZ + TYPE_ROW_GAP

        # (col=0,row=1): Tipo2
        if t2:
            draw_type_icon(t2, tx0, ty1)

        # (col=1,row=1): Tipo3
        if t3:
            draw_type_icon(t3, sx, ty1)

    # ================== Setor: DIREITO (ataques) ==================
    def setor_direito():
        global ATTACK_SURF_CACHE  # cache global de surfaces de ataques

        # helper para desenhar ícone centralizado e redimensionado
        def _blit_icon_center(btn_rect, icon_surface, pad=6):
            if not isinstance(icon_surface, pygame.Surface):
                return
            r = pygame.Rect(btn_rect)
            bw, bh = r.width, r.height
            iw, ih = icon_surface.get_size()
            if iw <= 0 or ih <= 0:
                return
            max_w = max(1, bw - pad * 2)
            max_h = max(1, bh - pad * 2)
            esc   = min(max_w / iw, max_h / ih)
            new_w = max(1, int(iw * esc))
            new_h = max(1, int(ih * esc))
            ic_scaled = pygame.transform.smoothscale(icon_surface, (new_w, new_h))
            dst = ic_scaled.get_rect(center=r.center)
            tela.blit(ic_scaled, dst)

        # coluna dos ataques
        moves_x = R_right.x + RIGHT_IN_PAD
        moves_y = R_right.y + max(RIGHT_IN_PAD - ATK_Y_EXTRA_UP, 0)

        # coluna nova (à direita dos ataques)
        extra_x = moves_x + ATTACK_W + EXTRA_BTN_GAP
        extra_y = moves_y

        # ------- lista de ataques (4 linhas) -------
        movelist = pokemon.get("MoveList", []) or []
        for i in range(4):
            ataque = movelist[i] if i < len(movelist) else None

            # surface do ataque (com cache por nome)
            if ataque:
                nome_atk = (ataque.get("nome") or ataque.get("Nome") or ataque.get("Ataque"))
                surf_atk = ATTACK_SURF_CACHE.get(nome_atk)
                if surf_atk is None:
                    surf_atk = SurfaceAtaque(
                        ataque, fontes, icones, main=True, size=(ATTACK_W, ATK_BTN_H)
                    )
                    ATTACK_SURF_CACHE[nome_atk] = surf_atk
            else:
                # placeholder leve
                surf_atk = pygame.Surface((ATTACK_W, ATK_BTN_H), pygame.SRCALPHA)
                pygame.draw.rect(surf_atk, (255,255,255,22), (0,0,ATTACK_W,ATK_BTN_H), border_radius=6)
                txt = f_mini.render("-", True, (200,200,200))
                surf_atk.blit(txt, ((ATTACK_W - txt.get_width())//2, (ATK_BTN_H - txt.get_height())//2))

            ataque_atual = ataque  # captura por linha

            # callbacks (você pode trocar depois)
            if ALIADO:
                func_esq = [
                    (lambda atk=ataque_atual: parametros.update({
                        "AtaqueAliadoSelecionado": atk,
                        "AtaqueInimigoSelecionado": None,
                        "ItemSelecionado": None,
                        "ModoAlvificando": True,
                        "AlvosSelecionados": [],
                        "AtacanteSelecionado": None,
                        "MovimentoSelecionado": None,
                        "CustoAtualEnergia": atk["custo"]
                    })),
                    (lambda: anima.update({"Y5": 1080, "Y6": 900, "_anima_painel_conteudo": pygame.time.get_ticks()})),
                ]
            else:
                func_esq = [
                    (lambda atk=ataque_atual: parametros.update({
                        "AtaqueAliadoSelecionado": None,
                        "AtaqueInimigoSelecionado": atk,
                        "ItemSelecionado": None,
                        "ModoAlvificando": False,
                        "CustoAtualEnergia": 0
                    })),
                    (lambda: anima.update({"Y5": 1080, "Y6": 900, "_anima_painel_conteudo": pygame.time.get_ticks()})),
                ]

            desf_esq = [
                (lambda: parametros.update({
                    "AtaqueAliadoSelecionado": None,
                    "AtaqueInimigoSelecionado": None,
                    "ItemSelecionado": None,
                    "ModoAlvificando": False,
                    "CustoAtualEnergia": 0
                })),
                (lambda: anima.update({"Y5": 900, "Y6": 1080, "_anima_painel_conteudo": pygame.time.get_ticks()})),
            ]

            # botão do ataque (usa a surface do ataque para o corpo do botão)
            Botao_Selecao(
                tela, "", (moves_x, moves_y, 0, 0), f_mini,
                surf_atk, (220,220,220),
                id_botao=f"{'A' if ALIADO else 'I'}_move_{i}_{pokemon.get('Nome','')}",
                estado_global=parametros["EstadoBotoesPainelPokemonBatalha"], eventos=eventos,
                cor_borda_esquerda=(120,220,120), cor_borda_direita=(220,120,120),
                cor_passagem=(230,230,230),
                branco=True, Surface=True, arredondamento=10, grossura=2,
                funcao_esquerdo=func_esq, desfazer_esquerdo=desf_esq
            )

            # ------- coluna extra (4 linhas) -------
            # i=0 → mover (sempre), i=1 → trocar (sempre), i=2..3 → habilidades ativas (se houver)
            btn_rect = (extra_x, extra_y, EXTRA_BTN_SZ, EXTRA_BTN_SZ)

            if i == 0:  # mover
                if ALIADO:
                    ic = icones.get("mover")

                    Botao_Selecao(
                        tela, "", btn_rect, f_mini,
                        cor_fundo=(120, 180, 255), cor_borda_normal=(200, 200, 255), cor_passagem=cores["branco"], cor_borda_esquerda=cores["vermelho"],
                        id_botao=f"{'A' if ALIADO else 'I'}_mover_{pokemon.get('Nome','')}",
                        estado_global=parametros["EstadoBotoesPainelPokemonBatalha"], eventos=eventos,
                        funcao_esquerdo=lambda: parametros.update({
                            "AtaqueAliadoSelecionado": 1,
                            "AtaqueInimigoSelecionado": None,
                            "ItemSelecionado": None,
                            "ModoAlvificando": True,
                            "AlvosSelecionados": [],
                            "AtacanteSelecionado": None,
                            "MovimentoSelecionado": None,
                            "CustoAtualEnergia": min(max(3,round((pokemon["Peso"] + 8) / 5)),70)
                        }),
                        desfazer_esquerdo=lambda: parametros.update({
                            "AtaqueAliadoSelecionado": None,
                            "AtaqueInimigoSelecionado": None,
                            "ItemSelecionado": None,
                            "ModoAlvificando": False,
                            "CustoAtualEnergia": 0
                        }),
                        arredondamento=8, grossura=2
                    )

                    _blit_icon_center(btn_rect, ic, pad=6)

            elif i == 1:  # trocar
                if ALIADO:
                    ic = icones.get("trocar")

                    Botao_Selecao(
                        tela, "", btn_rect, f_mini,
                        cor_fundo=(120, 180, 255), cor_borda_normal=(200, 200, 255), cor_passagem=cores["branco"], cor_borda_esquerda=cores["vermelho"],
                        id_botao=f"{'A' if ALIADO else 'I'}_trocar_{pokemon.get('Nome','')}",
                        estado_global=parametros["EstadoBotoesPainelPokemonBatalha"], eventos=eventos,
                        funcao_esquerdo=lambda: parametros.update({
                            "AtaqueAliadoSelecionado": 2,
                            "AtaqueInimigoSelecionado": None,
                            "ItemSelecionado": None,
                            "ModoAlvificando": True,
                            "AlvosSelecionados": [],
                            "AtacanteSelecionado": None,
                            "MovimentoSelecionado": None,
                            "CustoAtualEnergia": 5 if pokemon["Nivel"] < 50 else 10
                        }),
                        desfazer_esquerdo=lambda: parametros.update({
                            "AtaqueAliadoSelecionado": None,
                            "AtaqueInimigoSelecionado": None,
                            "ItemSelecionado": None,
                            "ModoAlvificando": False,
                            "CustoAtualEnergia": 0
                        }),
                        arredondamento=8, grossura=2
                    )

                    _blit_icon_center(btn_rect, ic, pad=6)

            else:
                # habilidades (até 2) alinhadas nas linhas 2 e 3
                habilidades = pokemon.get("HabilidadesAtivas") or []
                idx_hab = i - 2  # 0 ou 1
                if 0 <= idx_hab < len(habilidades):
                    hab = habilidades[idx_hab]
                    # aceita tanto string quanto dict {"Nome": "..."} ou {"Icone": "..."}
                    if isinstance(hab, dict):
                        hab_nome = (hab.get("Icone") or hab.get("Nome") or "").strip()
                    else:
                        hab_nome = str(hab).strip()

                    ic = icones.get(hab_nome)

                    # botão neutro para habilidade
                    Botao_Selecao(
                        tela, "", btn_rect, f_mini,
                        cor_fundo=(60, 60, 60), cor_borda_normal=(200,200,200), cor_passagem=cores["branco"],
                        id_botao=f"{'A' if ALIADO else 'I'}_hab_{i}_{pokemon.get('Nome','')}",
                        estado_global=parametros["EstadoBotoesPainelPokemonBatalha"], eventos=eventos,
                        funcao_esquerdo=(lambda: None),
                        arredondamento=8, grossura=2
                    )

                    _blit_icon_center(btn_rect, ic, pad=6)
                # se não houver habilidade para esta linha, não desenha nada extra

            # próxima linha
            moves_y += ATK_BTN_H + ATK_BTN_GAP
            extra_y += ATK_BTN_H + ATK_BTN_GAP

    setor_esquerda()             # << desenha o ESQUERDO e mede
    setor_central_superior()
    setor_central_inferior()
    setor_direito()

def PainelAcao(acao, parametros):
 
    # cores
    cor_borda       = (30, 30, 30)
    cor_header      = (235, 235, 235)
    cor_fundo       = (248, 248, 248)
    cor_placeholder = (220, 220, 220)
    cor_texto       = (20, 20, 20)

    # dimensões
    W, H = 150, 70
    HEADER_H = 24
    ICON = 42
    GAP = 3
    MARG_L = 9
    MARG_R = 9
    RADIUS = 10

    # fonte (para placeholders)
    fontes_param = parametros.get("Fontes")
    if isinstance(fontes_param, dict):
        fonte = fontes_param.get(16) or pygame.font.SysFont(None, 18)
    elif isinstance(fontes_param, (list, tuple)) and len(fontes_param) > 16:
        fonte = fontes_param[16] or pygame.font.SysFont(None, 18)
    else:
        fonte = pygame.font.SysFont(None, 18)

    # surface
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # fundo arredondado
    pygame.draw.rect(surf, cor_fundo, pygame.Rect(0, 0, W, H), border_radius=RADIUS)
    pygame.draw.rect(surf, cor_borda, pygame.Rect(0, 0, W, H), 1, border_radius=RADIUS)

    # cabeçalho (sem texto), com cantos superiores arredondados
    header_rect = pygame.Rect(0, 0, W, HEADER_H)
    pygame.draw.rect(surf, cor_header, header_rect, border_top_left_radius=RADIUS, border_top_right_radius=RADIUS)
    # linha separadora do cabeçalho
    pygame.draw.line(surf, cor_borda, (0, HEADER_H), (W, HEADER_H), 1)

    # --- faixa de ícones ---
    faixa_top = HEADER_H
    icon_top  = faixa_top + 2
    x_left  = MARG_L
    x_mid   = x_left + ICON + GAP
    x_right = x_mid + ICON + GAP

    # helpers
    def _scale_icon(img):
        if not img: return None
        try:
            if img.get_width() == ICON and img.get_height() == ICON:
                return img
            return pygame.transform.smoothscale(img, (ICON, ICON))
        except Exception:
            return None

    def _blit_placeholder(rect, text):
        pygame.draw.rect(surf, cor_placeholder, rect, border_radius=6)
        pygame.draw.rect(surf, cor_borda, rect, 1, border_radius=6)
        t = fonte.render(str(text), True, cor_texto)
        surf.blit(t, (rect.x + (rect.w - t.get_width()) // 2,
                      rect.y + (rect.h - t.get_height()) // 2))

    def _get_poke_icon_by_name(nome):
        if not nome: return None
        key = str(nome).lower()
        try:
            img = pokemons.get(key)
            return _scale_icon(img)
        except Exception:
            return None

    def _get_mov_icon(mov):
        # mov pode ser dict (com Estilo) ou int (1/2)
        if isinstance(mov, dict):
            est = (mov.get("Estilo") or mov.get("estilo") or "").strip().upper()
            try:
                if est == "N": return _scale_icon(icones.get("CustoFisico"))
                if est == "S": return _scale_icon(icones.get("CustoStatus"))
                if est == "E": return _scale_icon(icones.get("CustoEspecial"))
            except Exception:
                pass
        if isinstance(mov, int):
            if mov == 1: return _scale_icon(icones.get("mover"))
            if mov == 2: return _scale_icon(icones.get("trocar"))
        return None

    def _draw_icon_or_placeholder(x, top, image, placeholder_txt):
        rect = pygame.Rect(x, top, ICON, ICON)
        if image:
            surf.blit(image, rect.topleft)
        else:
            _blit_placeholder(rect, placeholder_txt)

    # ESQUERDA: Pokémon do Atacante (índice em EquipeAliada)
    atacante_idx = acao.get("Atacante")
    poke_img = None
    if atacante_idx is not None:
        try:
            equipeA = parametros.get("EquipeAliada") or []
            if 0 <= int(atacante_idx) < len(equipeA):
                nome = equipeA[int(atacante_idx)].get("Nome") or equipeA[int(atacante_idx)].get("nome")
                poke_img = _get_poke_icon_by_name(nome)
        except Exception:
            poke_img = None
    _draw_icon_or_placeholder(x_left, icon_top, poke_img, "A")

    # MEIO: Movimento
    mov = acao.get("Movimento")
    mov_img = _get_mov_icon(mov)
    place_meio = "—" if not isinstance(mov, int) else str(mov)
    _draw_icon_or_placeholder(x_mid, icon_top, mov_img, place_meio)

    # DIREITA: Alvos
    alvos = acao.get("Alvos") or []
    if len(alvos) == 1 and isinstance(alvos[0], str):
        code = alvos[0].strip().upper()
        lado = code[0] if len(code) >= 2 else "A"
        try:
            pos = int(code[1:])
        except Exception:
            pos = 1

        img_dir = None
        if lado == "A":
            equipe = parametros.get("EquipeAliada") or []
            poke = next((p for p in equipe if int(p.get("Pos", -1)) == pos), None)
            nome = (poke or {}).get("Nome") or (poke or {}).get("nome")
            img_dir = _get_poke_icon_by_name(nome) if poke else None
        elif lado == "I":
            equipe = parametros.get("EquipeInimiga") or []
            poke = next((p for p in equipe if int(p.get("Pos", -1)) == pos), None)
            nome = (poke or {}).get("Nome") or (poke or {}).get("nome")
            img_dir = _get_poke_icon_by_name(nome) if poke else None

        if img_dir:
            _draw_icon_or_placeholder(x_right, icon_top, img_dir, "?")
        else:
            _draw_icon_or_placeholder(x_right, icon_top, None, code)
    else:
        _draw_icon_or_placeholder(x_right, icon_top, None, "M")

    return surf
