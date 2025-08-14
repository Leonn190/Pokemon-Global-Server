
import pygame

from Codigo.Prefabs.FunçõesPrefabs import Barra, Scrolavel, Slider
from Codigo.Prefabs.BotoesPrefab import Botao, Botao_invisivel
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

def BarraDeItens(tela, player, eventos): 
    from Codigo.Cenas.Mundo import Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes
    global cores, fontes, texturas, fundos, outros, pokemons, estruturas, equipaveis, consumiveis, animaçoes

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

B_Voltar = {}

def PainelPokemon(tela, pos, pokemon, estado_barra, eventos, parametros):
    global pokemon_cache, pokemon_refresh, pokemon_atributos_salvos

    largura_painel = 1300
    altura_painel = 700
    x0, y0 = pos

    # --- Fundo do painel ---
    cor_fundo = (139, 69, 19)  # marrom escuro
    pygame.draw.rect(tela, cor_fundo, (x0, y0, largura_painel, altura_painel))

    # --- Cabeçalho ---
    altura_cabecalho = 70
    cor_cabecalho = (150, 75, 35)
    pygame.draw.rect(tela, cor_cabecalho, (x0, y0, largura_painel, altura_cabecalho))

    # Linha separadora do cabeçalho
    pygame.draw.line(
        tela, (0, 0, 0),
        (x0, y0 + altura_cabecalho),
        (x0 + largura_painel, y0 + altura_cabecalho),
        3
    )

    # Nome do Pokémon no centro
    nome_poke = str(pokemon.get("Nome", ""))
    fonte_cabecalho = fontes[35]
    txt_nome = fonte_cabecalho.render(nome_poke, True, (255, 255, 255))
    txt_nome_rect = txt_nome.get_rect(center=(x0 + largura_painel // 2, y0 + altura_cabecalho // 2))
    tela.blit(txt_nome, txt_nome_rect)

    # --- Botão no canto esquerdo ---
    botao_x = x0 + 2
    botao_y = y0 + 2
    botao_tam = 66
    Botao(
        tela, "", (botao_x, botao_y, botao_tam, botao_tam),
        cores["amarelo"], cores["preto"], cores["branco"],
        lambda: parametros.update({"PokemonSelecionado": None}),
        fontes[16], B_Voltar, eventos
    )

    # --- Imagem do Pokémon no canto direito ---
    img_x = x0 + largura_painel - botao_tam - 2
    img_y = y0 + 2
    if pokemon_refresh:
        imagem = pokemons.get(nome_poke.lower(), CarregarPokemon(nome_poke.lower(), pokemons))
    else:
        imagem = pokemons.get(nome_poke.lower())

    if imagem:
        imagem_redim = pygame.transform.smoothscale(imagem, (botao_tam, botao_tam))
        tela.blit(imagem_redim, (img_x, img_y))

    # --- Borda do painel ---
    pygame.draw.rect(tela, (0, 0, 0), (x0, y0, largura_painel, altura_painel), width=4)

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

    cores_barras = [
        (255, 0, 0),      # Vida - vermelho
        (255, 128, 0),    # Atk - laranja
        (255, 255, 0),    # Def - amarelo
        (128, 255, 0),    # SpA - verde claro
        (0, 255, 0),      # SpD - verde
        (0, 255, 128),    # Vel - verde água
        (0, 255, 255),    # Mag - ciano
        (0, 128, 255),    # Per - azul claro
        (0, 0, 255),      # Ene - azul
        (128, 0, 255),    # EnR - roxo claro
        (255, 0, 255),    # CrD - magenta
        (255, 0, 128),    # CrC - rosa
    ]

    largura_barra = 30
    altura_maxima = 250
    espacamento_horizontal = 75

    margem_inferior = 50
    margem_superior = 60

    fonte_nome = fontes[24]
    fonte_valor = fontes[25]
    fonte_iv = fontes[16]

    # --- TERCEIRO SETOR: animação idle + nível + barra de XP (canto superior esquerdo) ---
    def _desenhar_animacao():
        global idle

        ANIM_W, ANIM_H = 175, 175
        # Se quiser posicionar pela "caixa" da animação, defina o canto ESQUERDO/SUPERIOR
        LEFT = x0 + 50
        TOP  = y0 + 100

        # Centro geométrico da animação (a classe desenha no centro)
        CX = LEFT + ANIM_W // 2
        CY = TOP  + ANIM_H // 2

        # --- 1) Nome e frames (carrega se necessário) ---
        nome_poke = pokemon.get("Nome") or pokemon.get("Name") or str(pokemon.get("ID", ""))
        frames = animaçoes.get(nome_poke)  # use "Animacoes" (ASCII). Evite "Animaçoes" com cedilha.

        # --- 2) Instanciar/renovar SÓ quando troca de Pokémon ---
        if pokemon_refresh:
            frames = animaçoes.get(nome_poke, CarregarAnimacaoPokemon(nome_poke, animaçoes))
            idle = Animação(frames=frames, posicao=(CX, CY), intervalo=30, tamanho=1.2)

        # --- 3) Texto "Nível" ACIMA da animação (alinhado ao centro) ---
        nivel = int(pokemon.get("Nivel", 1))
        txt_nivel = fonte_nome.render(f"Nível {nivel}", True, (0, 0, 0))
        txt_nivel_rect = txt_nivel.get_rect(center=(CX, CY - ANIM_H // 2 - 12))
        tela.blit(txt_nivel, txt_nivel_rect)

        idle.atualizar(tela)

        # --- 5) Barra de XP ABAIXO da animação ---
        xp_atual = int(pokemon.get("XP", 0))
        xp_max = max(1, nivel * 10)

        BAR_W, BAR_H = ANIM_W, 18
        bar_x = CX - BAR_W // 2
        bar_y = CY + ANIM_H // 2 + 10
        cor_xp = cores["verde"]

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

        # --- 6) Texto "XP atual / XP necessário" abaixo da barra ---
        txt_xp = fontes[16].render(f"XP: {xp_atual} / {xp_max}", True, (0, 0, 0))
        txt_xp_rect = txt_xp.get_rect(center=(CX, bar_y + BAR_H + 16))
        tela.blit(txt_xp, txt_xp_rect)

    # ---------- HELPER 1: Barras ----------
    def _desenhar_barras():
        # Pré-calcula o valor máximo ajustado para todas as barras
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

            # Ajusta o valor para escala da barra
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

            # Usa a função Barra para desenhar
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

            # Nome do atributo
            texto_nome = fonte_nome.render(attr, True, (0, 0, 0))
            texto_nome_rect = texto_nome.get_rect(center=(x_barra + largura_barra // 2,
                                                          y_base - altura_maxima - margem_superior + 10))
            tela.blit(texto_nome, texto_nome_rect)

            # Valor do atributo
            texto_valor = fonte_valor.render(str(int(valor_atual)), True, (0, 0, 0))
            texto_valor_rect = texto_valor.get_rect(center=(x_barra + largura_barra // 2,
                                                            texto_nome_rect.bottom + 10))
            tela.blit(texto_valor, texto_valor_rect)

            # IV embaixo
            texto_iv = fonte_iv.render(f"IV: {int(valor_iv)}%", True, (0, 0, 0))
            texto_iv_rect = texto_iv.get_rect(center=(x_barra + largura_barra // 2, y_base + 20))
            tela.blit(texto_iv, texto_iv_rect)

    # ---------- HELPER 2: Blocos informativos ----------
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
            # Pegar os 6 maiores valores relativos
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
        altura_caixa = 80
        espacamento_caixa = 15

        # Posição inicial (primeira caixa, primeira coluna)
        x_base = x0 + len(atributos) * espacamento_horizontal + 25
        y_base = y0 + 225

        for i, (titulo, valor) in enumerate(info_caixas):
            coluna = i // 5  # 0 para primeiras 5, 1 para últimas 5
            linha = i % 5    # 0 a 4

            x_caixa = x_base + coluna * (largura_caixa + espacamento_caixa)
            y_caixa = y_base + linha * (altura_caixa + espacamento_caixa)

            # Desenha caixa
            pygame.draw.rect(tela, (200, 200, 200), (x_caixa, y_caixa, largura_caixa, altura_caixa))
            pygame.draw.rect(tela, (0, 0, 0), (x_caixa, y_caixa, largura_caixa, altura_caixa), 2)

            # Texto título (em cima)
            txt_titulo = fonte_nome.render(str(titulo), True, (0, 0, 0))
            txt_titulo_rect = txt_titulo.get_rect(center=(x_caixa + largura_caixa // 2, y_caixa + 20))
            tela.blit(txt_titulo, txt_titulo_rect)

            # Texto valor (embaixo)
            txt_valor = fonte_valor.render(str(valor), True, (0, 0, 0))
            txt_valor_rect = txt_valor.get_rect(center=(x_caixa + largura_caixa // 2, y_caixa + altura_caixa - 25))
            tela.blit(txt_valor, txt_valor_rect)

    # --- chamadas das helpers (ordem original: barras primeiro, depois blocos) ---
    _desenhar_barras()
    _desenhar_blocos_informativos()
    _desenhar_animacao()

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
                    time = i // 6
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
                    timeAlvo = i // 6
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
    largura = 1550
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

    # ---------------- Esquerda: informações em duas margens ----------------
    padding = 20
    col_w = 420
    gap_colunas = 24
    top_info = y + padding + 10
    left_block_x = x + padding
    right_block_x = left_block_x + col_w + gap_colunas

    total_pokes = len([p for p in player.Pokemons if p is not None])
    total_itens = getattr(player, "Itens", [])
    total_skins_lib = len(getattr(player, "SkinsLiberadas", []))
    v_pvp = getattr(player, "BatalhasVencidasPVP", 0)
    v_bot = getattr(player, "BatalhasVencidasBOT", 0)
    v_total = v_pvp + v_bot

    def draw_kv(label, valor, x0, y0):
        tela.blit(font.render(str(label), True, cor_texto_suave), (x0, y0))
        tela.blit(font_titulo.render(str(valor), True, cor_texto), (x0, y0 + 22))

    tela.blit(font_titulo.render("Perfil do Jogador", True, cor_texto), (left_block_x, y + padding))

    linha = top_info + 28
    draw_kv("Pokémons", total_pokes, left_block_x, linha); linha += 60
    draw_kv("Itens", total_itens, left_block_x, linha); linha += 60
    draw_kv("Skins liberadas", total_skins_lib, left_block_x, linha); linha += 60

    linha2 = top_info + 28
    draw_kv("Vitórias (Total)", v_total, right_block_x, linha2); linha2 += 60
    draw_kv("Vitórias vs Jogadores", v_pvp, right_block_x, linha2); linha2 += 60
    draw_kv("Vitórias vs BOT", v_bot, right_block_x, linha2); linha2 += 60

    # ---------------- Direita: área do player ----------------
    area_player_w = 500
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

    # ---------------- Slider de Skin (inferior) ----------------
    # Slider opera sobre o ÍNDICE na lista SkinsLiberadas (0..N-1)
    slider_x = x + padding
    slider_y = y + altura - 30
    slider_w = largura - 2 * padding

    NovoNumero = (player.SkinsLiberadas.index(player.SkinNumero) + 1)

    NovoNumero = Slider(
        tela, "Skin", slider_x, slider_y, slider_w,
        NovoNumero, 1, max(0, total_skins_lib) ,
        (180, 180, 180), (255, 255, 255), eventos,
        "", Mostrar=False)

    if NovoNumero != player.SkinNumero:
        player.SkinNumero = round(NovoNumero)
        player.Skin = outros["SkinsTodas"][player.SkinNumero]
        player.SkinRedimensionada = pygame.transform.scale(player.Skin, (83, 66))

    tela.blit(font.render("Use o slider para trocar a skin do jogador", True, cor_texto_suave),
              (slider_x, slider_y - 40))

    # ---------------- Desenhar o player (canto direito superior) ----------------
    # Usa a skin já atualizada do próprio player
    centro_x = x_quadrado + largura_quadrado / 2
    centro_y = y_quadrado + altura_quadrado / 2

    DesenharPlayer(tela, player.Skin, (centro_x, centro_y))

