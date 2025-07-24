import pygame

from Prefabs.FunçõesPrefabs import Botao, Barra_De_Texto, Botao_Selecao
from Prefabs.Animações import Animação
from Prefabs.Sonoridade import Musica
from Modulos.Server import AdicionaServer, CarregarServers, ApagarServer, RenomearServer
from Modulos.TelasGénericas import TelaEntradaDeTexto, TelaDeCerteza

B1 = {}

B_jogar = {}
B_config = {}
B_sair = {}
B_Adicionar = {}
B_Salvar = {}
B_Voltar = {}

EstadoSeleçãoServer = {"selecionado_esquerdo": None}

Cores = None
Fontes = None
Texturas = None
Fundos = None
Outros = None

SelecionadoNome = False
SelecionadoLink = False

def InicioTelaPrincipal(tela, estados, eventos, parametros):

    Botao(
        tela, "JOGAR", (750, 550, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaJogar}),
        Fontes[40], B_jogar, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    Botao(
        tela, "CONFIGURAÇÕES", (750, 710, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": False}),
        Fontes[40], B_config, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    Botao(
        tela, "SAIR", (750, 870, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: estados.update({"Inicio": False, "Rodando": False}),
        Fontes[40], B_sair, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    tela.blit(Outros["Logo"], (620, -120))

def InicioTelaJogar(tela, estados, eventos, parametros):
    # Botão para adicionar novo servidor
    Botao(
        tela, "Adicionar Novo Server", (640, 170, 610, 150),
        Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaNovoServer}),
        Fontes[40], B_Adicionar, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    if parametros["Carregar"]:
        CarregarServers(parametros)
        parametros["Carregar"] = False

    base_x, base_y = 710, 360
    largura, altura = 500, 100
    espaçamento = 20
    max_servers = 5

    # Mostrar servidores ou mensagem de vazio
    if not parametros["Servers"]:
        texto = Fontes[50].render("Nenhum server adicionado ainda", True, Cores["branco"])
        rect = texto.get_rect(center=(1920 // 2, base_y + ((altura + espaçamento) * max_servers) // 2))
        tela.blit(texto, rect)
    else:
        for i, server in enumerate(parametros["Servers"][:max_servers]):
            y_atual = base_y + i * (altura + espaçamento)
            Botao_Selecao(
                tela=tela,
                texto=server["nome"],
                espaço=(base_x, y_atual, largura, altura),
                Fonte=Fontes[35],
                cor_fundo=Texturas["AzulRoxa"],
                cor_borda_normal=Cores["preto"],
                cor_passagem=Cores["branco"],
                cor_borda_esquerda=Cores["vermelho"],
                funcao_esquerdo=lambda s=server: parametros.update({"ServerSelecionado": s}),
                desfazer_esquerdo=lambda s=server: parametros.update({"ServerSelecionado": None}),
                funcao_direito=None,
                id_botao=server["link"],
                estado_global=EstadoSeleçãoServer,
                eventos=eventos,
                som="Clique"
            )

    # Botões inferiores
    botoes_labels = ["Voltar", "Entrar", "Renomear", "Apagar", "Operar"]
    total_botoes = len(botoes_labels)
    largura_botao = 230
    altura_botao = 70
    espacamento_horizontal = 25
    total_largura = total_botoes * largura_botao + (total_botoes - 1) * espacamento_horizontal
    inicio_x = (1920 - total_largura) // 2
    y_botoes = base_y + max_servers * (altura + espaçamento) + 30

    for i, nome in enumerate(botoes_labels):
        x = inicio_x + i * (largura_botao + espacamento_horizontal)

        if nome == "Voltar":
            funcao = lambda: parametros.update({"Tela": InicioTelaPrincipal})
            textura = Texturas["azul"]
        else:
            server_selecionado = parametros.get("ServerSelecionado")
            if not server_selecionado:
                funcao = None
                textura = Cores["cinza"]
            elif nome == "Entrar":
                funcao = lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Codigo de login do server", "Texto": "000", "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar}), "Enviar": print("pass")}})
                textura = Texturas["amarelo"]
            elif nome == "Renomear":
                funcao = [lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Digite o novo nome do server", "Texto": f"{server_selecionado["nome"]}", "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True}), "Enviar": RenomearServer, "Info1": server_selecionado["link"]}})]
                textura = Texturas["verde"]
            elif nome == "Apagar":
                funcao = lambda: parametros.update({"Tela": TelaDeCerteza, "TelaDeCerteza": {"Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True}), "Funcao": [lambda: ApagarServer(server_selecionado["nome"]),lambda: parametros.update({"Tela": InicioTelaJogar})]}})
                textura = Texturas["vermelho"]
            elif nome == "Operar":
                funcao = lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Digite o codigo de operador so server", "Texto": "0000", "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True}), "Enviar": print("pass")}})
                textura = Texturas["roxo"]
            else:
                funcao = None
                textura = Cores["cinza"]

        Botao(
            tela, nome, (x, y_botoes, largura_botao, altura_botao),
            textura, Cores["preto"], Cores["branco"],
            funcao, Fontes[35], B1, eventos, som="Clique"
        )

def InicioTelaNovoServer(tela, estados, eventos, parametros):
    global SelecionadoNome, SelecionadoLink

    largura_fundo, altura_fundo = 800, 400
    x_fundo = (1920 - largura_fundo) // 2
    y_fundo = (1080 - altura_fundo) // 2
    fundo_rect = pygame.Rect(x_fundo, y_fundo, largura_fundo, altura_fundo)
    pygame.draw.rect(tela, Cores["preto"], fundo_rect)

    nome_texto = Fontes[40].render("Nome do Servidor:", True, Cores["branco"])
    link_texto = Fontes[40].render("Link do Servidor:", True, Cores["branco"])
    tela.blit(nome_texto, (x_fundo + 30, y_fundo + 30))
    tela.blit(link_texto, (x_fundo + 30, y_fundo + 160))

    parametros["NomeServer"], SelecionadoNome = Barra_De_Texto(
        tela,
        (x_fundo + 30, y_fundo + 80, 740, 50),
        Fontes[40],
        Cores["cinza"],
        Cores["branco"],
        Cores["branco"],
        eventos,
        parametros.get("NomeServer", ""),
        cor_selecionado=Cores["amarelo"],
        selecionada=SelecionadoNome
    )

    parametros["LinkServer"], SelecionadoLink = Barra_De_Texto(
        tela,
        (x_fundo + 30, y_fundo + 210, 740, 50),
        Fontes[40],
        Cores["cinza"],
        Cores["branco"],
        Cores["branco"],
        eventos,
        parametros.get("LinkServer", ""),
        cor_selecionado=Cores["amarelo"],
        selecionada=SelecionadoLink
    )

    Botao(
        tela, "Salvar", (x_fundo + 30, y_fundo + 310, 350, 60),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        [lambda: AdicionaServer(parametros["NomeServer"], parametros["LinkServer"]),lambda: parametros.update({"Tela": InicioTelaJogar,"NomeServer": "Novo Server", "LinkServer": "Link do Server", "Carregar": True})],
        Fontes[40], B_Salvar, eventos, som="Clique"
    )
    Botao(
        tela, "Voltar", (x_fundo + 420, y_fundo + 310, 350, 60),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaJogar,"NomeServer": "Novo Server", "LinkServer": "Link do Server", "Carregar": True}),
        Fontes[40], B_Voltar, eventos, som="Clique"
    )
    
def InicioLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros 
    Cores, Fontes, Texturas, Fundos, Outros = info["Conteudo"]

    parametros = {
        "Tela": InicioTelaPrincipal,
        "Servers": [],
        "ServerSelecionado": None,
        "NomeServer": "Novo Server",
        "LinkServer": "Link do Server",
        "Carregar": False
    }

    x = 0
    reverse = False  # começa indo pra esquerda
    LIMITE_ESQUERDA = -1520  # vai até -1520 (3440 - 1920)

    CarregarServers(parametros)
    Musica("MusicaTema")

    while estados["Inicio"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Inicio"] = False
                estados["Rodando"] = False

        # Atualiza reversão de direção
        if x <= LIMITE_ESQUERDA:
            reverse = True
        elif x >= 0:
            reverse = False

        # Desenha fundo com deslocamento e corte vertical
        tela.blit(Fundos["FundoInicio"], (round(x), -360))

        # Chama tela atual
        parametros["Tela"](tela, estados, eventos, parametros)

        # Atualiza movimento
        if reverse:
            x += 0.35  # volta para a direita
        else:
            x -= 0.35  # vai para a esquerda

        pygame.display.update()
        relogio.tick(config["FPS"])