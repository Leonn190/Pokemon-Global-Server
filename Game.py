import pygame
import sys
import os
import ctypes
import threading

from Codigo.Prefabs.Sonoridade import VerificaSonoridade
from Codigo.Prefabs.FunçõesPrefabs import Carregar_Imagem

try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

pygame.init()
pygame.mixer.init()

# Iniciar tela
tela = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
pygame.display.set_caption("Pokemon Global Server")

# Ícone da janela (funciona com PNG)
icone = Carregar_Imagem("Outros/Logo.png")  # ou use sua função Carregar_Imagem
pygame.display.set_icon(icone)

relogio = pygame.time.Clock()

config = {
    "FPS": 100, 
    "Volume": 0.5,
    "Claridade": 75,
    "Mudo": False,
    "FPS Visivel": False,
    "Cords Visiveis": False,
    "Ping Visivel": False,
    "Pré-Carregamento": False
}

if os.path.exists("ConfigFixa.py"):
    try:
        from ConfigFixa import Config as ConfigSalva
        config = ConfigSalva
    except Exception as e:
        pass  # Silenciosamente ignora erro

VerificaSonoridade(config)

config.update({"Ver": 1.0})

info = {
    "Carregado": False,
    "Alvo": "Inicio",
    "Escuro": 100
}

from Outros.Discord import iniciar_discord_presence
rpc = iniciar_discord_presence()

from Codigo.Cenas.Inicio import InicioLoop
from Codigo.Cenas.Carregamento import CarregamentoLoop
from Codigo.Cenas.Mundo import MundoLoop 
from Codigo.Cenas.Batalha import BatalhaLoop

from Codigo.Carregar.CarregamentoBasico import CarregamentoBasico

estados = {
    "Rodando": True,
    "Inicio": False,
    "Carregamento": True,
    "Mundo": False,
    "PreBatalha": False,
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
