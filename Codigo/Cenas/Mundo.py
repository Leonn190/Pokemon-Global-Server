import pygame
import threading
import time

from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Modulos.ServerMundo import VerificaçãoSimplesServer, VerificaMapa

Cores = None
Fontes = None
Texturas = None
Fundos = None
Outros = None
Pokemons = None
Estruturas = None
Equipaveis = None
Consumiveis = None

def thread_verificacao_continua(parametros):
    while parametros.get("Running", True):
        if parametros["Verificado"]:
            VerificaçãoSimplesServer(parametros)
            time.sleep(0.2)
        else:
            time.sleep(3)

def MundoLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis
    Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Consumiveis, Equipaveis, Estruturas = info["Conteudo"]

    parametros = {
        "Link": info["Server"]["Link"],
        "Player": info["Server"]["Player"]["dados"]["personagem"],
        "Code": info["Server"]["Code"],
        "Loc": info["Server"]["Player"]["dados"]["personagem"]["Loc"],
        "Verificado": True,
        "Running": True,   # flag para controle da thread
    }

    VerificaMapa(parametros)

    # Cria e inicia thread da verificação
    verif_thread = threading.Thread(target=thread_verificacao_continua, args=(parametros,), daemon=True)
    verif_thread.start()

    while estados["Mundo"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Mundo"] = False
                estados["Rodando"] = False
                parametros["Running"] = False  # sinaliza para thread parar

        Clarear(tela, info)
        pygame.display.update()
        relogio.tick(config["FPS"])

    parametros["Running"] = False  # garante que a thread pare ao sair do loop
    verif_thread.join(timeout=1)
    
    Escurecer(tela, info)
    