import pygame

pygame.init()

# 🎨 CORES (RGB)
BRANCO      = (255, 255, 255)
PRETO       = (0, 0, 0)
CINZA       = (128, 128, 128)
VERMELHO    = (200, 0, 0)
VERDE       = (0, 200, 0)
AZUL        = (0, 0, 200)
AMARELO     = (255, 255, 0)
LARANJA     = (255, 140, 0)
ROXO        = (138, 43, 226)
ROSA        = (255, 105, 180)
AZUL_CLARO  = (173, 216, 230)
VERDE_CLARO = (144, 238, 144)
MARROM      = (139, 69, 19)

# Dicionário de cores (para acesso por string)
Cores = {
    "branco": BRANCO,
    "preto": PRETO,
    "cinza": CINZA,
    "vermelho": VERMELHO,
    "verde": VERDE,
    "azul": AZUL,
    "amarelo": AMARELO,
    "laranja": LARANJA,
    "roxo": ROXO,
    "rosa": ROSA,
    "azul_claro": AZUL_CLARO,
    "verde_claro": VERDE_CLARO,
    "marrom": MARROM,
}

# 🔠 FONTES
CAMINHO_FONTE = "Visual/Fontes/FontePadrão.ttf"

Fontes = {
    "fonte16": pygame.font.Font(CAMINHO_FONTE, 16),
    "fonte20": pygame.font.Font(CAMINHO_FONTE, 20),
    "fonte24": pygame.font.Font(CAMINHO_FONTE, 24),
    "fonte25": pygame.font.Font(CAMINHO_FONTE, 25),
    "fonte30": pygame.font.Font(CAMINHO_FONTE, 30),
    "fonte40": pygame.font.Font(CAMINHO_FONTE, 40),
    "fonte50": pygame.font.Font(CAMINHO_FONTE, 50),
    "fonte60": pygame.font.Font(CAMINHO_FONTE, 60),
    "fonte72": pygame.font.Font(CAMINHO_FONTE, 72),
}