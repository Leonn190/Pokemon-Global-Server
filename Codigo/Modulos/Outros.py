import pygame, math

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

def FecharIris(tela, Info, cor=(0, 0, 0), velocidade=3, fps=120, borda_suave=0):
    """
    Transição 'iris close': escuro avança das bordas até o centro, deixando um
    círculo de clareza que encolhe até 0.
    - Usa Info["Escuro"] de 0 a 100 (incrementa até 100).
    - velocidade: quanto Info["Escuro"] sobe por frame (como em Escurecer).
    - borda_suave: largura (px) da transição suave na borda do círculo (0 = dura).
    """
    clock = pygame.time.Clock()
    w, h = tela.get_size()
    cx, cy = w // 2, h // 2

    # raio máximo: distância ao canto mais distante (garante cobertura total)
    max_radius = int(math.hypot(w * 0.5, h * 0.5))

    # garante a chave
    if "Escuro" not in Info:
        Info["Escuro"] = 0

    while Info["Escuro"] < 100:
        # avança progresso (0..100)
        Info["Escuro"] += velocidade
        if Info["Escuro"] > 100:
            Info["Escuro"] = 100

        # 0% => raio máximo (nada escuro) ; 100% => raio 0 (tela toda escura)
        t = Info["Escuro"] / 100.0
        r = max(0, int(round(max_radius * (1.0 - t))))

        # overlay com alpha por pixel
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        # todo o overlay preto opaco
        overlay.fill((*cor, 255))

        # "fura" um círculo transparente no centro (área visível)
        pygame.draw.circle(overlay, (0, 0, 0, 0), (cx, cy), r)

        # opcional: borda suave (feather) para o círculo
        if borda_suave > 0 and r > 0:
            # desenha alguns anéis com alpha crescente para suavizar a borda
            steps = max(4, min(24, borda_suave // 2))
            for i in range(1, steps + 1):
                rr = r + i
                # alpha cresce do 0 (no limite interno) até ~200
                a = int(200 * (i / steps))
                pygame.draw.circle(overlay, (*cor, a), (cx, cy), rr, width=1)

        # aplica na tela atual (sem redesenhar o mundo, igual ao Escurecer)
        tela.blit(overlay, (0, 0))
        pygame.display.update()
        clock.tick(fps)