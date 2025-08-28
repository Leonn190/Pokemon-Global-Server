import pygame
import copy

from Codigo.Prefabs.BotoesPrefab import Botao, Botao_invisivel
from Codigo.Prefabs.Arrastavel import Arrastavel
from Codigo.Modulos.Paineis import PainelItem, PainelPokemon, PainelPokemonAuxiliar, PainelPlayer

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

B_Splayer = {}
B_Spokemons = {}
B_Sitens = {}

Barras_Controle = {}

# Configurações da grade do inventário
SLOTS_LARGURA = 10
SLOTS_ALTURA = 7
TAMANHO_SLOT = 72
ESPACO = 15

# Lista global para manter referência aos arrastáveis
arrastaveis_inventario = []
inventario_cache = []
areas_inventario = []  # Lista de rects dos slots

arrastaveis_pokemons = []
pokemons_cache = []
times_cache = []
areas_pokemons = []
areas_pokemons_times = []

pos_grid=(230, 274)

def SetorPlayer(tela, player, eventos, parametros):
    PainelPlayer(tela, (175,250), player, eventos, parametros)

def SetorPokemonsPadrao(tela, player, eventos, parametros):
    global areas_pokemons, pokemons_cache, arrastaveis_pokemons, times_cache

    def executar_pokemon(arr):
        global pokemons_cache

        interno = arr.interno
        pos = arr.pos
        dados = arr.dados
        timeOrigem = arr.infoExtra1

        if interno:
            for i, area in enumerate(areas_pokemons):
                if area.collidepoint(pos):
                    origem = player.Pokemons.index(dados)
                    if player.Pokemons[origem] == player.Pokemons[i]:
                        return False
                    else:
                        player.Pokemons[origem], player.Pokemons[i] = player.Pokemons[i], player.Pokemons[origem]
                        return True
                    
            for i, area in enumerate(areas_pokemons_times):
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
            for i, area in enumerate(areas_pokemons_times):
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

    # --- layout geral (mantive suas contas) ---
    linhas_total = (len(player.Pokemons) + SLOTS_LARGURA - 1) // SLOTS_LARGURA
    largura_total = SLOTS_LARGURA * TAMANHO_SLOT + (SLOTS_LARGURA - 1) * ESPACO
    altura_total = linhas_total * TAMANHO_SLOT + (linhas_total - 1) * ESPACO

    # fundo da área principal de slots
    fundo_rect = pygame.Rect(pos_grid[0] - 14, pos_grid[1] - 14, largura_total + 28, altura_total + 28)
    pygame.draw.rect(tela, (139, 69, 19), fundo_rect, border_radius=6)

    fundo_slot = pygame.transform.scale(fundos["FundoSlots"], (TAMANHO_SLOT, TAMANHO_SLOT))

    # limpar/renovar arrays que representam áreas (sempre)
    areas_pokemons.clear()
    areas_pokemons_times.clear()

    # === 1) OBRIGATÓRIO: desenhar grade principal (sempre) ===
    for index in range(len(player.Pokemons)):
        col = index % SLOTS_LARGURA
        lin = index // SLOTS_LARGURA
        x = pos_grid[0] + col * (TAMANHO_SLOT + ESPACO)
        y = pos_grid[1] + lin * (TAMANHO_SLOT + ESPACO)

        rect = pygame.Rect(x, y, TAMANHO_SLOT, TAMANHO_SLOT)
        areas_pokemons.append(rect)
        tela.blit(fundo_slot, rect.topleft)

        poke = player.Pokemons[index]

        # botão invisível para seleção (sempre)
        Botao_invisivel((x, y, TAMANHO_SLOT, TAMANHO_SLOT), lambda p=poke: parametros.update({"PokemonSelecionado": p}), clique_duplo=True)

    # === 2) OBRIGATÓRIO: desenhar área dos TIMES (fundo + títulos + poderes + slots + imagens/níveis) ===
    equipes_cache = getattr(player, "Equipes", [])
    num_times = min(5, max(1, len(equipes_cache)))  # garante pelo menos 1 na conta visual
    pos_equipes_x = pos_grid[0] + largura_total + 100
    pos_equipes_y = pos_grid[1]
    fonte_equipes = fontes[20]  # ajuste se quiser maior/menor

    header_h = fonte_equipes.get_height()
    # altura por time: header + espaço + slot
    altura_por_time = header_h + 4 + TAMANHO_SLOT
    # espaçamento entre times (o seu código usava +24)
    espacamento_times = 24
    altura_total_times = num_times * altura_por_time + (num_times - 1) * espacamento_times

    largura_times = 6 * TAMANHO_SLOT + (6 - 1) * ESPACO
    padding = 12
    # fundo que engloba todos os times (um único fundo atrás da seção dos times)
    fundo_times_rect = pygame.Rect(
        pos_equipes_x - padding,
        pos_equipes_y - padding,
        largura_times + padding * 2,
        altura_total_times + padding * 2
    )
    pygame.draw.rect(tela, (139, 69, 19), fundo_times_rect, border_radius=6)

    # agora desenha cada time (título, poder, slots, imagens, níveis) — sempre
    cur_y = pos_equipes_y
    for idx, equipe in enumerate(equipes_cache[:5]):
        # calcula poder do time (soma de poke["Total"] dos pokes presentes)
        poder_total = round(sum((p.get("Total", 0) for p in equipe if p)))
        texto_poder = fonte_equipes.render(f"Poder: {poder_total}", True, (255, 255, 0))
        texto_time = fonte_equipes.render(f"Time {idx + 1}", True, (255, 255, 255))

        # desenha poder à esquerda e "Time X" à direita (dentro da área dos times)
        tela.blit(texto_poder, (pos_equipes_x + 5, cur_y))
        tela.blit(texto_time, (pos_equipes_x + largura_times - texto_time.get_width(), cur_y))

        y_slots = cur_y + header_h + 4
        for slot_idx in range(6):
            x = pos_equipes_x + slot_idx * (TAMANHO_SLOT + ESPACO)
            y = y_slots
            rect = pygame.Rect(x, y, TAMANHO_SLOT, TAMANHO_SLOT)
            pygame.draw.rect(tela, (139, 69, 19), rect, border_radius=4)
            tela.blit(fundo_slot, rect.topleft)

            areas_pokemons_times.append(rect)

        cur_y += altura_por_time + espacamento_times

     # ---- snapshot de equipes como IDs (ordem preservada) ----
    def snapshot_equipes_ids(equipes):
        # lista de listas de dicts -> tupla de tuplas de IDs
        snapshot = []
        for equipe in equipes:
            ids = tuple(m["ID"] for m in equipe if m is not None)
            snapshot.append(ids)
        return tuple(snapshot)

    # ---- comparação e atualização de caches ----
    times_now_ids = snapshot_equipes_ids(player.Equipes)

    if (pokemons_cache != player.Pokemons) or (times_cache != times_now_ids):
        times_cache    = times_now_ids
        pokemons_cache = copy.deepcopy(player.Pokemons)  # snapshot pra detectar mutações in-place
        arrastaveis_pokemons.clear()

        # arrastaveis para grade principal
        for index, poke in enumerate(player.Pokemons):
            if not poke:
                continue
            col = index % SLOTS_LARGURA
            lin = index // SLOTS_LARGURA
            x = pos_grid[0] + col * (TAMANHO_SLOT + ESPACO)
            y = pos_grid[1] + lin * (TAMANHO_SLOT + ESPACO)

            nome = poke["Nome"]
            imagem = pokemons.get(nome.lower())
            if imagem:
                imagem_ajustada = pygame.transform.scale(imagem, (TAMANHO_SLOT + 2, TAMANHO_SLOT + 2))
                arr = Arrastavel(
                    imagem_ajustada,
                    (x - 1, y - 1),
                    dados=poke,
                    interno=True,
                    funcao_execucao=executar_pokemon
                )
                arrastaveis_pokemons.append(arr)

        # arrastaveis para os times (mantendo infoExtra1 = indice do time)
        cur_y = pos_equipes_y
        for idx, equipe in enumerate(equipes_cache[:5]):
            y_slots = cur_y + header_h + 4
            for slot_idx in range(6):
                x = pos_equipes_x + slot_idx * (TAMANHO_SLOT + ESPACO)
                y = y_slots
                poke = equipe[slot_idx] if slot_idx < len(equipe) else None
                if poke:
                    nome = poke["Nome"]
                    imagem = pokemons.get(nome.lower())
                    if imagem:
                        imagem_ajustada = pygame.transform.scale(imagem, (TAMANHO_SLOT + 2, TAMANHO_SLOT + 2))
                        arr = Arrastavel(
                            imagem_ajustada,
                            (x - 1, y - 1),
                            dados=poke,
                            interno=False,
                            infoExtra1=idx,
                            funcao_execucao=executar_pokemon
                        )
                        arrastaveis_pokemons.append(arr)
            cur_y += altura_por_time + espacamento_times

        # Atualizar e desenhar arrastáveis
    for arr in arrastaveis_pokemons:
        if parametros["PokemonSelecionado"] is not None:
            arr.esta_arrastando = False
        arr.atualizar(eventos)
        arr.arrastar(pygame.mouse.get_pos())

    for arr in arrastaveis_pokemons:
        if not arr.esta_arrastando:
            arr.desenhar(tela)
    for arr in arrastaveis_pokemons:
        if arr.esta_arrastando:
            arr.desenhar(tela)

def SetorPokemons(tela, player, eventos, parametros):

    if parametros["PokemonSelecionado"] is not None:
        PainelPokemon(tela,(175,250),parametros["PokemonSelecionado"], Barras_Controle, eventos, parametros)
        PainelPokemonAuxiliar(tela, (1500,250), player, eventos, parametros)
        
    else:
        SetorPokemonsPadrao(tela, player, eventos, parametros)

def SetorItens(tela, player, eventos, parametros):
    global arrastaveis_inventario, inventario_cache, areas_inventario

    def executar_inventario(arr):
        interno = arr.interno
        pos = arr.pos
        dados = arr.dados

        if interno:
            for i, area in enumerate(areas_pokemons):
                if area.collidepoint(pos):
                    origem = player.Inventario.index(dados)
                    if player.Inventario[origem] == player.Inventario[i]:
                        return False
                    else:
                        player.Inventario[origem], player.Inventario[i] = player.Inventario[i], player.Inventario[origem]
                        return True
    
        # === Desenhar fundo marrom da área do inventário ===
    linhas_total = (len(player.Inventario) + SLOTS_LARGURA - 1) // SLOTS_LARGURA
    largura_total = SLOTS_LARGURA * TAMANHO_SLOT + (SLOTS_LARGURA - 1) * ESPACO
    altura_total = linhas_total * TAMANHO_SLOT + (linhas_total - 1) * ESPACO

    fundo_rect = pygame.Rect(pos_grid[0] - 14, pos_grid[1] - 14, largura_total + 28, altura_total + 28)
    pygame.draw.rect(tela, (139, 69, 19), fundo_rect, border_radius=6)  # marrom com cantos arredondados

    fundo_slot = pygame.transform.scale(fundos["FundoSlots"], (TAMANHO_SLOT, TAMANHO_SLOT))
    areas_inventario = []  # Lista de rects dos slots
    fonte = fontes[20]

    if inventario_cache != player.Inventario:
        inventario_cache = list(player.Inventario)
        arrastaveis_inventario.clear()

        for index, item in enumerate(player.Inventario):
            col = index % SLOTS_LARGURA
            lin = index // SLOTS_LARGURA
            x = pos_grid[0] + col * (TAMANHO_SLOT + ESPACO)
            y = pos_grid[1] + lin * (TAMANHO_SLOT + ESPACO)

            rect = pygame.Rect(x, y, TAMANHO_SLOT, TAMANHO_SLOT)
            areas_inventario.append(rect)
            tela.blit(fundo_slot, rect.topleft)

            if item:
                nome = item["nome"]
                numero = item.get("numero", 1)
                imagem = consumiveis.get(nome)

                if imagem:
                    imagem_ajustada = pygame.transform.scale(imagem, (TAMANHO_SLOT - 16, TAMANHO_SLOT - 16))
                    arr = Arrastavel(
                        imagem_ajustada,
                        (x + 8, y + 8),
                        dados=item,
                        interno=True,
                        funcao_execucao=executar_inventario
                    )
                    arrastaveis_inventario.append(arr)

                # ➕ Desenhar número no canto inferior direito
                texto = fonte.render(str(numero), True, (0, 0, 0))
                texto_rect = texto.get_rect(bottomright=(x + TAMANHO_SLOT - 4, y + TAMANHO_SLOT - 4))
                tela.blit(texto, texto_rect)

    else:
        for index in range(len(player.Inventario)):
            col = index % SLOTS_LARGURA
            lin = index // SLOTS_LARGURA
            x = pos_grid[0] + col * (TAMANHO_SLOT + ESPACO)
            y = pos_grid[1] + lin * (TAMANHO_SLOT + ESPACO)

            rect = pygame.Rect(x, y, TAMANHO_SLOT, TAMANHO_SLOT)
            areas_inventario.append(rect)
            tela.blit(fundo_slot, rect.topleft)

            item = player.Inventario[index]
            if item:
                numero = item.get("numero", 1)
                texto = fonte.render(str(numero), True, (0, 0, 0))
                texto_rect = texto.get_rect(bottomright=(x + TAMANHO_SLOT - 4, y + TAMANHO_SLOT - 4))
                Botao_invisivel((x, y, TAMANHO_SLOT, TAMANHO_SLOT),lambda i=item: parametros.update({"ItemSelecionado": i}))
                tela.blit(texto, texto_rect)

    # Atualizar e desenhar arrastáveis
    for arr in arrastaveis_inventario:
        arr.atualizar(eventos)
        arr.arrastar(pygame.mouse.get_pos())

    for arr in arrastaveis_inventario:
        if not arr.esta_arrastando:
            arr.desenhar(tela)
    for arr in arrastaveis_inventario:
        if arr.esta_arrastando:
            arr.desenhar(tela)

        # ==== Mostrar contagem de itens ====
    fonte_info = fontes[40]
    texto_info = f"{player.Itens} / {player.MaxItens}"
    texto_renderizado = fonte_info.render(texto_info, True, (0, 0, 0))

    # Calcular a posição X central em relação à grade
    largura_total = SLOTS_LARGURA * TAMANHO_SLOT + (SLOTS_LARGURA - 1) * ESPACO
    centro_x = pos_grid[0] + largura_total // 2

    # Calcular posição Y abaixo da última linha
    linhas_total = (len(player.Inventario) + SLOTS_LARGURA - 1) // SLOTS_LARGURA
    y_ultimo = pos_grid[1] + linhas_total * (TAMANHO_SLOT + ESPACO) + 25

    texto_rect = texto_renderizado.get_rect(center=(centro_x, y_ultimo))
    tela.blit(texto_renderizado, texto_rect)

    PainelItem(tela, (1320,270), parametros["ItemSelecionado"])

def TelaInventario(tela, player, eventos, parametros):
    from Codigo.Cenas.Mundo import Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes
    global cores, fontes, texturas, fundos, outros, pokemons, estruturas, equipaveis, consumiveis, animaçoes

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

    if parametros["Inventario"]["Setor"] is None:
        parametros["Inventario"]["Setor"] = SetorItens
    
    if parametros["Inventario"]["Setor"] != SetorPokemons:
        parametros["Inventario"]["PokemonSelecionado"] = None
        parametros["Inventario"]["AtaqueSelecionado"] = None
    
    if parametros["Inventario"]["Setor"] != SetorItens:
        parametros["Inventario"]["ItemSelecionado"] = None

    largura_fundo = 1600
    altura_fundo = 850
    x_fundo = (1920 - largura_fundo) // 2
    y_fundo = (1080 - altura_fundo) // 2

    # Fechar inventário se clicar fora dele
    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = evento.pos
            inventario_rect = pygame.Rect(x_fundo, y_fundo, largura_fundo, altura_fundo)
            if not inventario_rect.collidepoint(pos):
                parametros.update({"InventarioAtivo": False})

    # Desenha fundo com borda preta
    pygame.draw.rect(tela, (0, 0, 0), (x_fundo - 2, y_fundo - 2, largura_fundo + 4, altura_fundo + 4))  # Borda preta
    pygame.draw.rect(tela, (181, 141, 92), (x_fundo, y_fundo, largura_fundo, altura_fundo))  # Fundo marrom claro

    altura_topo = 120
    margem_lateral = 35
    espacamento = 30
    largura_botao = (largura_fundo - 2 * margem_lateral - 2 * espacamento) // 3
    altura_botao = altura_topo

    y_botoes = y_fundo
    x1 = x_fundo + margem_lateral
    x2 = x1 + largura_botao + espacamento
    x3 = x2 + largura_botao + espacamento

    # Linha divisória preta após os botões
    pygame.draw.line(tela, (0, 0, 0), (x_fundo, y_fundo + altura_topo), (x_fundo + largura_fundo, y_fundo + altura_topo), 3)

    cor_branca = Cores["branco"]
    cor_amarela = Cores["amarelo"]  # amarelo puro, pode ajustar se quiser

    Botao(
        tela, "PLAYER", (x1, y_botoes, largura_botao, altura_botao), 
        Texturas["Madeira"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorPlayer}),
        Fontes[40], B_Splayer, eventos, 
        som="Clique", 
        cor_texto=cor_amarela if parametros["Inventario"]["Setor"] == SetorPlayer else cor_branca,
        aumento=1.05
    )

    Botao(
        tela, "POKÉMONS", (x2, y_botoes, largura_botao, altura_botao),
        Texturas["Madeira"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorPokemons}),
        Fontes[40], B_Spokemons, eventos,
        som="Clique",
        cor_texto=cor_amarela if parametros["Inventario"]["Setor"] == SetorPokemons else cor_branca,
        aumento=1.05
    )

    Botao(
        tela, "ITENS", (x3, y_botoes, largura_botao, altura_botao),
        Texturas["Madeira"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorItens}),
        Fontes[40], B_Sitens, eventos,
        som="Clique",
        cor_texto=cor_amarela if parametros["Inventario"]["Setor"] == SetorItens else cor_branca,
        aumento=1.05
    )
    
    parametros["Inventario"]["Setor"](tela, player, eventos, parametros["Inventario"])
