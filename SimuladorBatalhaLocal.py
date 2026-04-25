"""
Simulador local de batalha (sem servidor).

Objetivo:
- Reusar a lógica real do projeto (gerador de Pokémon + motor de batalha).
- Montar uma batalha mínima funcional entre duas equipes geradas automaticamente.
- Executar rodadas com escolhas simples de ataque para validar o fluxo offline.

Uso:
    python SimuladorBatalhaLocal.py
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional

import pandas as pd

from Codigo.Geradores.GeradorPokemon import (
    GeraPokemonBatalha,
    MaterializarPokemon,
    criar_pokemon_especifico,
    desserializar_pokemon,
    df as df_pokemons,
)
from Codigo.Localidades.EstabilizadorBatalhaLocal import (
    criar_e_inicializar_sala_local,
    receber_e_executar_jogadas,
)
from Codigo.Funções.FunçõesAtaques import AtkDic


_DF_ATAQUES = pd.read_csv("Dados/Ataques.csv")


def _gerar_pokemon_comum() -> Dict:
    """Gera 1 Pokémon usando o próprio gerador do projeto, priorizando raridade comum."""
    raridade_col = "Raridade"
    nome_col = "Nome"
    estagio_col = "Estagio"

    candidatos = df_pokemons

    if raridade_col in df_pokemons.columns:
        serie = df_pokemons[raridade_col].astype(str).str.lower().str.strip()
        comuns = df_pokemons[serie.str.contains("comum", na=False)]
        if not comuns.empty:
            candidatos = comuns

    # Evita nomes que quebram no criar_pokemon_especifico (Estagio inválido/NaN)
    if estagio_col in candidatos.columns:
        estagio_numerico = candidatos[estagio_col].astype(str).str.replace(",", ".", regex=False)
        estagio_numerico = estagio_numerico.str.strip()
        estagio_numerico = estagio_numerico[~estagio_numerico.str.contains(r"[^0-9\.\-]", na=True)]
        idx_validos = estagio_numerico.index
        candidatos = candidatos.loc[idx_validos]

    # Também elimina entradas explicitamente bloqueadas pela geração do projeto
    if raridade_col in candidatos.columns:
        candidatos = candidatos[candidatos[raridade_col].astype(str).str.strip() != "-"]

    pool_nomes = candidatos[nome_col].dropna().tolist()
    if not pool_nomes:
        pool_nomes = df_pokemons[nome_col].dropna().tolist()
    if not pool_nomes:
        raise RuntimeError("Não foi possível montar pool de nomes para geração de Pokémon.")

    # Fluxo real de geração: compactado -> desserializado -> materializado -> formato batalha
    compacto_valido = None
    tentativas = 0
    max_tentativas = 250
    while not compacto_valido and tentativas < max_tentativas:
        tentativas += 1
        nome = random.choice(pool_nomes)
        try:
            compactado = criar_pokemon_especifico(nome)
            if not compactado:
                continue
            materializado = MaterializarPokemon(desserializar_pokemon(compactado))
            compacto_valido = GeraPokemonBatalha(materializado)
        except (ValueError, TypeError):
            compacto_valido = None

    if not compacto_valido:
        raise RuntimeError("Falha ao gerar Pokémon válido após múltiplas tentativas.")

    return compacto_valido


def _gerar_equipe(tamanho: int = 6) -> List[Dict]:
    return [_gerar_pokemon_comum() for _ in range(tamanho)]


def _definir_ativos(equipe: List[Dict], quantidade: int = 3) -> None:
    for poke in equipe:
        poke["Ativo"] = False
        poke["Pos"] = None

    ativos = random.sample(equipe, k=min(quantidade, len(equipe)))
    posicoes = random.sample(list(range(1, 10)), k=len(ativos))

    for poke, pos in zip(ativos, posicoes):
        poke["Ativo"] = True
        poke["Pos"] = pos


def _nome_move(move: Dict) -> Optional[str]:
    return move.get("nome") or move.get("Nome") or move.get("Ataque") or move.get("ataque")


def _custo_move(move: Dict) -> float:
    bruto = move.get("custo", move.get("Custo", 0))
    try:
        return float(bruto)
    except (TypeError, ValueError):
        return 0.0


def _ataque_suportado(nome_ataque: str) -> bool:
    """Garante que funções irregulares do ataque existem em AtkDic (evita KeyError no motor)."""
    linha = _DF_ATAQUES[_DF_ATAQUES["Ataque"] == nome_ataque]
    if linha.empty:
        return False

    ataque = linha.iloc[0]
    codigo = int(ataque["Code"])
    funcoes = str(ataque.get("função", "")).lower()
    if funcoes in {"nan", "none"}:
        funcoes = ""

    for sufixo in ("i", "m", "s", "p", "f"):
        if sufixo in funcoes and f"{codigo}{sufixo}" not in AtkDic:
            return False

    return True


def _escolher_alvo_inimigo(equipe_inimiga: List[Dict]) -> Optional[str]:
    vivos_ativos = [p for p in equipe_inimiga if p.get("Ativo") and p.get("Vida", 0) > 0]
    if not vivos_ativos:
        vivos_ativos = [p for p in equipe_inimiga if p.get("Vida", 0) > 0 and p.get("Pos")]
    if not vivos_ativos:
        return None

    alvo = random.choice(vivos_ativos)
    return f"I{int(alvo['Pos'])}"


def _montar_jogadas(equipe: List[Dict], equipe_inimiga: List[Dict]) -> List[Dict]:
    jogadas: List[Dict] = []

    for idx, poke in enumerate(equipe):
        if not poke.get("Ativo"):
            continue
        if poke.get("Vida", 0) <= 0:
            continue

        movelist = [m for m in (poke.get("MoveList") or []) if isinstance(m, dict)]
        if not movelist:
            continue

        energia = float(poke.get("Energia", 0) or 0)
        viaveis = [m for m in movelist if _custo_move(m) <= energia]
        if not viaveis:
            continue

        ataques_suportados = [m for m in viaveis if _nome_move(m) and _ataque_suportado(_nome_move(m))]
        if not ataques_suportados:
            # fallback seguro para nunca quebrar em AtkDic: movimenta para outra casa
            pos_atual = int(poke.get("Pos", 5) or 5)
            opcoes = [p for p in range(1, 10) if p != pos_atual]
            jogadas.append({
                "agente": idx,
                "ataque": "Mover",
                "alvo": random.choice(opcoes) if opcoes else pos_atual,
            })
            continue

        move = random.choice(ataques_suportados)
        nome_ataque = _nome_move(move)
        if not nome_ataque:
            continue

        alvo = _escolher_alvo_inimigo(equipe_inimiga)
        if not alvo:
            continue

        jogadas.append({
            "agente": idx,
            "ataque": nome_ataque,
            "alvo": [alvo],
        })

    return jogadas


def _time_derrotado(equipe: List[Dict]) -> bool:
    return not any((p.get("Vida", 0) > 0) for p in equipe)


def simular_batalha_local(max_turnos: int = 20) -> Dict:
    equipe_1 = _gerar_equipe(6)
    equipe_2 = _gerar_equipe(6)

    _definir_ativos(equipe_1)
    _definir_ativos(equipe_2)

    sala = criar_e_inicializar_sala_local(equipe_1, equipe_2, "SIM_P1", "SIM_IA")

    resultado = {
        "turnos": 0,
        "vencedor": None,
        "logs": [],
    }

    for turno in range(1, max_turnos + 1):
        jogadas_p1 = _montar_jogadas(sala["pokemons_jogador1"], sala["pokemons_jogador2"])
        jogadas_p2 = _montar_jogadas(sala["pokemons_jogador2"], sala["pokemons_jogador1"])

        log_turno, _ = receber_e_executar_jogadas(sala, jogadas_p1, jogadas_p2)

        resultado["turnos"] = turno
        resultado["logs"].append(log_turno)

        if _time_derrotado(sala["pokemons_jogador1"]):
            resultado["vencedor"] = "Jogador 2"
            break
        if _time_derrotado(sala["pokemons_jogador2"]):
            resultado["vencedor"] = "Jogador 1"
            break

    if resultado["vencedor"] is None:
        vida_p1 = sum(max(0, p.get("Vida", 0)) for p in sala["pokemons_jogador1"])
        vida_p2 = sum(max(0, p.get("Vida", 0)) for p in sala["pokemons_jogador2"])
        if vida_p1 > vida_p2:
            resultado["vencedor"] = "Jogador 1 (por vida restante)"
        elif vida_p2 > vida_p1:
            resultado["vencedor"] = "Jogador 2 (por vida restante)"
        else:
            resultado["vencedor"] = "Empate"

    return resultado


def _main() -> None:
    resultado = simular_batalha_local(max_turnos=20)
    print("=== SIMULAÇÃO FINALIZADA ===")
    print(f"Turnos executados: {resultado['turnos']}")
    print(f"Vencedor: {resultado['vencedor']}")
    print(f"Rodadas logadas: {len(resultado['logs'])}")


if __name__ == "__main__":
    _main()
