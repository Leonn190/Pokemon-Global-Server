import pygame

def InicioLoop(tela, relogio, estados, config):

    while estados["Inicio"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Inicio"] = False
                estados["Rodando"] = False

        pygame.display.update()
        relogio.tick(config["FPS"])