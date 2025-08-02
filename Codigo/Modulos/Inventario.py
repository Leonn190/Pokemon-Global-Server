import pygame

from Codigo.Prefabs.BotoesPrefab import Botao

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

def SetorPlayer(tela, player):
    pass
def SetorPokemons(tela, player):
    pass
def SetorItens(tela, player):
    pass
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

    # Fundo central marrom claro
    largura_fundo = 1400
    altura_fundo = 900
    x_fundo = (1920 - largura_fundo) // 2
    y_fundo = (1080 - altura_fundo) // 2
    pygame.draw.rect(tela, (181, 141, 92), (x_fundo, y_fundo, largura_fundo, altura_fundo))  # marrom claro

    # Botões de setor
    largura_botao = 300
    altura_botao = 100
    espacamento = 20
    pos_x_inicial = x_fundo + (largura_fundo - (3 * largura_botao + 2 * espacamento)) // 2
    y_botoes = y_fundo + 30

    # Botão SetorPlayer
    Botao(
        tela, "PLAYER", (pos_x_inicial, y_botoes, largura_botao, altura_botao), 
        Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorPlayer}),
        Fontes[40], B_Splayer, eventos, 
        som="Clique", cor_texto=Cores["branco"], aumento=1.1
    )

    # Botão SetorPokemons
    Botao(
        tela, "POKÉMONS", (pos_x_inicial + largura_botao + espacamento, y_botoes, largura_botao, altura_botao),
        Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorPokemons}),
        Fontes[40], B_Spokemons, eventos,
        som="Clique", cor_texto=Cores["branco"], aumento=1.1
    )

    # Botão SetorItens
    Botao(
        tela, "ITENS", (pos_x_inicial + 2 * (largura_botao + espacamento), y_botoes, largura_botao, altura_botao),
        Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros["Inventario"].update({"Setor": SetorItens}),
        Fontes[40], B_Sitens, eventos,
        som="Clique", cor_texto=Cores["branco"], aumento=1.1
    )
    
