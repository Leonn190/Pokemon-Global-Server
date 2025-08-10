
import pygame

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
