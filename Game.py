import pygame
import sys
import ctypes

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
    "Fps": 100,
    "Volume": 0.5
}

from Cenas.Inicio import InicioLoop
from Cenas.Carregamento import CarregamentoLoop
from Cenas.Mundo import MundoLoop 
from Cenas.Batalha import BatalhaLoop

estados = {
    "Rodando": True,
    "Inicio": True,
    "Carregamento": False,
    "Mundo": False,
    "Batalha": False
}

while estados["Rodando"]:
    if estados["Inicio"]:
        InicioLoop(tela, relogio, estados, config)

    elif estados["Carregamento"]:
        CarregamentoLoop(tela, relogio, estados, config)

    elif estados["Mundo"]:
        MundoLoop(tela, relogio, estados, config)

    elif estados["Batalha"]:
        BatalhaLoop(tela, relogio, estados, config)

pygame.quit()
sys.exit()