import pygame
import threading
import time
import traceback

from Codigo.Modulos.Outros import Clarear, Escurecer
from Codigo.Server.ServerMundo import VerificaçãoSimplesServer, VerificaMapa, SalvarConta, SairConta, RemoverBau, RemoverPokemon, AtualizarPokemon
from Codigo.Modulos.Config import TelaConfigurações
from Codigo.Modulos.Inventario import TelaInventario
from Codigo.Modulos.Paineis import BarraDeItens
from Codigo.Modulos.Comandos import ComandosMundo
from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda
from Codigo.Prefabs.Particulas import atualizar_e_desenhar_bursts
from Codigo.Prefabs.Terminal import terminal
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
Icones = None

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
        raio_geral = 3
        x_min, x_max = px - raio_geral, px + raio_geral
        y_min, y_max = py - raio_geral, py + raio_geral

        # Raio especial para pokémons (dobro do geral)
        raio_pokemon = raio_geral * 3
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
    Parametros.setdefault("IDsPokemonsRemovidos", [])

    while Parametros["Running"]:
        try:
            # ====== POKÉMONS ======
            pokemons_novos = {}
            pokemons_antigos = dict(Mapa.PokemonsAtivos)

            for pkm_info in Parametros["PokemonsProximos"]:
                id_ = pkm_info["id"]

                if id_ not in Parametros["IDsPokemonsRemovidos"]:

                    if id_ not in Mapa.PokemonsAtivos and "Fugiu" not in pkm_info["extra"]:
                        novo_pokemon = Pokemon(
                            Loc=pkm_info["loc"],
                            string_dados=pkm_info["info"],
                            extra=pkm_info["extra"],
                            Imagens=Pokemons,
                            Animaçoes=Animaçoes,
                            Parametros=Parametros
                        )
                        pokemons_novos[id_] = novo_pokemon
                    else:
                        if id_ in Mapa.PokemonsAtivos:
                            pkm_existente = Mapa.PokemonsAtivos[id_]
                            pkm_existente.LocAlvo = pkm_info["loc"]
                            pkm_existente.TamanhoMirando = pkm_info["extra"]["TamanhoMirando"]
                            pkm_existente.VelocidadeMirando = pkm_info["extra"]["VelocidadeMirando"]
                            pkm_existente.Dificuldade = pkm_info["extra"]["Dificuldade"]
                            pkm_existente.Frutas = pkm_info["extra"]["Frutas"]

                            if "Tentativas" in pkm_info["extra"]:
                                pkm_existente.Tentativas = pkm_info["extra"]["Tentativas"]
                            if "MaxFrutas" in pkm_info["extra"]:
                                pkm_existente.MaxFrutas = pkm_info["extra"]["MaxFrutas"]
                            if "DocesExtras" in pkm_info["extra"]:
                                pkm_existente.DocesExtras = pkm_info["extra"]["DocesExtras"]
                            if "Irritado" in pkm_info["extra"]:
                                pkm_existente.Irritado = pkm_info["extra"]["Irritado"]
                            if "Batalhando" in pkm_info["extra"]:
                                pkm_existente.Batalhando = pkm_info["extra"]["Batalhando"]
                            if "Capturado" in pkm_info["extra"]:
                                pkm_existente.Capturado = pkm_info["extra"]["Capturado"]
                            if "Fugiu" in pkm_info["extra"]:
                                pkm_existente.Fugiu = pkm_info["extra"]["Fugiu"]

                            pokemons_novos[id_] = pkm_existente

                # Se tiver Fugiu == 1 ou Capturado == 1, marcar como removido
                if pkm_info.get("Fugiu", False) != False or pkm_info.get("Capturado", False) != False:
                    if id_ not in Parametros["IDsPokemonsRemovidos"]:
                        Parametros["IDsPokemonsRemovidos"].append(id_)

                if id_ in pokemons_antigos:
                    del pokemons_antigos[id_]

            # Marcar como Apagar pokémons que não estão mais próximos
            for pkm_removido in pokemons_antigos.values():
                pkm_removido.Apagar = True
                pokemons_novos[pkm_removido.Dados["ID"]] = pkm_removido

            # IDs removidos
            for id_, pkm in list(pokemons_novos.items()):
                if getattr(pkm, "Apagar", False):
                    if id_ not in Parametros["IDsPokemonsRemovidos"]:
                        Parametros["IDsPokemonsRemovidos"].append(id_)

            # Remove efetivamente
            Mapa.PokemonsAtivos = {
                k: v for k, v in pokemons_novos.items()
                if not getattr(v, "Apagar", False)
            }

            # ====== BAÚS ======
            baus_novos = {}
            baus_antigos = dict(Mapa.BausAtivos)

            for bau_info in Parametros.get("BausProximos", []):
                id_ = bau_info["ID"]
                loc = (bau_info["X"], bau_info["Y"])
                raridade = bau_info["Raridade"]

                if id_ not in Mapa.BausAtivos:
                    novo_bau = Bau(raridade=raridade, ID=id_, Loc=loc)
                    baus_novos[id_] = novo_bau
                else:
                    bau_existente = Mapa.BausAtivos[id_]
                    bau_existente.Loc = loc
                    baus_novos[id_] = bau_existente

                if id_ in baus_antigos:
                    del baus_antigos[id_]

            for bau_removido in baus_antigos.values():
                bau_removido.Aberto = True
                baus_novos[bau_removido.ID] = bau_removido

            Mapa.BausAtivos = {k: v for k, v in baus_novos.items() if not getattr(v, "Apagar", False)}

            time.sleep(0.5)

        except Exception as e:
            print(f"[ERRO] {e}")
            traceback.print_exc()
            continue

def LoopRemoveBaus(parametros):
    while parametros["Running"]:
        for bauID in parametros["BausRemover"]:
            RemoverBau(parametros, bauID)
        for PokemonID in parametros["PokemonsRemover"]:
            RemoverPokemon(parametros, PokemonID)
        for PokemonInfo in parametros["PokemonsAtualizar"]:
            AtualizarPokemon(parametros, PokemonInfo)

        parametros["BausRemover"] = []
        parametros["PokemonsRemover"] = []
        parametros["PokemonsAtualizar"] = []
        time.sleep(1)

def MundoTelaOpçoes(tela, estados, eventos, parametros):

    if parametros["TelaConfigurações"]["Entrou"]:
        if pygame.mouse.get_pressed()[0]:
            return
        else:
            parametros["TelaConfigurações"]["Entrou"] = False

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
    
    camera.desenhar(tela,player.Loc,mapa,player,Estruturas,parametros["delta_time"],Outros["Baus"])

    if parametros["ModoTeclado"] == False:
        Botao_Tecla("esc",lambda: parametros.update({"Tela": MundoTelaOpçoes}))
        Botao_Tecla("E",lambda: parametros.update({"InventarioAtivo": True}))

    if parametros["InventarioAtivo"]:
        TelaInventario(tela, player, eventos, parametros)
    else:
        player.Atualizar(tela, parametros["delta_time"], mapa, Fontes[20], parametros, Consumiveis)
        BarraDeItens(tela, player, eventos)
        terminal(tela,Fontes[16],player.Nome,pygame.K_TAB,eventos,parametros,ComandosMundo,parametros)

def MundoLoop(tela, relogio, estados, config, info):
    global Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Estruturas, Equipaveis, Consumiveis, Animaçoes, Icones, player, mapa, camera
    if Cores == None:
        Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Consumiveis, Equipaveis, Estruturas, Animaçoes, Icones = info["Conteudo"]

    parametros = {
        "Link": info["Server"]["Link"],
        "Code": info["Server"]["Code"],
        "Ping": 0,
        "Verificado": True,
        "Running": True,   # flag para controle da thread
        "Tela": MundoTelaPadrao,
        "Config": config,
        "TelaConfigurações": {"Entrou": False},
        "PokemonsProximos": [],
        "PokemonsRemover": [],
        "PokemonsAtualizar": [],
        "PlayersProximos": [],
        "BausProximos": [],
        "BausRemover": [],
        "MensagemOnline": None,
        "ModoTeclado": False,
        "InventarioAtivo": False,
        "Inventario": {
            "Setor": None,
            "ItemSelecionado": None,
            "PokemonSelecionado": None
        }
    }

    VerificaMapa(parametros)
    Musica("MundoTema")

    player = Player(info["Server"]["Player"]["dados"],Outros["SkinsTodas"])
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
        parametros["delta_time"] = relogio.tick(config["FPS"]) / 1000  # Em segundos
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

        atualizar_e_desenhar_mensagens_itens(tela, parametros["delta_time"])

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
            texto = f" X:{round(x_cord - 450)} Y:{round(y_cord - 450)}"
            texto_surface = Fontes[25].render(texto, True, (255, 255, 255))
            x = tela.get_width() - texto_surface.get_width() - 10
            texto_com_borda(tela, texto, Fontes[25], (x, y_base), (255, 255, 255), (0, 0, 0))
        
        atualizar_e_desenhar_bursts(tela,[x_cord,y_cord], parametros["delta_time"])

        Clarear(tela, info)
        pygame.display.update()

    parametros["Running"] = False  # garante que a thread pare ao sair do loop
    Escurecer(tela, info)
    