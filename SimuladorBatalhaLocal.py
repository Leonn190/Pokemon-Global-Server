"""Simulador de batalha local "idêntico" ao jogo (abre a tela real de batalha).

Este arquivo NÃO cria uma UI paralela.
Ele monta um contexto fake mínimo (player + alvo de confronto) e chama a
mesma cena `Codigo.Cenas.Batalha.BatalhaLoop` usada no jogo.
"""

from __future__ import annotations

import ctypes
import os
import random
from dataclasses import dataclass
from typing import Dict, List

import pygame

from Codigo.Carregar.CarregamentoAvançado import CarregamentoAvançado
from Codigo.Carregar.CarregamentoBasico import CarregamentoBasico
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


def _nomes_com_animacao_valida() -> set[str]:
    pasta = os.path.join("Recursos", "Visual", "Pokemons", "Animação")
    validos: set[str] = set()
    if not os.path.isdir(pasta):
        return validos

    for nome in os.listdir(pasta):
        caminho = os.path.join(pasta, nome)
        if not os.path.isdir(caminho):
            continue
        tem_frame = any(arq.lower().endswith(".png") for arq in os.listdir(caminho))
        if tem_frame:
            validos.add(nome.lower())
    return validos


def _gerar_pokemon_materializado_comum(nomes_permitidos: set[str] | None = None) -> Dict:
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

    if nomes_permitidos:
        candidatos = candidatos[candidatos["Nome"].astype(str).str.lower().isin(nomes_permitidos)]

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


def _gerar_time_materializado_6(nomes_permitidos: set[str] | None = None) -> List[Dict]:
    return [_gerar_pokemon_materializado_comum(nomes_permitidos) for _ in range(6)]


def _criar_player_fake(outros: Dict, nomes_permitidos: set[str]) -> PlayerFake:
    equipe = _gerar_time_materializado_6(nomes_permitidos)
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


def _criar_alvo_fake(nomes_permitidos: set[str]) -> AlvoConfrontoFake:
    return AlvoConfrontoFake(Dados=_gerar_pokemon_materializado_comum(nomes_permitidos))


def _montar_info_config_estados(Mundo) -> tuple[Dict, Dict, Dict]:
    info = {
        "Carregado": False,
        "Alvo": "Batalha",
        "Escuro": 100,
        "AcabouDeSairConfronto": False,
    }

    # Carrega os mesmos assets da pipeline do jogo.
    CarregamentoBasico(info)
    CarregamentoAvançado(info, Pré=True)

    _, _, _, _, outros, _, _, _, _, animacoes, _ = info["Conteudo"]
    nomes_permitidos = _nomes_com_animacao_valida()

    # limpeza extra: remove entradas de animação vazias para forçar fallback do carregador normal
    for chave in list(animacoes.keys()):
        if not animacoes[chave]:
            del animacoes[chave]

    # Injeta player fake no módulo Mundo, que é de onde a cena de batalha lê.
    Mundo.player = _criar_player_fake(outros, nomes_permitidos)

    info["ParametrosConfronto"] = {
        "BatalhaSimples": True,
        "AlvoConfronto": _criar_alvo_fake(nomes_permitidos),
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
    pygame.font.init()
    pygame.mixer.init()

    # Importa cenas somente após inicializar pygame/font,
    # pois alguns módulos constroem fontes no import-time.
    from Codigo.Cenas import Mundo
    from Codigo.Cenas import Batalha as ModBatalha

    tela = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
    pygame.display.set_caption("Simulador de Batalha Local 6v6")
    try:
        pygame.display.set_icon(Carregar_Imagem("Outros/Logo.png"))
    except Exception:
        pass

    relogio = pygame.time.Clock()

    info, config, estados = _montar_info_config_estados(Mundo)

    # Patch local-only: evita GerarMatilha puxar espécies sem assets de animação.
    nomes_permitidos = _nomes_com_animacao_valida()
    ModBatalha.GerarMatilha = lambda pokemon, max=6: _gerar_time_materializado_6(nomes_permitidos)[:max]

    VerificaSonoridade(config)

    # Chama exatamente a mesma cena/loop de batalha do jogo.
    ModBatalha.BatalhaLoop(tela, relogio, estados, config, info)

    pygame.quit()


if __name__ == "__main__":
    _main()
