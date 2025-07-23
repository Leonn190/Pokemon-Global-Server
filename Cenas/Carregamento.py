import pygame

def CarregamentoLoop(tela, relogio, estados, config):

    while estados["Carregamento"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Carregamento"] = False
                estados["Rodando"] = False

        pygame.display.update()
        relogio.tick(config["FPS"])