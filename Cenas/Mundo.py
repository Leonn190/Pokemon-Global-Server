import pygame

def MundoLoop(tela, relogio, estados, config):

    while estados["Mundo"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Mundo"] = False
                estados["Rodando"] = False

        pygame.display.update()
        relogio.tick(config["FPS"])