import pygame
from Prefabs.FunçõesPrefabs import Carregar_Frames, Carregar_Imagem
from Prefabs.Animações import Animação

CarregandoGif = None

def CarregamentoLoop(tela, relogio, estados, config, info):
    global CarregandoGif

    if CarregandoGif is None:
        CarregandoGif = Animação(Carregar_Frames("Outros/Carregando_Frames"),(960,520))
    
    Fundo = Carregar_Imagem("Fundos/FundoCarregamento.jpg",(1920,1080))

    while estados["Carregamento"]:

        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Carregamento"] = False
                estados["Rodando"] = False

        tela.blit(Fundo,(0,0))
        CarregandoGif.atualizar(tela)

        if info["Carregado"]:
            estados["Carregamento"] = False
            estados[info["Alvo"]] = True
            info["Carregado"] = False
            info["Alvo"] = None

        pygame.display.update()
        relogio.tick(config["FPS"])