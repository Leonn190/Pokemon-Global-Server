import pygame
from Codigo.Modulos.Outros import Clarear, Escurecer

Cores = None
Fontes = None
Texturas = None
Fundos = None
Outros = None
Pokemons = None
Estruturas = None
Equipaveis = None
Consumiveis = None

def MundoLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis
    Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Consumiveis, Equipaveis, Estruturas = info["Conteudo"]

    parametros = {
        "Link": info["Server"]["Link"],
        "Player": info["Server"]["Player"],
        "Code": info["Server"]["Code"],
        "Loc": info["Server"]["Player"]["Loc"],
        "GridBiomas": None
    }


    while estados["Mundo"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Mundo"] = False
                estados["Rodando"] = False

        Clarear(tela,info)
        pygame.display.update() 
        relogio.tick(config["FPS"])
    
    Escurecer(tela,info)
    