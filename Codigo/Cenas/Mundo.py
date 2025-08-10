import pygame
import threading
import time

from Codigo.Modulos.Outros import Clarear, Escurecer
from Server.ServerMundo import VerificaçãoSimplesServer, VerificaMapa, SalvarConta, SairConta, RemoverBau, RemoverPokemon
from Codigo.Modulos.Config import TelaConfigurações
from Codigo.Modulos.Inventario import TelaInventario
from Codigo.Modulos.Paineis import BarraDeItens
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda
from Codigo.Prefabs.BotoesPrefab import Botao, Botao_Tecla
from Codigo.Prefabs.Sonoridade import Musica
from Codigo.Prefabs.Mensagens import atualizar_e_desenhar_mensagens_itens
from Codigo.Geradores.GeradorPlayer import Player
from Codigo.Geradores.GeradorMapa import Mapa, Camera
from Codigo.Geradores.GeradorEstruturas import GridToDic, Bau
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

def AtualizarColisaoProxima(mapa, player, parametros):
    while parametros["Running"]:
        px, py = player.Loc  # posição do player em coordenadas de tile

        # Raio geral (para objetos e baús)
        raio_geral = 5
        x_min, x_max = px - raio_geral, px + raio_geral
        y_min, y_max = py - raio_geral, py + raio_geral

        # Raio especial para pokémons (dobro do geral)
        raio_pokemon = raio_geral * 2
        pkm_x_min, pkm_x_max = px - raio_pokemon, px + raio_pokemon
        pkm_y_min, pkm_y_max = py - raio_pokemon, py + raio_pokemon

        # Limpar colisões anteriores
        mapa.ObjetosColisão = {}
        mapa.PokemonsColisão = {}
        mapa.BausColisão = {}

        # Atualizar Objetos
        for (x, y), obj in mapa.DicObjetos.items():
            if x_min <= x <= x_max and y_min <= y <= y_max:
                mapa.ObjetosColisão[(x, y)] = obj

        # Atualizar Pokémons
        for pokemon in mapa.PokemonsAtivos.values():
            x, y = pokemon.Loc
            if pkm_x_min <= x <= pkm_x_max and pkm_y_min <= y <= pkm_y_max:
                mapa.PokemonsColisão[(x, y)] = pokemon

        # Atualizar Baús
        for bau in mapa.BausAtivos.values():
            x, y = bau.Loc
            if x_min <= x <= x_max and y_min <= y <= y_max:
                mapa.BausColisão[(x, y)] = bau

        time.sleep(0.25)

def thread_verificacao_continua(parametros):
    while parametros["Running"]:
        if parametros["Verificado"]:
            inicio = time.time()
            VerificaçãoSimplesServer(parametros)
            fim = time.time()
            parametros["Ping"] = round((fim - inicio) * 1000, 2)  # Ping em milissegundos
        else:
            time.sleep(3)

def GerenciadorDePokemonsProximos(Parametros, Mapa):

    while Parametros["Running"]:
        # ====== POKÉMONS ======
        pokemons_novos = {}
        for pkm_info in Parametros["PokemonsProximos"]:
            id_ = pkm_info["id"]
            if id_ not in Mapa.PokemonsAtivos:
                # Criar novo Pokémon
                novo_pokemon = Pokemon(
                    Loc=pkm_info["loc"],
                    string_dados=pkm_info["info"],
                    Imagens=Pokemons,
                    Animaçoes=Animaçoes,
                    Parametros=Parametros
                )
                pokemons_novos[id_] = novo_pokemon
            else:
                # Atualiza o Pokémon existente
                pokemons_novos[id_] = Mapa.PokemonsAtivos[id_]
                pokemons_novos[id_].Loc = pkm_info["loc"]

        Mapa.PokemonsAtivos = pokemons_novos

        # ====== BAÚS ======
        baus_novos = {}

        # Marca todos os baús atuais como potencialmente "desaparecidos"
        baus_antigos = dict(Mapa.BausAtivos)

        # Percorre os baús próximos
        for bau_info in Parametros.get("BausProximos", []):
            id_ = bau_info["ID"]
            loc = (bau_info["X"], bau_info["Y"])
            raridade = bau_info["Raridade"]

            if id_ not in Mapa.BausAtivos:
                novo_bau = Bau(raridade=raridade, ID=id_, Loc=loc)
                baus_novos[id_] = novo_bau
            else:
                bau_existente = Mapa.BausAtivos[id_]
                bau_existente.Loc = loc  # atualiza a posição
                baus_novos[id_] = bau_existente

            # Como esse baú ainda existe, removemos da lista de antigos
            if id_ in baus_antigos:
                del baus_antigos[id_]

        # Todos os baús que *não* estão mais em BausProximos devem ser marcados como abertos
        for bau_removido in baus_antigos.values():
            bau_removido.Aberto = True
            baus_novos[bau_removido.ID] = bau_removido  # Mantém o baú nos ativos

        Mapa.BausAtivos = baus_novos

        time.sleep(0.75)

def LoopRemoveBaus(parametros):
    while parametros["Running"]:
        for bauID in parametros["BausRemover"]:
            RemoverBau(parametros, bauID)
        for PokemonID in parametros["PokemonsRemover"]:
            RemoverPokemon(parametros, PokemonID)
        parametros["BausRemover"] = []
        parametros["PokemonsRemover"] = []
        time.sleep(1.25)

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
    
    camera.desenhar(tela,player.Loc,mapa,player,Estruturas,Outros["Baus"])

    if parametros["InventarioAtivo"]:
        TelaInventario(tela, player, eventos, parametros)
    else:
        player.Atualizar(tela, parametros["delta_time"], mapa, Fontes[20], parametros, Consumiveis)
        BarraDeItens(tela, player, eventos)

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
        "PokemonsRemover": [],
        "PlayersProximos": [],
        "BausProximos": [],
        "BausRemover": [],
        "InventarioAtivo": False,
        "Inventario": {
            "Setor": None,
            "ItemSelecionado": None,
            "PokemonSelecionado": None
        }
    }

    VerificaMapa(parametros)
    Musica("MundoTema")

    player = Player(info["Server"]["Player"]["dados"],Outros["Skins"])
    mapa = Mapa(parametros["GridBiomas"],GridToDic(parametros["GridObjetos"]))
    camera = Camera(18)

    parametros.update({"Player": player})

    # Cria e inicia thread da verificação
    threading.Thread(target=thread_verificacao_continua, args=(parametros,), daemon=True).start()
    threading.Thread(target=AtualizarColisaoProxima, args=(mapa,player,parametros), daemon=True).start()
    threading.Thread(target=GerenciadorDePokemonsProximos, args=(parametros, mapa), daemon=True).start()
    threading.Thread(target=LoopRemoveBaus, args=(parametros,), daemon=True).start()

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

        atualizar_e_desenhar_mensagens_itens(tela)

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
    Escurecer(tela, info)
    