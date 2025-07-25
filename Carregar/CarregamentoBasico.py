import pygame

from Prefabs.FunçõesPrefabs import Carregar_Imagem, Carregar_Frames

def CarregarTexturas():
    return {
        "AzulRoxa": Carregar_Imagem("Texturas/TexturaAzulRoxa.jpg"),
        "azul": Carregar_Imagem("Texturas/FundoAzul.jpg"),
        "vermelho": Carregar_Imagem("Texturas/FundoVermelho.jpg"),
        "roxo": Carregar_Imagem("Texturas/FundoRoxo.jpg"),
        "amarelo": Carregar_Imagem("Texturas/FundoAmarelo.jpg"),
        "verde": Carregar_Imagem("Texturas/FundoVerde.jpg"),
        "Cosmico": Carregar_Frames("Texturas/TexturaCosmica")
    }

def CarregarFundos():
    return {
        "FundoInicio": Carregar_Imagem("Fundos/FundoInicio.png")
        
    }

def CarregarOutros():
    return {
        "Logo": Carregar_Imagem("Outros/Logo.png",(750,750))
    }

def CarregamentoBasico(info):

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
    CAMINHO_FONTE = "Recursos/Visual/Fontes/FontePadrão.ttf"

    Fontes = [None] * 73  # Cria uma lista de 73 posições (índices de 0 a 72)

    for tamanho in [16, 20, 24, 25, 30, 35, 40, 50, 60, 72]:
        Fontes[tamanho] = pygame.font.Font(CAMINHO_FONTE, tamanho)

    
    from Carregar.CarregamentoBasico import CarregarFundos, CarregarTexturas, CarregarOutros

    Texturas = CarregarTexturas()
    Fundos = CarregarFundos()
    Outros = CarregarOutros()

    info["Conteudo"] = Cores, Fontes, Texturas, Fundos, Outros
    info["Carregado"] = True
