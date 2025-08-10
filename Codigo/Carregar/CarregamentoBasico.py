import pygame
from Codigo.Prefabs.FunçõesPrefabs import Carregar_Imagem, Carregar_Frames

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
        "FundoInicio": Carregar_Imagem("Fundos/FundoInicio.png"),
        "FundoPersonagem": Carregar_Imagem("Fundos/FundoPersonagem.jpg"),
        "FundoQuadradoNeutro": Carregar_Imagem("Fundos/FundoQuadradoNeutro.jpg")
        
    }

def CarregarOutros():
    return {
        "Logo": Carregar_Imagem("Outros/Logo.png",(750,750)),
        "Conectando": Carregar_Frames("Outros/Conectando_Frames"),

        "Skins": [None] + [Carregar_Imagem(f"Skins/Liberadas/S{i}.png") for i in range(1, 13)],

        "PokemonsIniciais": {
        "Charmander": Carregar_Imagem("Pokemons/Imagens/charmander.png"),
        "Torchic": Carregar_Imagem("Pokemons/Imagens/torchic.png"),
        "Fennekin": Carregar_Imagem("Pokemons/Imagens/fennekin.png"),
        "Litten": Carregar_Imagem("Pokemons/Imagens/litten.png"),
        
        "Bulbasaur": Carregar_Imagem("Pokemons/Imagens/bulbasaur.png"),
        "Treecko": Carregar_Imagem("Pokemons/Imagens/treecko.png"),
        "Chespin": Carregar_Imagem("Pokemons/Imagens/chespin.png"),
        "Rowlet": Carregar_Imagem("Pokemons/Imagens/rowlet.png"),
        
        "Squirtle": Carregar_Imagem("Pokemons/Imagens/squirtle.png"),
        "Mudkip": Carregar_Imagem("Pokemons/Imagens/mudkip.png"),
        "Froakie": Carregar_Imagem("Pokemons/Imagens/froakie.png"),
        "Popplio": Carregar_Imagem("Pokemons/Imagens/popplio.png"),

        "CharmanderGif": Carregar_Frames("Pokemons/Animação/charmander"),
        "TorchicGif": Carregar_Frames("Pokemons/Animação/torchic"),
        "FennekinGif": Carregar_Frames("Pokemons/Animação/fennekin"),
        "LittenGif": Carregar_Frames("Pokemons/Animação/litten"),

        "BulbasaurGif": Carregar_Frames("Pokemons/Animação/bulbasaur"),
        "TreeckoGif": Carregar_Frames("Pokemons/Animação/treecko"),
        "ChespinGif": Carregar_Frames("Pokemons/Animação/chespin"), 
        "RowletGif": Carregar_Frames("Pokemons/Animação/rowlet"),

        "SquirtleGif": Carregar_Frames("Pokemons/Animação/squirtle"),
        "MudkipGif": Carregar_Frames("Pokemons/Animação/mudkip"),
        "FroakieGif": Carregar_Frames("Pokemons/Animação/froakie"),
        "PopplioGif": Carregar_Frames("Pokemons/Animação/popplio"),
    }
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
        "marrom": MARROM,}

    # 🔠 FONTES
    CAMINHO_FONTE = "Recursos/Visual/Fontes/FontePadrão.ttf"
    CAMINHO_FONTE2 = "Recursos/Visual/Fontes/FonteTextos.ttf"

    Fontes = [None] * 102  # Cria uma lista de 73 posições (índices de 0 a 72)

    for tamanho in [16, 20, 24, 25, 30, 35, 40, 50, 60, 72, 100]:
        Fontes[tamanho] = pygame.font.Font(CAMINHO_FONTE, tamanho)
    Fontes[101] = pygame.font.Font(CAMINHO_FONTE2, 18)

    Texturas = CarregarTexturas()
    Fundos = CarregarFundos()
    Outros = CarregarOutros()

    info["Conteudo"] = Cores, Fontes, Texturas, Fundos, Outros
    info["Carregado"] = True
