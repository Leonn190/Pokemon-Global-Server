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


def _gerar_pokemon_comum() -> Dict:
    """Gera 1 Pokémon usando o próprio gerador do projeto, priorizando raridade comum."""
    raridade_col = "Raridade"
    nome_col = "Nome"

    candidatos = df_pokemons

    if raridade_col in df_pokemons.columns:
        serie = df_pokemons[raridade_col].astype(str).str.lower().str.strip()
        comuns = df_pokemons[serie.str.contains("comum", na=False)]
        if not comuns.empty:
            candidatos = comuns

    nome = random.choice(candidatos[nome_col].dropna().tolist())

    # Fluxo real de geração: compactado -> desserializado -> materializado -> formato batalha
    compactado = criar_pokemon_especifico(nome)
    while not compactado:
        nome = random.choice(df_pokemons[nome_col].dropna().tolist())
        compactado = criar_pokemon_especifico(nome)

    materializado = MaterializarPokemon(desserializar_pokemon(compactado))
    return GeraPokemonBatalha(materializado)


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

        move = random.choice(viaveis)
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
