import pygame
import os

from Prefabs.FunçõesPrefabs import Botao, Barra_De_Texto
from Prefabs.Animações import Animação

B1 = {}

Cores = None
Fontes = None
Texturas = None
Fundos = None
Outros = None

Servers = []

SelecionadoNome = False
SelecionadoLink = False

def AdicionaServer(Nome, Link):
    # Garante que a pasta Servers existe
    os.makedirs("Servers", exist_ok=True)

    # Garante que o nome do arquivo seja válido (sem espaços ou símbolos)
    nome_arquivo = "".join(c if c.isalnum() else "_" for c in Nome)

    caminho = os.path.join("Servers", f"{nome_arquivo}.py")

    # Conteúdo do arquivo
    conteudo = f"server = {{'nome': {repr(Nome)}, 'link': {repr(Link)}}}\n"

    # Cria o arquivo com o dicionário
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)

def InicioTelaInicial(tela, estados, eventos, parametros):

    Botao(
        tela, "JOGAR", (760, 550, 400, 80), Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaJogar}),
        Fontes[40], B1, eventos, som="Jogar"
    )

    Botao(
        tela, "CONFIGURAÇÔES", (760, 660, 400, 80), Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": False}),
        Fontes[40], B1, eventos, som="Jogar"
    )

    Botao(
        tela, "SAIR", (760, 770, 400, 80), Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: estados.update({"Inicio": False, "Rodando": False}),
        Fontes[40], B1, eventos, som="Jogar"
    )

    tela.blit(Outros["Logo"], (635, -35))

def InicioTelaJogar(tela, estados, eventos, parametros):

    if Servers == []:
        Botao(
        tela, "Adicionar Novo Server", (710, 300, 500, 120), Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaNovoServer}),
        Fontes[40], B1, eventos, som="Jogar"
    )
    
    else:

def InicioTelaNovoServer(tela, estados, eventos, parametros):

    parametros["NomeServer"], SelecionadoNome = Barra_De_Texto()
    parametros["LinkServer"], SelecionadoLink = Barra_De_Texto()
    

def InicioLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros 
    Cores, Fontes, Texturas, Fundos, Outros = info["Conteudo"]
    
    Fundo = Animação(Fundos["FundoInicio"],(960,540),ping_pong=True)

    parametros = {
        "Tela": InicioTelaInicial,
        "Server": None,
        "NomeServer": "Novo Server",
        "LinkServer": "Link do Server"
    }

    while estados["Inicio"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Inicio"] = False
                estados["Rodando"] = False

        Fundo.atualizar(tela)

        parametros["Tela"](tela, estados, eventos, parametros)

        pygame.display.update()
        relogio.tick(config["FPS"])