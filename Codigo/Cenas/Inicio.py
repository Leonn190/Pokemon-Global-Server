import pygame
import threading
import requests
import time

from Codigo.Prefabs.BotoesPrefab import Botao, Botao_Selecao, Botao_Alavanca
from Codigo.Prefabs.FunçõesPrefabs import Barra_De_Texto, DesenharPlayer, Slider, texto_com_borda
from Codigo.Prefabs.Animações import Animação
from Codigo.Prefabs.Sonoridade import Musica
from Codigo.Prefabs.Mensagens import adicionar_mensagem_passageira, mensagens_passageiras
from Codigo.Modulos.ServerInicio import AdicionaServer, CarregarServers, ApagarServer, RenomearServer, EntrarServer, RegistrarNoServer, VerificaOperador, ObterEstadoServidor, AtivarServidor, LigarDesligarServidor, ResetarServidor
from Codigo.Modulos.TelasGénericas import TelaEntradaDeTexto, TelaDeCerteza
from Codigo.Modulos.Config import TelaConfigurações, aplicar_claridade
from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Carregar.CarregamentoAvançado import CarregamentoAvançado

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

Inicial = None
PokemonDestaque = None

def InicioTelaPrincipal(tela, estados, eventos, parametros):

    Botao(
        tela, "JOGAR", (750, 560, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaJogar}),
        Fontes[40], B_jogar, eventos, som="Clique", cor_texto=Cores["branco"], aumento=1.2
    )

    Botao(
        tela, "CONFIGURAÇÕES", (750, 730, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": TelaConfigurações, "TelaConfigurações": {"Voltar":lambda: parametros.update({"Tela": InicioTelaPrincipal}), "Entrou": True}}),
        Fontes[40], B_config, eventos, som="Clique", cor_texto=Cores["branco"], aumento=1.2
    )

    Botao(
        tela, "SAIR", (750, 900, 420, 125), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: estados.update({"Inicio": False, "Rodando": False}),
        Fontes[40], B_sair, eventos, som="Clique", cor_texto=Cores["branco"], aumento=1.2
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
                funcao = lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Codigo de login do server", "Texto": "","Limite": 3, "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "ServerSelecionado": None,}), "Enviar": lambda: parametros.update({"Tela": InicioTelaConectando, "Code": str(parametros["TelaEntradaDeTexto"]["Texto"])})}})
                textura = Texturas["amarelo"]
            elif nome == "Renomear":
                funcao = [lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Digite o novo nome do server", "Texto": f"{server_selecionado["nome"]}", "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "ServerSelecionado": None,}), "Enviar": [lambda: RenomearServer(parametros["TelaEntradaDeTexto"]["Texto"], parametros["ServerSelecionado"]["link"]), lambda: adicionar_mensagem_passageira("Nome do Server Alterado com Sucesso"), lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True, "ServerSelecionado": None,})]}})]
                textura = Texturas["verde"]
            elif nome == "Apagar":
                funcao = lambda: parametros.update({"Tela": TelaDeCerteza, "TelaDeCerteza": {"Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "ServerSelecionado": None,}), "Funcao": [lambda: ApagarServer(server_selecionado["nome"]),lambda: parametros.update({"Tela": InicioTelaJogar}),lambda: adicionar_mensagem_passageira("Server Apagado com Sucesso"), lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True, "ServerSelecionado": None,})]}})
                textura = Texturas["vermelho"]
            elif nome == "Operar":
                funcao = lambda: parametros.update({"Tela": TelaEntradaDeTexto, "TelaEntradaDeTexto": {"Rotulo": "Digite o codigo de operador so server", "Texto": "","Limite": 4, "Voltar": lambda: parametros.update({"Tela": InicioTelaJogar, "Carregar": True, "ServerSelecionado": None}), "Enviar": lambda: parametros.update({"Tela": InicioTelaOperador, "OperadorCode": parametros["TelaEntradaDeTexto"]["Texto"]})}})
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
    global ConectandoGif, CriandoPersonagem

    CriandoPersonagem = False

    if ConectandoGif is None:
        ConectandoGif = Animação(Outros["Conectando"], (960, 520))
    
    if parametros["TentarEntrarNoServidor"]:
        parametros["TentarEntrarNoServidor"] = False
        parametros["EstadoServidor"] = None  # inicializa o estado
        parametros["TempoInicioConexao"] = pygame.time.get_ticks()  # tempo em ms
        threading.Thread(target=lambda: requests.get(f"{parametros['ServerSelecionado']['link']}/verifica-servidor-ativo"),daemon=True).start()
        threading.Thread(target=EntrarServer, args=(parametros["Code"], parametros), daemon=True).start()

    ConectandoGif.atualizar(tela)

    # --- TEXTO CENTRAL SUPERIOR ---
    texto = Fontes[60].render("Conectando ao servidor", True, Cores["branco"])
    texto_rect = texto.get_rect(center=(960, 80))  # Centralizado no topo
    tela.blit(texto, texto_rect)

    # --- BOTÃO VOLTAR ---
    Botao(
        tela, "Voltar", (800, 700, 320, 80),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": InicioTelaJogar, "TentarEntrarNoServidor": True, "ServerSelecionado": None}),
        Fontes[40], B_Voltar, eventos, som="Clique"
    )

    estado = parametros.get("EstadoServidor")
    tempo_decorrido_ms = pygame.time.get_ticks() - parametros.get("TempoInicioConexao", 0)

    if estado is None or tempo_decorrido_ms < 1000:  # 6000 ms = 6 segundos
        # Ainda esperando resposta OU não completou 6 segundos
        pass
    else:
        status = estado.get("status")
        if status == 201:
            estados.update({"Inicio": False, "Carregamento": True})
        elif status == 200:
            parametros.update({"Tela": InicioTelaJogar, "TentarEntrarNoServidor": True, "ServerSelecionado": None})
            adicionar_mensagem_passageira("Outro jogador já está usando essa conta", cor=Cores["vermelho"])
        elif status == 202:
            parametros.update({"Tela": InicioTelaCriandoPersonagem, "TentarEntrarNoServidor": True})
        elif status == 503:
            parametros.update({"Tela": InicioTelaJogar, "TentarEntrarNoServidor": True, "ServerSelecionado": None})
            adicionar_mensagem_passageira("Servidor não está ativado", cor=Cores["vermelho"])
        elif status == 504:
            parametros.update({"Tela": InicioTelaJogar, "TentarEntrarNoServidor": True, "ServerSelecionado": None})
            adicionar_mensagem_passageira("Servidor está desligado", cor=Cores["vermelho"])
        elif status == 600:
            parametros.update({"Tela": InicioTelaJogar, "TentarEntrarNoServidor": True, "ServerSelecionado": None})
            adicionar_mensagem_passageira("Erro Inesperado", cor=Cores["vermelho"])
        else:
            parametros.update({"Tela": InicioTelaJogar, "TentarEntrarNoServidor": True, "ServerSelecionado": None})
            adicionar_mensagem_passageira("Erro Desconhecido", cor=Cores["vermelho"])

def InicioTelaCriandoPersonagem(tela, estados, eventos, parametros):
    global CriandoPersonagem, Inicial, PokemonDestaque, SelecionadoNome, ConectandoGif

    if not CriandoPersonagem:
        CriandoPersonagem = True
        parametros["Personagem"] = {
            "Code": parametros["Code"],
            "Nome": "Nome",
            "Skin": 1,
            "Inicial": None,
            "Inventario": [None] * 70,
            "Pokemons": [None] * 70,
            "Equipes": [[None] * 6] * 5,
            "Nivel": 0,
            "XP": 0,
            "Ouro": 100,
            "Velocidade": 0,
            "Mochila": 0,
            "Maestria":0,
            "Loc": [500,500]
        }
        SelecionadoNome = False

    largura = 1000
    altura = 750
    centro_x = (tela.get_width() - largura) // 2
    centro_y = (tela.get_height() - altura) // 2

    # Renderizar o código
    texto_code = Fontes[25].render(f"Código: {parametros['Code']}", True, (255, 255, 255))
    texto_rect = texto_code.get_rect(bottomright=(centro_x + 130, centro_y + altura))

    # Fundo preto
    pygame.draw.rect(tela, Cores["preto"], (centro_x, centro_y, largura, altura))

    # Desenhar o texto na tela
    tela.blit(texto_code, texto_rect)

    # TÍTULO no topo central da tela
    titulo = Fontes[60].render("Crie seu Personagem", True, Cores["branco"])
    tela.blit(titulo, ((tela.get_width() - titulo.get_width()) // 2, centro_y + 10))

    # Nome
    parametros["Personagem"]["Nome"], SelecionadoNome = Barra_De_Texto(
        tela,
        (centro_x + 30, centro_y + 120, 650, 50),
        Fontes[40],
        Cores["cinza"],
        Cores["branco"],
        Cores["branco"],
        eventos,
        parametros["Personagem"]["Nome"],
        cor_selecionado=Cores["amarelo"],
        selecionada=SelecionadoNome
    )

    largura_quadrado = 190
    altura_quadrado = 190
    x_quadrado = 1235
    y_quadrado = centro_y + 120

    imagem_quadrado = pygame.transform.scale(Fundos["FundoQuadradoNeutro"], (largura_quadrado, altura_quadrado))
    tela.blit(imagem_quadrado, (x_quadrado, y_quadrado))
    DesenharPlayer(tela, Outros["Skins"][round(parametros["Personagem"]["Skin"])],(x_quadrado + largura_quadrado/2, y_quadrado + altura_quadrado /2))

    # TEXTO: Escolha seu Visual
    visual_texto = Fontes[35].render("Escolha seu Visual", True, Cores["branco"])
    tela.blit(visual_texto, (centro_x + 30, centro_y + 220))

    parametros["Personagem"]["Skin"] = Slider(
        tela, "Skin", centro_x + 30, centro_y + 280, 650,
        parametros["Personagem"]["Skin"], 1, len(Outros["Skins"])-1,
        (180, 180, 180), (255, 255, 255), eventos,
        "", Mostrar=False
    )

    espaco_blocos = 45
    tamanho_botao = 90
    espaco_botao = 10

    x_inicial = centro_x + 60
    y_inicial = centro_y + altura - 2 * (tamanho_botao + espaco_botao) - 40

    # TEXTO: Escolha seu Inicial
    inicial_texto = Fontes[35].render("Escolha seu Inicial", True, Cores["branco"])
    tela.blit(inicial_texto, (x_inicial, y_inicial - 110))

    iniciais_fogo = ["Charmander", "Torchic", "Fennekin", "Litten"]
    iniciais_planta = ["Bulbasaur", "Treecko", "Chespin", "Rowlet"]
    iniciais_agua = ["Squirtle", "Mudkip", "Froakie", "Popplio"]

    todos_iniciais = [
        ("Fogo", iniciais_fogo),
        ("Planta", iniciais_planta),
        ("Agua", iniciais_agua)
    ]

    for bloco_idx, (tipo, lista) in enumerate(todos_iniciais):
        x_bloco = x_inicial + bloco_idx * (2 * tamanho_botao + espaco_botao + espaco_blocos)

        for i, nome in enumerate(lista):
            linha = i // 2
            coluna = i % 2
            x = x_bloco + coluna * (tamanho_botao + espaco_botao)
            y = y_inicial + linha * (tamanho_botao + espaco_botao) - 60

            Botao_Selecao(
                tela=tela,
                texto="",
                espaço=(x, y, tamanho_botao, tamanho_botao),
                Fonte=Fontes[30],
                cor_fundo=Texturas["AzulRoxa"],
                cor_borda_normal=Cores["preto"],
                cor_passagem=Cores["branco"],
                cor_borda_esquerda=Cores["vermelho"],
                funcao_esquerdo=lambda nome=nome: parametros["Personagem"].update({"Inicial": nome}),
                desfazer_esquerdo=lambda: parametros["Personagem"].update({"Inicial": None}),
                funcao_direito=None,
                id_botao="selecao_inicial_" + nome,
                estado_global=estados,
                eventos=eventos,
                som="Clique"
            )

            if nome in Outros["PokemonsIniciais"]:
                imagem = pygame.transform.scale(Outros["PokemonsIniciais"][nome], (tamanho_botao + 12, tamanho_botao + 12))
                tela.blit(imagem, (x - 10, y - 25))

    # Quadrado decorativo ao lado dos blocos
    largura_quadrado = 190
    altura_quadrado = 190
    x_quadrado = x_inicial + 3 * (2 * tamanho_botao + espaco_botao + espaco_blocos) + 10
    y_quadrado = y_inicial - 60

    imagem_quadrado = pygame.transform.scale(Fundos["FundoQuadradoNeutro"], (largura_quadrado, altura_quadrado))
    tela.blit(imagem_quadrado, (x_quadrado, y_quadrado))

    if parametros["Personagem"]["Inicial"] is not None:
        nome_pokemon = parametros["Personagem"]["Inicial"]
        texto_nome = Fontes[30].render(nome_pokemon, True, Cores["branco"])
        texto_rect = texto_nome.get_rect(center=(x_quadrado + largura_quadrado // 2, y_quadrado - 20))
        tela.blit(texto_nome, texto_rect)

    if parametros["Personagem"]["Inicial"] != Inicial:
        Inicial = parametros["Personagem"]["Inicial"]
        if parametros["Personagem"]["Inicial"] != None:
            PokemonDestaque = Animação(Outros["PokemonsIniciais"][f"{Inicial}Gif"],(x_quadrado + 95, y_quadrado + 95), intervalo=30, tamanho=1.2)
    
    if PokemonDestaque is not None:
        if parametros["Personagem"]["Inicial"] != None:
            PokemonDestaque.atualizar(tela)
    
    Botao(
        tela, "Registrar", (x_quadrado - 200, y_quadrado + 210, 350, 60),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": TelaDeCerteza, "TelaDeCerteza": {"Voltar": lambda: parametros.update({"Tela": InicioTelaCriandoPersonagem}),"Funcao": [lambda: RegistrarNoServer(parametros["Personagem"]["Code"], parametros["Personagem"], parametros),lambda: parametros.update({"Tela": InicioTelaConectando, "TentandoEntrarNoServidor": True})]}}),
        Fontes[40], B_Salvar, eventos, som="Clique"
    )
    Botao(
        tela, "Cancelar", (x_quadrado - 650, y_quadrado + 210, 350, 60),
        Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": TelaDeCerteza, "TelaDeCerteza": {"Voltar": lambda: parametros.update({"Tela": InicioTelaCriandoPersonagem}),"Recado": "O personagem não será salvo, Tem certeza?", "Funcao": lambda: parametros.update({"Tela": InicioTelaJogar, "ServerSelecionado": None})}}),
        Fontes[40], B_Voltar, eventos, som="Clique"
    )

def InicioTelaOperador(tela, estados, eventos, parametros):
    global ConectandoGif

    if parametros["Operador"]:
            
            if parametros["ServerOperadoAtivado"]:
                Botao(
                    tela, "Resetar Server", (750, 560, 420, 125), Texturas["vermelho"], Cores["preto"], Cores["branco"],
                    lambda: parametros.update({"Tela": TelaDeCerteza, "TelaDeCerteza": {"Voltar": lambda: parametros.update({"Tela": InicioTelaOperador}), "Funcao": [lambda: ResetarServidor(parametros), lambda: parametros.update({"Tela": InicioTelaOperador})]}}),
                    Fontes[40], B_jogar, eventos, som="Clique", cor_texto=Cores["branco"]
                )
            else:
                Botao(
                    tela, "Ativar Server", (750, 560, 420, 125), Texturas["azul"], Cores["preto"], Cores["branco"],
                    [lambda: AtivarServidor(parametros), lambda: parametros.update({"ServerOperadoAtivado": True})],
                    Fontes[40], B_jogar, eventos, som="Clique", cor_texto=Cores["branco"]
                )
            
            if parametros["ServerOperadoLigado"]:
                Botao(
                    tela, "Desligar Server", (750, 730, 420, 125), Texturas["vermelho"], Cores["preto"], Cores["branco"],
                    [lambda: LigarDesligarServidor(parametros, False),lambda: parametros.update({"ServerOperadoLigado": False})],
                    Fontes[40], B_jogar, eventos, som="Clique", cor_texto=Cores["branco"]
                )
            else:
                Botao(
                    tela, "Ligar Server", (750, 730, 420, 125), Texturas["azul"], Cores["preto"], Cores["branco"],
                    [lambda: LigarDesligarServidor(parametros, True),lambda: parametros.update({"ServerOperadoLigado": True})],
                    Fontes[40], B_jogar, eventos, som="Clique", cor_texto=Cores["branco"]
                )
            
            Botao(
            tela, "Voltar", (800, 900, 320, 80),
            Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
            lambda: parametros.update({"Tela": InicioTelaJogar, "Operador": False, "ServerSelecionado": None, "TentarOperarServidor": True}),
            Fontes[40], B_Voltar, eventos, som="Clique"
            )

    else:
        if ConectandoGif is None:
            ConectandoGif = Animação(Outros["Conectando"], (960, 520))

        # --- TEXTO CENTRAL SUPERIOR ---
        texto = Fontes[60].render("Conectando ao servidor", True, Cores["branco"])
        texto_rect = texto.get_rect(center=(960, 80))  # Centralizado no topo
        tela.blit(texto, texto_rect)

        
        # Inicializa o tempo da última tentativa
        if "TempoUltimaTentativa" not in parametros:
            parametros["TempoUltimaTentativa"] = 0

        tempo_entre_tentativas = 6  # segundos
        tempo_atual = time.time()

        if parametros["TentarOperarServidor"] or (tempo_atual - parametros["TempoUltimaTentativa"]) > tempo_entre_tentativas:
            parametros["TempoUltimaTentativa"] = tempo_atual
            parametros["TentarOperarServidor"] = False
            threading.Thread(target=lambda: requests.get(f"{parametros['ServerSelecionado']['link']}/verifica-servidor-ativo"), daemon=True).start()
            threading.Thread(target=ObterEstadoServidor, args=(parametros,), daemon=True).start()
            threading.Thread(target=VerificaOperador, args=(parametros["OperadorCode"], parametros), daemon=True).start()
        
        Botao(
            tela, "Voltar", (800, 700, 320, 80),
            Texturas["AzulRoxa"], Cores["preto"], Cores["branco"],
            lambda: parametros.update({"Tela": InicioTelaJogar, "Operador": False, "ServerSelecionado": None, "TentarOperarServidor": True}),
            Fontes[40], B_Voltar, eventos, som="Clique"
        )
        ConectandoGif.atualizar(tela)

def InicioLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros 
    if Cores == None:
        Cores, Fontes, Texturas, Fundos, Outros = info["Conteudo"]
    else:
        info["Conteudo"] = Cores, Fontes, Texturas, Fundos, Outros

    parametros = {
        "Tela": InicioTelaPrincipal,
        "Servers": [],
        "ServerSelecionado": None,
        "NomeServer": "Novo Server",
        "LinkServer": "Link do Server",
        "Carregar": False,
        "Config": config,
        "TelaEntradaTexto": {"Texto": ""},
        "TentarEntrarNoServidor": True,
        "TentarOperarServidor": True,
        "ServerOperadoLigado": False,
        "ServerOperadoAtivado": False,
        "Operador": False
    }

    x = 0
    reverse = False  # começa indo pra esquerda
    LIMITE_ESQUERDA = -1520  # vai até -1520 (3440 - 1920)

    tempo_anterior = pygame.time.get_ticks()
    velocidade = 0.04  # pixels por milissegundo

    CarregarServers(parametros)
    Musica("MusicaTema")

    while estados["Inicio"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Inicio"] = False
                estados["Rodando"] = False
                Escurecer(tela,info)
                return

        # Atualiza reversão de direção
        if x <= LIMITE_ESQUERDA:
            reverse = True
        elif x >= 0:
            reverse = False

        # Calcula deslocamento com base no tempo decorrido
        tempo_atual = pygame.time.get_ticks()
        delta = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual

        deslocamento = velocidade * delta
        if reverse:
            x += deslocamento  # volta para a direita
        else:
            x -= deslocamento  # vai para a esquerda

        # Desenha fundo com deslocamento e corte vertical
        tela.blit(Fundos["FundoInicio"], (round(x), -360))

        # Chama tela atual
        parametros["Tela"](tela, estados, eventos, parametros)

        for msg in mensagens_passageiras:
            msg.atualizar()
            msg.desenhar(tela)
        mensagens_passageiras[:] = [msg for msg in mensagens_passageiras if msg.ativa]

        if config["FPS Visivel"]:
            fps_atual = relogio.get_fps()
            texto = f"FPS: {fps_atual:.1f}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x_fps = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x_fps, 10), (255, 255, 255), (0, 0, 0))

        texto = f"VER: {config['Ver']:.1f}"
        texto_com_borda(tela, texto, Fontes[40], (10, tela.get_height() - Fontes[40].get_height()), (255, 255, 255), (0, 0, 0))

        aplicar_claridade(tela, config["Claridade"])
        Clarear(tela,info)
        pygame.display.update() 
        relogio.tick(config["FPS"])

    try:
        info.update({

        "Server": {
            "Code": parametros["Code"],
            "Player": parametros["EstadoServidor"]["dados"]["conta"],
            "Link": parametros["ServerSelecionado"]["link"]
        },

        "Alvo": "Mundo",
        "Carregado": False
    })
        
    except KeyError:
        return
    
    if config["Pré-Carregamento"]:
        carregamento_thread = threading.Thread(target=CarregamentoAvançado, args=(info,True))
    else:
        carregamento_thread = threading.Thread(target=CarregamentoAvançado, args=(info,False))

    carregamento_thread.start()
    Escurecer(tela,info)
