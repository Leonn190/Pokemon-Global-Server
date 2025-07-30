import pygame

def Clarear(tela, Info, cor=(0, 0, 0), velocidade=3):
    """
    Clareia gradualmente a tela, reduzindo Info["Escuro"] até 0.
    Deve ser chamada a cada frame dentro do loop principal.
    """
    if Info["Escuro"] > 0:
        Info["Escuro"] -= velocidade
        if Info["Escuro"] < 0:
            Info["Escuro"] = 0

        alpha = int((Info["Escuro"] / 100) * 255)
        camada = pygame.Surface(tela.get_size()).convert_alpha()
        camada.fill((*cor, alpha))
        tela.blit(camada, (0, 0))

def Escurecer(tela, Info, cor=(0, 0, 0), velocidade=3, fps=70):
    """
    Escurece a tela até Info["Escuro"] chegar a 100.
    Possui seu próprio loop bloqueante.
    """
    clock = pygame.time.Clock()
    largura, altura = tela.get_size()

    while Info["Escuro"] < 100:
        Info["Escuro"] += velocidade
        if Info["Escuro"] > 100:
            Info["Escuro"] = 100

        # Redesenhar camada
        alpha = int((Info["Escuro"] / 100) * 255)
        camada = pygame.Surface((largura, altura)).convert_alpha()
        camada.fill((*cor, alpha))

        tela.blit(camada, (0, 0))
        pygame.display.update()
        clock.tick(fps)
        