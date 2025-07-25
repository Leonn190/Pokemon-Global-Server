import pygame
from Prefabs.FunçõesPrefabs import Barra_De_Texto
from Prefabs.BotoesPrefab import Botao

B1 = {}
B2 = {}
SelecionadoEntrada = False

def TelaEntradaDeTexto(tela, estados, eventos, parametros):
    global SelecionadoEntrada

    from Cenas.Inicio import Fontes, Cores, Texturas, Outros, Fontes

    Rotulo = parametros.get("TelaEntradaDeTexto", {}).get("Rotulo")
    Enviar = parametros.get("TelaEntradaDeTexto", {}).get("Enviar")
    Voltar = parametros.get("TelaEntradaDeTexto", {}).get("Voltar")

    # Configurações de layout
    largura_fundo, altura_fundo = 800, 300
    x_fundo = (1920 - largura_fundo) // 2
    y_fundo = (1080 - altura_fundo) // 2
    fundo_rect = pygame.Rect(x_fundo, y_fundo, largura_fundo, altura_fundo)

    # Fundo preto
    pygame.draw.rect(tela, Cores["preto"], fundo_rect)

    texto_instrucao = Fontes[40].render(Rotulo, True, Cores["branco"])
    tela.blit(texto_instrucao, (x_fundo + 30, y_fundo + 30))

    # Barra de texto
    parametros["TelaEntradaDeTexto"]["Texto"], SelecionadoEntrada = Barra_De_Texto(
        tela,
        (x_fundo + 30, y_fundo + 80, 740, 60),
        Fontes[40],
        Cores["cinza"],
        Cores["branco"],
        Cores["branco"],
        eventos,
        parametros["TelaEntradaDeTexto"]["Texto"],
        cor_selecionado=Cores["amarelo"],
        selecionada=SelecionadoEntrada
    )

    # Botão Enviar
    Botao(
        tela, "Enviar", (x_fundo + 30, y_fundo + 170, 350, 60),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: [f() for f in Enviar] if isinstance(Enviar, list) else Enviar(),
        Fontes[40], B1, eventos, som="Clique"
    )

    # Botão Voltar
    Botao(
        tela, "Voltar", (x_fundo + 420, y_fundo + 170, 350, 60),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: [f() for f in Voltar] if isinstance(Voltar, list) else Voltar(),
        Fontes[40], B2, eventos, som="Clique"
    )

B3 = {}
B4 = {}

def TelaDeCerteza(tela, estados, eventos, parametros):
    from Cenas.Inicio import Fontes, Cores, Texturas, Outros

    # Parâmetros esperados
    Recado = parametros.get("TelaDeCerteza", {}).get("Recado", "Tem certeza?")
    Funcao = parametros.get("TelaDeCerteza", {}).get("Funcao")
    Voltar = parametros.get("TelaDeCerteza", {}).get("Voltar")

    # Configurações de layout
    largura_fundo, altura_fundo = 800, 250
    x_fundo = (1920 - largura_fundo) // 2
    y_fundo = (1080 - altura_fundo) // 2
    fundo_rect = pygame.Rect(x_fundo, y_fundo, largura_fundo, altura_fundo)

    # Fundo preto
    pygame.draw.rect(tela, Cores["preto"], fundo_rect)

    # Texto central de confirmação
    texto = Fontes[40].render(Recado, True, Cores["branco"])
    texto_rect = texto.get_rect(center=(x_fundo + largura_fundo // 2, y_fundo + 60))
    tela.blit(texto, texto_rect)

    # Botão Sim
    Botao(
    tela, "Confirmar", (x_fundo + 100, y_fundo + 140, 250, 60),
    Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
    lambda: [f() for f in Funcao] if isinstance(Funcao, list) else Funcao(),
    Fontes[40], B3, eventos, som="Clique"
    )

    # Botão Não
    Botao(
        tela, "Cancelar", (x_fundo + 450, y_fundo + 140, 250, 60),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: [f() for f in Voltar] if isinstance(Voltar, list) else Voltar(),
        Fontes[40], B4, eventos, som="Clique"
    )
