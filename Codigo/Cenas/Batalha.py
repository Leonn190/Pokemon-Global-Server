import pygame

def BatalhaLoop(tela, relogio, estados, config, info):

    while estados["Batalha"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Batalha"] = False
                estados["Rodando"] = False

        pygame.display.update()
        relogio.tick(config["FPS"])
