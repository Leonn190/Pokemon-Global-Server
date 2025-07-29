import pygame
from Codigo.Modulos.Outros import Clarear, Escurecer

def BatalhaLoop(tela, relogio, estados, config, info):

    while estados["Batalha"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Batalha"] = False
                estados["Rodando"] = False

        Clarear(tela,info)
        pygame.display.update() 
        relogio.tick(config["FPS"])
    
    Escurecer(tela,info)
