import pygame
import sys
import ctypes
import threading

from Prefabs.Sonoridade import VerificaSonoridade

try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

pygame.init()
pygame.mixer.init()

tela = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("Jogo Pokémon")

relogio = pygame.time.Clock()

config = {
    "FPS": 100,
    "Volume": 0.5,
    "Mudo": False
}

VerificaSonoridade(config)

info = {
    "Carregado": False,
    "Alvo": "Inicio"
}

from Cenas.Inicio import InicioLoop
from Cenas.Carregamento import CarregamentoLoop
from Cenas.Mundo import MundoLoop 
from Cenas.Batalha import BatalhaLoop

from Prefabs.Aspectos import CarregamentoBasico

estados = {
    "Rodando": True,
    "Inicio": False,
    "Carregamento": True,
    "Mundo": False,
    "Batalha": False
}

# Inicia o carregamento básico em paralelo
carregamento_thread = threading.Thread(target=CarregamentoBasico, args=(info,))
carregamento_thread.start()

while estados["Rodando"]:

    if estados["Inicio"]:
        InicioLoop(tela, relogio, estados, config, info)

    elif estados["Carregamento"]:
        CarregamentoLoop(tela, relogio, estados, config, info)

    elif estados["Mundo"]:
        MundoLoop(tela, relogio, estados, config, info)

    elif estados["Batalha"]:
        BatalhaLoop(tela, relogio, estados, config, info)

pygame.quit()
sys.exit()