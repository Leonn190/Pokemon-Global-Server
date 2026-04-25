"""Simulador de batalha local "idêntico" ao jogo (abre a tela real de batalha).

Este arquivo NÃO cria uma UI paralela.
Ele monta um contexto fake mínimo (player + alvo de confronto) e chama a
mesma cena `Codigo.Cenas.Batalha.BatalhaLoop` usada no jogo.
"""

from __future__ import annotations

import ctypes
import random
from dataclasses import dataclass
from typing import Dict, List

import pygame

from Codigo.Carregar.CarregamentoAvançado import CarregamentoAvançado
from Codigo.Carregar.CarregamentoBasico import CarregamentoBasico
from Codigo.Cenas.Batalha import BatalhaLoop
from Codigo.Cenas import Mundo
from Codigo.Geradores.GeradorPokemon import (
    MaterializarPokemon,
    criar_pokemon_especifico,
    desserializar_pokemon,
    df as df_pokemons,
)
from Codigo.Prefabs.FunçõesPrefabs import Carregar_Imagem
from Codigo.Prefabs.Sonoridade import VerificaSonoridade


@dataclass
class AlvoConfrontoFake:
    Dados: Dict


@dataclass
class PlayerFake:
    Nome: str
    Skin: pygame.Surface
    Equipes: List[List[Dict]]
    Pokemons: List[Dict]


def _gerar_pokemon_materializado_comum() -> Dict:
    candidatos = df_pokemons

    if "Raridade" in candidatos.columns:
        comuns = candidatos[candidatos["Raridade"].astype(str).str.lower().str.contains("comum", na=False)]
        if not comuns.empty:
            candidatos = comuns

    if "Estagio" in candidatos.columns:
        est = candidatos["Estagio"].astype(str).str.replace(",", ".", regex=False).str.strip()
        est = est[~est.str.contains(r"[^0-9\.\-]", na=True)]
        candidatos = candidatos.loc[est.index]

    if "Raridade" in candidatos.columns:
        candidatos = candidatos[candidatos["Raridade"].astype(str).str.strip() != "-"]

    nomes = candidatos["Nome"].dropna().tolist() or df_pokemons["Nome"].dropna().tolist()
    if not nomes:
        raise RuntimeError("Não há nomes válidos para geração de Pokémon.")

    for _ in range(300):
        nome = random.choice(nomes)
        try:
            compacto = criar_pokemon_especifico(nome)
            if not compacto:
                continue
            return MaterializarPokemon(desserializar_pokemon(compacto))
        except Exception:
            continue

    raise RuntimeError("Falha ao gerar Pokémon materializado para o simulador.")


def _gerar_time_materializado_6() -> List[Dict]:
    return [_gerar_pokemon_materializado_comum() for _ in range(6)]


def _criar_player_fake(outros: Dict) -> PlayerFake:
    equipe = _gerar_time_materializado_6()
    pokemons = list(equipe)

    skin = outros["Skins"][1] if outros.get("Skins") else pygame.Surface((64, 64), pygame.SRCALPHA)
    if skin.get_width() == 0 or skin.get_height() == 0:
        skin = pygame.Surface((64, 64), pygame.SRCALPHA)
        skin.fill((120, 180, 255))

    return PlayerFake(
        Nome="Simulador",
        Skin=skin,
        Equipes=[equipe],
        Pokemons=pokemons,
    )


def _criar_alvo_fake() -> AlvoConfrontoFake:
    return AlvoConfrontoFake(Dados=_gerar_pokemon_materializado_comum())


def _montar_info_config_estados() -> tuple[Dict, Dict, Dict]:
    info = {
        "Carregado": False,
        "Alvo": "Batalha",
        "Escuro": 100,
        "AcabouDeSairConfronto": False,
    }

    # Carrega os mesmos assets da pipeline do jogo.
    CarregamentoBasico(info)
    CarregamentoAvançado(info, Pré=True)

    _, _, _, _, outros, *_ = info["Conteudo"]

    # Injeta player fake no módulo Mundo, que é de onde a cena de batalha lê.
    Mundo.player = _criar_player_fake(outros)

    info["ParametrosConfronto"] = {
        "BatalhaSimples": True,
        "AlvoConfronto": _criar_alvo_fake(),
    }

    estados = {
        "Rodando": True,
        "Inicio": False,
        "Carregamento": False,
        "Mundo": False,
        "PreBatalha": False,
        "Batalha": True,
    }

    config = {
        "FPS": 180,
        "Volume": 0.5,
        "Claridade": 75,
        "Mudo": False,
        "FPS Visivel": False,
        "Cords Visiveis": False,
        "Ping Visivel": False,
        "Pré-Carregamento": True,
        "Ver": 1.0,
    }

    return info, config, estados


def _main() -> None:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

    pygame.init()
    pygame.mixer.init()

    tela = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
    pygame.display.set_caption("Simulador de Batalha Local 6v6")
    try:
        pygame.display.set_icon(Carregar_Imagem("Outros/Logo.png"))
    except Exception:
        pass

    relogio = pygame.time.Clock()

    info, config, estados = _montar_info_config_estados()

    VerificaSonoridade(config)

    # Chama exatamente a mesma cena/loop de batalha do jogo.
    BatalhaLoop(tela, relogio, estados, config, info)

    pygame.quit()


if __name__ == "__main__":
    _main()
