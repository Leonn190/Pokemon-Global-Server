import pygame

from Codigo.Prefabs.BotoesPrefab import Botao
from Codigo.Prefabs.Arrastavel import Arrastavel

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

# Configurações da grade do inventário
SLOTS_LARGURA = 10
SLOTS_ALTURA = 7
TAMANHO_SLOT = 70
ESPACO = 12

# Lista global para manter referência aos arrastáveis
arrastaveis_inventario = []
inventario_cache = []

areas_inventario = []  # Lista de rects dos slots

def desenhar_inventario(tela, player, pos_inicial=(230, 270), eventos=None):

    def executar_inventario(pos, dados, interno):
        global areas_inventario

        if interno:
            origem = player.Inventario.index(dados)

            if RectDireito.collidepoint(pos):
                player.Inventario[origem], player.MaoDireita = player.MaoDireita, player.Inventario[origem]
                return True
            elif RectEsquerdo.collidepoint(pos):
                player.Inventario[origem], player.MaoEsquerda = player.MaoEsquerda, player.Inventario[origem]
                return True
            
            for i, area in enumerate(areas_inventario):
                if area.collidepoint(pos):
                    player.Inventario[origem], player.Inventario[i] = player.Inventario[i], player.Inventario[origem]
                    return True
        else:
            if dados == player.MaoEsquerda:
                if RectDireito.collidepoint(pos):
                    player.MaoEsquerda, player.MaoDireita = player.MaoDireita, player.MaoEsquerda
                    return True
                
                for i, area in enumerate(areas_inventario):
                    if area.collidepoint(pos):
                        player.MaoEsquerda, player.Inventario[i] = player.Inventario[i], player.MaoEsquerda
                        return True 

            elif dados == player.MaoDireita:
                if RectEsquerdo.collidepoint(pos):
                    player.MaoEsquerda, player.MaoDireita = player.MaoDireita, player.MaoEsquerda
                    return True
                
                for i, area in enumerate(areas_inventario):
                    if area.collidepoint(pos):
                        player.MaoDireita, player.Inventario[i] = player.Inventario[i], player.MaoDireita
                        return True
                    
        return False

    global arrastaveis_inventario, inventario_cache, areas_inventario

    fundo_slot = pygame.transform.scale(fundos["FundoSlots"], (TAMANHO_SLOT, TAMANHO_SLOT))
    areas_inventario = []  # Lista de rects dos slots

    if inventario_cache != player.Inventario:
        inventario_cache = list(player.Inventario)
        arrastaveis_inventario.clear()

        for index, item in enumerate(player.Inventario):
            col = index % SLOTS_LARGURA
            lin = index // SLOTS_LARGURA
            x = pos_inicial[0] + col * (TAMANHO_SLOT + ESPACO)
            y = pos_inicial[1] + lin * (TAMANHO_SLOT + ESPACO)

            rect = pygame.Rect(x, y, TAMANHO_SLOT, TAMANHO_SLOT)
            areas_inventario.append(rect)
            tela.blit(fundo_slot, rect.topleft)
            fonte = fontes[20]

            if item:
                nome = item["nome"]
                numero = item["numero"]
                imagem = consumiveis.get(nome)

                if imagem:
                    imagem_ajustada = pygame.transform.scale(imagem, (TAMANHO_SLOT - 16, TAMANHO_SLOT - 16))
                    arr = Arrastavel(
                        imagem_ajustada,
                        (x + 8, y + 8),
                        dados=item,  # agora é o próprio item
                        interno=True,
                        funcao_execucao=executar_inventario
                    )
                    arrastaveis_inventario.append(arr)
                
                # Renderiza a quantidade do item
                texto_numero = fonte.render(str(numero), True, (0, 0, 0))  # Cor branca
                texto_rect = texto_numero.get_rect(bottomright=(x + TAMANHO_SLOT - 4, y + TAMANHO_SLOT - 4))
                tela.blit(texto_numero, texto_rect)

        RectDireito = pygame.Rect(1300,750, TAMANHO_SLOT, TAMANHO_SLOT)
        RectEsquerdo = pygame.Rect(1380,750, TAMANHO_SLOT, TAMANHO_SLOT)

        tela.blit(fundo_slot,(1300,750))
        tela.blit(fundo_slot,(1380,750))

        if player.MaoDireita is not None:
            imagem = pygame.transform.scale(consumiveis[player.MaoDireita["nome"]], (TAMANHO_SLOT - 16, TAMANHO_SLOT - 16))
            ArrDir = Arrastavel(imagem, (1300 + 8, 750 + 8), dados=player.MaoDireita, interno=False, funcao_execucao=executar_inventario)
            arrastaveis_inventario.append(ArrDir)
        if player.MaoEsquerda is not None:
            imagem = pygame.transform.scale(consumiveis[player.MaoEsquerda["nome"]], (TAMANHO_SLOT - 16, TAMANHO_SLOT - 16))
            ArrEsq = Arrastavel(imagem, (1380 + 8, 750 + 8), dados=player.MaoEsquerda, interno=False, funcao_execucao=executar_inventario)
            arrastaveis_inventario.append(ArrEsq)
    
    for index, item in enumerate(player.Inventario):
            if item:
                col = index % SLOTS_LARGURA
                lin = index // SLOTS_LARGURA
                x = pos_inicial[0] + col * (TAMANHO_SLOT + ESPACO)
                y = pos_inicial[1] + lin * (TAMANHO_SLOT + ESPACO)

                numero = item.get("numero", 1)
                fonte = fontes[20]
                texto_numero = fonte.render(str(numero), True, (0, 0, 0))
                texto_rect = texto_numero.get_rect(bottomright=(x + TAMANHO_SLOT - 4, y + TAMANHO_SLOT - 4))
                tela.blit(texto_numero, texto_rect)
                
                RectDireito = pygame.Rect(1300,750, TAMANHO_SLOT, TAMANHO_SLOT)
                RectEsquerdo = pygame.Rect(1380,750, TAMANHO_SLOT, TAMANHO_SLOT)

                tela.blit(fundo_slot,(1300,750))
                tela.blit(fundo_slot,(1380,750))

    for arr in arrastaveis_inventario:
        arr.atualizar(eventos)
        arr.arrastar(pygame.mouse.get_pos())

    for arr in arrastaveis_inventario:
        if not arr.esta_arrastando:
            arr.desenhar(tela)
    for arr in arrastaveis_inventario:
        if arr.esta_arrastando:
            arr.desenhar(tela)
            
def SetorPlayer(tela, player, eventos):
    pass

def SetorPokemons(tela, player, eventos):
    pass

def SetorItens(tela, player, eventos):

    desenhar_inventario(tela, player, eventos=eventos)

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

    # Botão PLAYER
    Botao(
        tela, "PLAYER", (x1, y_botoes, largura_botao, altura_botao), 
        Texturas["Madeira"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorPlayer}),
        Fontes[40], B_Splayer, eventos, 
        som="Clique", cor_texto=Cores["branco"], aumento=1.05
    )

    # Botão POKÉMONS
    Botao(
        tela, "POKÉMONS", (x2, y_botoes, largura_botao, altura_botao),
        Texturas["Madeira"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorPokemons}),
        Fontes[40], B_Spokemons, eventos,
        som="Clique", cor_texto=Cores["branco"], aumento=1.05
    )

    # Botão ITENS
    Botao(
        tela, "ITENS", (x3, y_botoes, largura_botao, altura_botao),
        Texturas["Madeira"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorItens}),
        Fontes[40], B_Sitens, eventos,
        som="Clique", cor_texto=Cores["branco"], aumento=1.05
    )
    
    parametros["Inventario"]["Setor"](tela, player, eventos)
