import pygame
import threading
import time

from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Modulos.ServerMundo import VerificaçãoSimplesServer, VerificaMapa
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda

from Codigo.Geradores.GeradorPlayer import Player
from Codigo.Geradores.GeradorMapa import Mapa, Camera
from Codigo.Geradores.GeradorEstruturas import GridToDic

Cores = None
Fontes = None
Texturas = None
Fundos = None
Outros = None
Pokemons = None
Estruturas = None
Equipaveis = None
Consumiveis = None
Animaçoes = None

player = None
mapa = None
camera = None

def thread_verificacao_continua(parametros):
    while parametros.get("Running", True):
        if parametros["Verificado"]:
            inicio = time.time()
            VerificaçãoSimplesServer(parametros)
            fim = time.time()
            parametros["Ping"] = round((fim - inicio) * 1000, 2)  # Ping em milissegundos
        else:
            time.sleep(3)

def MundoLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes, player, mapa, camera
    Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Consumiveis, Equipaveis, Estruturas, Animaçoes = info["Conteudo"]

    parametros = {
        "Link": info["Server"]["Link"],
        "Code": info["Server"]["Code"],
        "Ping": 0,
        "Verificado": True,
        "Running": True,   # flag para controle da thread
    }

    VerificaMapa(parametros)

    player = Player(info["Server"]["Player"]["dados"]["personagem"],Outros["Skins"])
    mapa = Mapa(parametros["GridBiomas"],GridToDic(parametros["GridObjetos"]))
    camera = Camera(55)

    parametros.update({"Loc": player.Loc})

    # Cria e inicia thread da verificação
    verif_thread = threading.Thread(target=thread_verificacao_continua, args=(parametros,), daemon=True)
    verif_thread.start()

    # tela = pygame.display.set_mode(camera.Resolucao, pygame.FULLSCREEN)

    while estados["Mundo"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Mundo"] = False
                estados["Rodando"] = False
                parametros["Running"] = False  # sinaliza para thread parar

        tela.fill((0, 0, 0))  # preto
        camera.desenhar(tela,player.Loc,mapa,Estruturas)
        player.Atualizar(tela)

        y_base = 10  # Posição inicial do topo
        espaco = 5   # Espaço entre as linhas

        if config["FPS Visivel"]:
            fps_atual = relogio.get_fps()
            texto = f"FPS: {fps_atual:.1f}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x, y_base), (255, 255, 255), (0, 0, 0))
            y_base += texto_surface.get_height() + espaco

        if config["Ping Visivel"]:
            texto = f"Ping: {parametros['Ping']:.1f}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x, y_base), (255, 255, 255), (0, 0, 0))
            y_base += texto_surface.get_height() + espaco

        if config["Cords Visiveis"]:
            x_cord = round(player.Loc[0], 1)
            y_cord = round(player.Loc[1], 1)
            texto = f" X:{x_cord} Y:{y_cord}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x, y_base), (255, 255, 255), (0, 0, 0))

        Clarear(tela, info)
        pygame.display.update()
        relogio.tick(config["FPS"])

    parametros["Running"] = False  # garante que a thread pare ao sair do loop
    verif_thread.join(timeout=1)
    
    Escurecer(tela, info)
    