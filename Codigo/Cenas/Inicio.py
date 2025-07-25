import pygame
import math

from Prefabs.BotoesPrefab import Botao, Botao_Selecao
from Prefabs.FunçõesPrefabs import Barra_De_Texto
from Prefabs.Animações import Animação
from Prefabs.Sonoridade import Musica
from Prefabs.Mensagens import adicionar_mensagem_passageira, mensagens_passageiras
from Modulos.Server import AdicionaServer, CarregarServers, ApagarServer, RenomearServer, EntrarServer
from Modulos.TelasGénericas import TelaEntradaDeTexto, TelaDeCerteza
from Modulos.Config import TelaConfigurações, aplicar_claridade

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

ConectandoGif = None
CriandoPersonagem = False

# Cores
BEGE = (245, 222, 179)

def desenhar_boneco(tela, centro, mouse_pos):
    x, y = centro

    # Calcular ângulo do boneco em relação ao mouse
    dx, dy = mouse_pos[0] - x, mouse_pos[1] - y
    angulo = math.atan2(dy, dx)

    # Tamanhos
    raio_corpo = 30
    raio_mao = 10
    dist_mao = 40  # distância do centro para as mãos

    # Corpo
    pygame.draw.circle(tela, BEGE, (x, y), raio_corpo)

    # Posições das mãos com rotação
    mao1_x = x + math.cos(angulo + math.pi / 2) * dist_mao
    mao1_y = y + math.sin(angulo + math.pi / 2) * dist_mao

    mao2_x = x + math.cos(angulo - math.pi / 2) * dist_mao
    mao2_y = y + math.sin(angulo - math.pi / 2) * dist_mao

    # Desenhar mãos
    pygame.draw.circle(tela, BEGE, (int(mao1_x), int(mao1_y)), raio_mao)
    pygame.draw.circle(tela, BEGE, (int(mao2_x), int(mao2_y)), raio_mao)

def InicioTelaPrincipal(tela, estados, eventos, parametros):

    Botao(
        tela, "JOGAR", (750, 560, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaJogar}),
        Fontes[40], B_jogar, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    Botao(
        tela, "CONFIGURAÇÕES", (750, 730, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": TelaConfigurações, "TelaConfigurações": {"Voltar":lambda: parametros.update({"Tela": InicioTelaPrincipal})}}),
        Fontes[40], B_config, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    Botao(
        tela, "SAIR", (750, 900, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: estados.update({"Inicio": False, "Rodando": False}),
        Fontes[40], B_sair, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    tela.blit(Outros["Logo"], (620, -120))

def InicioTelaJogar(tela, estados, eventos, parametros):
    # Botão para adicionar novo servidor
    Botao(
        tela, "Adicionar Novo Server", (655, 170, 610, 150),
        Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaNovoServer, "ServerSelecionado": None,}),
        Fontes[40], B_Adicionar, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    if parametros["Carregar"]:
        CarregarServers(parametros)
        parametros["Carregar"] = False

    base_x, base_y = 710, 350
    largura, altura = 500, 70
    espaçamento = 12
    max_servers = 7

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
    y_botoes = base_y + max_servers * (altura + espaçamento) + 20

    for i, nome in enumerate(botoes_labels):
        x = inicio_x + i * (largura_botao + espacamento_horizontal)

        Som = "Clique"
        if nome == "Voltar":
            funcao = lambda: parametros.update({"Tela": InicioTelaPrincipal, "ServerSelecionado": None,})
            textura = Texturas["azul"]
        else:
            server_selecionado = parametros.get("ServerSelecionado")
            if not server_selecionado:
                funcao = None
                textura = Cores["cinza"]
                Som = "Bloq"
            elif nome == "Entrar":
                funcao = lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Codigo de login do server", "Texto": "000", "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "ServerSelecionado": None,}), "Enviar": lambda: parametros.update({"Tela": InicioTelaConectando, "Code": str(parametros["TelaEntradaDeTexto"]["Texto"])})}})
                textura = Texturas["amarelo"]
            elif nome == "Renomear":
                funcao = [lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Digite o novo nome do server", "Texto": f"{server_selecionado["nome"]}", "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "ServerSelecionado": None,}), "Enviar": [lambda: RenomearServer(parametros["TelaEntradaDeTexto"]["Texto"], parametros["ServerSelecionado"]["link"]), lambda: adicionar_mensagem_passageira("Nome do Server Alterado com Sucesso"), lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True, "ServerSelecionado": None,})]}})]
                textura = Texturas["verde"]
            elif nome == "Apagar":
                funcao = lambda: parametros.update({"Tela": TelaDeCerteza, "TelaDeCerteza": {"Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "ServerSelecionado": None,}), "Funcao": [lambda: ApagarServer(server_selecionado["nome"]),lambda: parametros.update({"Tela": InicioTelaJogar}),lambda: adicionar_mensagem_passageira("Server Apagado com Sucesso"), lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True, "ServerSelecionado": None,})]}})
                textura = Texturas["vermelho"]
            elif nome == "Operar":
                funcao = lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Digite o codigo de operador so server", "Texto": "0000", "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True, "ServerSelecionado": None}), "Enviar": print("pass")}})
                textura = Texturas["roxo"]
            else:
                funcao = None
                textura = Cores["cinza"]

        Botao(
            tela, nome, (x, y_botoes, largura_botao, altura_botao),
            textura, Cores["preto"], Cores["branco"],
            funcao, Fontes[35], B1, eventos, som=Som
        )

    if parametros["Tela"] != InicioTelaJogar:
        EstadoSeleçãoServer["selecionado_esquerdo"] = None

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

def InicioTelaConectando(tela, estados, eventos, parametros):
    global ConectandoGif

    if ConectandoGif is None:
        ConectandoGif = Animação(Outros["Conectando"], (960, 520))

    ConectandoGif.atualizar(tela)

    # --- TEXTO CENTRAL SUPERIOR ---
    texto = Fontes[50].render("Conectando ao servidor", True, Cores["branco"])
    texto_rect = texto.get_rect(center=(960, 80))  # Centralizado no topo
    tela.blit(texto, texto_rect)

    # --- BOTÃO VOLTAR ---
    Botao(
        tela, "Voltar", (800, 700, 320, 80),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaJogar}),
        Fontes[40], B_Voltar, eventos, som="Clique"
    )

    desenhar_boneco(tela, (300, 45), pygame.mouse.get_pos())


# def InicioTelaCriandoPersonagem(tela, estados, eventos, parametros):
#     global CriandoPersonagem

#     if CriandoPersonagem is False:
#         CriandoPersonagem = True
#         parametros.update("Personagem": {
#             "Nome":
#             "Sexo":
#             "Estilo":
#             "Inicial":

#         })

#     Botao_Selecao(
#                 tela=tela,
#                 texto="",
#                 espaço=(),
#                 Fonte=None],
#                 cor_fundo=Texturas["AzulRoxa"],
#                 cor_borda_normal=Cores["preto"],
#                 cor_passagem=Cores["branco"],
#                 cor_borda_esquerda=Cores["vermelho"],
#                 funcao_esquerdo=lambda s=server: parametros.update({"ServerSelecionado": s}),
#                 desfazer_esquerdo=lambda s=server: parametros.update({"ServerSelecionado": None}),
#                 funcao_direito=None,
#                 id_botao=server["link"],
#                 estado_global=EstadoSeleçãoServer,
#                 eventos=eventos,
#                 som="Clique"
#             )

def InicioLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros 
    Cores, Fontes, Texturas, Fundos, Outros = info["Conteudo"]

    parametros = {
        "Tela": InicioTelaPrincipal,
        "Servers": [],
        "ServerSelecionado": None,
        "NomeServer": "Novo Server",
        "LinkServer": "Link do Server",
        "Carregar": False,
        "Config": config,
        "TelaEntradaTexto": {"Texto": ""}
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

        for msg in mensagens_passageiras:
            msg.atualizar()
            msg.desenhar(tela)
        mensagens_passageiras[:] = [msg for msg in mensagens_passageiras if msg.ativa]

        if config["FPS Visivel"]:
            fps_atual = relogio.get_fps()
            texto_fps = Fontes[30].render(f"FPS: {fps_atual:.1f}", True, (255, 255, 255))
            tela.blit(texto_fps, (tela.get_width() - texto_fps.get_width() - 10, 10))

        aplicar_claridade(tela,config["Claridade"])
        pygame.display.update()
        relogio.tick(config["FPS"])
        