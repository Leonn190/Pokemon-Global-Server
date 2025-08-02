import pygame
import threading
import time

from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Modulos.ServerMundo import VerificaçãoSimplesServer, VerificaMapa, SalvarConta, SairConta
from Codigo.Modulos.Config import TelaConfigurações
from Codigo.Modulos.Inventario import TelaInventario
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda
from Codigo.Prefabs.BotoesPrefab import Botao, Botao_Tecla
from Codigo.Prefabs.Sonoridade import Musica
from Codigo.Geradores.GeradorPlayer import Player
from Codigo.Geradores.GeradorMapa import Mapa, Camera
from Codigo.Geradores.GeradorEstruturas import GridToDic
from Codigo.Geradores.GeradorPokemon import Pokemon

Cores = None
Fontes = None
Texturas = None
Fundos = None
Outros = None
Pokemons = None
Estruturas = None
Equipaveis = None
Consumiveis = None
Animaçoes = None

player = None
mapa = None
camera = None

B_voltar = {}
B_config = {}
B_sair = {}

def atualizar_chunks(parametros, player, mapa):
    while parametros["Running"]:
        x, y = player.Loc  # posição absoluta em tiles
        chunk_x = int(x) // 100
        chunk_y = int(y) // 100

        chunks_ao_redor = [
            (chunk_x + dx, chunk_y + dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
        ]

        # Filtrar os que realmente existem
        mapa.ChunksCarregados = {
            chave: mapa.ChunksObjetos[chave]
            for chave in chunks_ao_redor
            if chave in mapa.ChunksObjetos
        }

        time.sleep(0.5)

def thread_verificacao_continua(parametros):
    while parametros["Running"]:
        if parametros["Verificado"]:
            inicio = time.time()
            VerificaçãoSimplesServer(parametros)
            fim = time.time()
            parametros["Ping"] = round((fim - inicio) * 1000, 2)  # Ping em milissegundos
        else:
            time.sleep(3)

def GerenciadorDePokemonsProximos(Parametros):
    # Inicializa o dicionário se não existir ainda
    if "PokemonsAtivos" not in Parametros:
        Parametros["PokemonsAtivos"] = {}

    while Parametros["Running"]:
        pokemons_novos = {}

        for pkm_info in Parametros["PokemonsProximos"]:
            id_ = pkm_info["id"]
            if id_ not in Parametros["PokemonsAtivos"]:
                # Criar novo Pokémon
                novo_pokemon = Pokemon(
                    Loc=pkm_info["loc"],
                    string_dados=pkm_info["info"],
                    Imagens=Pokemons,
                    Animaçoes=Animaçoes
                )
                pokemons_novos[id_] = novo_pokemon
            else:
                # Mantém e atualiza o Pokémon já existente
                pokemons_novos[id_] = Parametros["PokemonsAtivos"][id_]
                pokemons_novos[id_].Loc = pkm_info["loc"]

        # Atualiza o dicionário de ativos
        Parametros["PokemonsAtivos"] = pokemons_novos

        time.sleep(0.5)

def MundoTelaOpçoes(tela, estados, eventos, parametros):
    
    Botao(
        tela, "Voltar", (710, 300, 500, 150), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": MundoTelaPadrao}),
        Fontes[40], B_voltar, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    Botao(
        tela, "Configurações", (710, 500, 500, 150), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: parametros.update({"Tela": TelaConfigurações, "TelaConfigurações": {"Voltar":lambda: parametros.update({"Tela": MundoTelaOpçoes}), "Entrou": True}}),
        Fontes[40], B_config, eventos, som="Clique", cor_texto=Cores["branco"]
    )

    Botao(
        tela, "Salvar e Sair", (710, 700, 500, 150), Texturas["Cosmico"], Cores["preto"], Cores["branco"],
        lambda: [SalvarConta(parametros), SairConta(parametros), estados.update({"Mundo": False, "Inicio": True})],
        Fontes[40], B_sair, eventos, som="Clique", cor_texto=Cores["branco"]
    )

def MundoTelaPadrao(tela, estados, eventos, parametros):
    
    camera.desenhar(tela,player.Loc,mapa,Estruturas,parametros["PokemonsAtivos"])

    if parametros["InventarioAtivo"]:
        TelaInventario(tela, player, eventos, parametros)
    else:
        player.Atualizar(tela, parametros["delta_time"], mapa, Fontes[20])

    Botao_Tecla("esc",lambda: parametros.update({"Tela": MundoTelaOpçoes}))
    Botao_Tecla("E",lambda: parametros.update({"InventarioAtivo": True}))

def MundoLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes, player, mapa, camera
    if Cores == None:
        Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Consumiveis, Equipaveis, Estruturas, Animaçoes = info["Conteudo"]

    parametros = {
        "Link": info["Server"]["Link"],
        "Code": info["Server"]["Code"],
        "Ping": 0,
        "Verificado": True,
        "Running": True,   # flag para controle da thread
        "Tela": MundoTelaPadrao,
        "Config": config,
        "PokemonsProximos": [],
        "PlayersProximos": [],
        "PokemonsAtivos": {},
        "InventarioAtivo": False,
        "Inventario": {
            "Setor": None
        }
    }

    VerificaMapa(parametros)
    Musica("MundoTema")

    player = Player(info["Server"]["Player"]["dados"],Outros["Skins"])
    mapa = Mapa(parametros["GridBiomas"],GridToDic(parametros["GridObjetos"]))
    camera = Camera(16)

    parametros.update({"Player": player})

    # Cria e inicia thread da verificação
    verif_thread = threading.Thread(target=thread_verificacao_continua, args=(parametros,), daemon=True)
    verif_thread.start()
    threading.Thread(target=atualizar_chunks, args=(parametros,player,mapa), daemon=True).start()
    threading.Thread(target=GerenciadorDePokemonsProximos, args=(parametros,), daemon=True).start()

    # tela = pygame.display.set_mode(camera.Resolucao, pygame.FULLSCREEN)

    while estados["Mundo"]:
        parametros["delta_time"] = relogio.tick(200) / 1000  # Em segundos
        tela.blit(Fundos["FundoMundo"],(0,0))

        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                estados["Mundo"] = False
                estados["Rodando"] = False
                parametros["Running"] = False  # sinaliza para thread parar
        
        parametros["Tela"](tela, estados, eventos, parametros)

        y_base = 10  # Posição inicial do topo
        espaco = 5   # Espaço entre as linhas

        if config["FPS Visivel"]:
            fps_atual = relogio.get_fps()
            texto = f"FPS: {fps_atual:.1f}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x, y_base), (255, 255, 255), (0, 0, 0))
            y_base += texto_surface.get_height() + espaco

        if config["Ping Visivel"]:
            texto = f"Ping: {parametros['Ping']:.1f}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x, y_base), (255, 255, 255), (0, 0, 0))
            y_base += texto_surface.get_height() + espaco

        if config["Cords Visiveis"]:
            x_cord = round(player.Loc[0], 1)
            y_cord = round(player.Loc[1], 1)
            texto = f" X:{x_cord} Y:{y_cord}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x, y_base), (255, 255, 255), (0, 0, 0))

        Clarear(tela, info)
        pygame.display.update()
        relogio.tick(config["FPS"])

    parametros["Running"] = False  # garante que a thread pare ao sair do loop
    verif_thread.join(timeout=1)
    
    Escurecer(tela, info)
    