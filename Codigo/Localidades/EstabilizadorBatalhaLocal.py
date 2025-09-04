
from Codigo.Localidades.ControleBatalha import ExecutePartida, ExecuteRodada

def criar_e_inicializar_sala_local(pokemons_jogador1,pokemons_ia,code_p1="LOCAL_P1",code_ia="IA_LOCAL"):

    sala = {
        "jogador1": code_p1,
        "pokemons_jogador1": pokemons_jogador1,

        "jogador2": code_ia,                 # sempre IA local
        "pokemons_jogador2": pokemons_ia,

        "modo_local": True
    }

    ExecutePartida(sala)  # monta Partida e campos padrão

    sala["Log"] = []
    sala["jogada_jogador1"] = None
    sala["jogada_jogador2"] = None
    return sala

def receber_e_executar_jogadas(sala, jogada_p1, jogada_p2=None):

    # Jogada P1
    sala["jogada_jogador1"] = jogada_p1
    sala["jogada_jogador2"] = jogada_p2

    # Executa a rodada
    ExecuteRodada(sala)

    # Resultados
    log = sala.get("Log")
    partida_dic = sala["partida"].ToDic()
    sala["log"] = log
    sala["partidaDic"] = partida_dic

    # Reseta para o próximo turno
    sala["jogada_jogador1"] = None
    sala["jogada_jogador2"] = None

    return log, partida_dic

