"""Simulador de batalha 6v6 com tela própria (pygame), sem abrir o jogo completo.

- Reutiliza geração e motor de batalha do projeto.
- Cria contexto local de luta (6x6), define 3 ativos por lado e deixa o jogador controlar o time 1.
- Roda loop a 180 FPS.

Controles:
- TAB: trocar Pokémon aliado selecionado
- 1/2/3/4: escolher ataque do aliado selecionado
- Q/W/E: escolher alvo (inimigo ativo 1/2/3)
- ESPAÇO: confirmar ação do aliado selecionado
- ENTER: executar rodada
- R: limpar ações da rodada
- ESC: sair
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

import pandas as pd
import pygame

from Codigo.Funções.FunçõesAtaques import AtkDic
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

_DF_ATAQUES = pd.read_csv("Dados/Ataques.csv")
FPS = 180


def _gerar_pokemon_comum() -> Dict:
    raridade_col, nome_col, estagio_col = "Raridade", "Nome", "Estagio"
    candidatos = df_pokemons

    if raridade_col in candidatos.columns:
        comuns = candidatos[candidatos[raridade_col].astype(str).str.lower().str.contains("comum", na=False)]
        if not comuns.empty:
            candidatos = comuns

    if estagio_col in candidatos.columns:
        est = candidatos[estagio_col].astype(str).str.replace(",", ".", regex=False).str.strip()
        est = est[~est.str.contains(r"[^0-9\.\-]", na=True)]
        candidatos = candidatos.loc[est.index]

    if raridade_col in candidatos.columns:
        candidatos = candidatos[candidatos[raridade_col].astype(str).str.strip() != "-"]

    nomes = candidatos[nome_col].dropna().tolist() or df_pokemons[nome_col].dropna().tolist()
    if not nomes:
        raise RuntimeError("Sem nomes para gerar Pokémon.")

    for _ in range(250):
        nome = random.choice(nomes)
        try:
            compactado = criar_pokemon_especifico(nome)
            if not compactado:
                continue
            mat = MaterializarPokemon(desserializar_pokemon(compactado))
            return GeraPokemonBatalha(mat)
        except (ValueError, TypeError):
            continue

    raise RuntimeError("Falha ao gerar Pokémon válido.")


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
    try:
        return float(move.get("custo", move.get("Custo", 0)) or 0)
    except (TypeError, ValueError):
        return 0.0


def _ataque_suportado(nome_ataque: str) -> bool:
    """Filtro robusto: apenas ataques diretos (n/e) sem funções irregulares."""
    linha = _DF_ATAQUES[_DF_ATAQUES["Ataque"] == nome_ataque]
    if linha.empty:
        return False
    ataque = linha.iloc[0]
    estilo = str(ataque.get("Estilo", "")).lower().strip()
    funcoes = str(ataque.get("função", "")).lower()
    if funcoes in {"nan", "none"}:
        funcoes = ""

    if estilo not in {"n", "e"}:
        return False

    if any(s in funcoes for s in ("i", "m", "s", "p", "f", "g")):
        return False

    # proteção extra contra callback inesperado
    codigo = int(ataque["Code"])
    for sufixo in ("i", "m", "s", "p", "f", "g"):
        if sufixo in funcoes and f"{codigo}{sufixo}" in AtkDic:
            return False

    return True


def _moves_viaveis_seguros(poke: Dict) -> List[Dict]:
    movelist = [m for m in (poke.get("MoveList") or []) if isinstance(m, dict)]
    energia = float(poke.get("Energia", 0) or 0)
    viaveis = [m for m in movelist if _custo_move(m) <= energia]
    return [m for m in viaveis if _nome_move(m) and _ataque_suportado(_nome_move(m))]


def _ativos_vivos_indices(equipe: List[Dict]) -> List[int]:
    return [i for i, p in enumerate(equipe) if p.get("Ativo") and p.get("Vida", 0) > 0 and p.get("Pos")]


def _alvo_inimigo_por_ordem(equipe_inimiga: List[Dict], ordem: int) -> Optional[str]:
    idxs = _ativos_vivos_indices(equipe_inimiga)
    if ordem < 0 or ordem >= len(idxs):
        return None
    pos = int(equipe_inimiga[idxs[ordem]]["Pos"])
    return f"I{pos}"


def _acao_mover_segura(poke: Dict, idx: int) -> Dict:
    pos_atual = int(poke.get("Pos", 5) or 5)
    opcoes = [p for p in range(1, 10) if p != pos_atual]
    return {"agente": idx, "ataque": "Mover", "alvo": random.choice(opcoes) if opcoes else pos_atual}


def _gerar_jogada_ia(equipe: List[Dict], inimigos: List[Dict]) -> List[Dict]:
    jogadas = []
    for idx in _ativos_vivos_indices(equipe):
        poke = equipe[idx]
        moves = _moves_viaveis_seguros(poke)
        if not moves:
            jogadas.append(_acao_mover_segura(poke, idx))
            continue
        mov = random.choice(moves)
        alvos = _ativos_vivos_indices(inimigos)
        if not alvos:
            jogadas.append(_acao_mover_segura(poke, idx))
            continue
        alvo_idx = random.choice(range(len(alvos)))
        alvo = _alvo_inimigo_por_ordem(inimigos, alvo_idx)
        if not alvo:
            jogadas.append(_acao_mover_segura(poke, idx))
            continue
        jogadas.append({"agente": idx, "ataque": _nome_move(mov), "alvo": [alvo]})
    return jogadas


def _render_texto(tela: pygame.Surface, fonte: pygame.font.Font, texto: str, x: int, y: int, cor=(235, 235, 235)) -> None:
    tela.blit(fonte.render(texto, True, cor), (x, y))


def _render_equipes(
    tela: pygame.Surface,
    fonte: pygame.font.Font,
    equipe_aliada: List[Dict],
    equipe_inimiga: List[Dict],
    aliado_sel_idx: Optional[int],
) -> None:
    _render_texto(tela, fonte, "ALIADOS (você)", 30, 20, (120, 220, 255))
    y = 50
    for i, p in enumerate(equipe_aliada):
        marcador = ">" if i == aliado_sel_idx else " "
        ativo = "A" if p.get("Ativo") else "-"
        nome = str(p.get("Nome", "???"))
        vida = int(max(0, p.get("Vida", 0)))
        ene = int(max(0, p.get("Energia", 0)))
        pos = p.get("Pos")
        _render_texto(tela, fonte, f"{marcador} [{i}] {ativo} P{pos} {nome[:18]} HP:{vida:4d} EN:{ene:3d}", 30, y)
        y += 20

    _render_texto(tela, fonte, "INIMIGOS", 730, 20, (255, 120, 120))
    y = 50
    for i, p in enumerate(equipe_inimiga):
        ativo = "A" if p.get("Ativo") else "-"
        nome = str(p.get("Nome", "???"))
        vida = int(max(0, p.get("Vida", 0)))
        ene = int(max(0, p.get("Energia", 0)))
        pos = p.get("Pos")
        _render_texto(tela, fonte, f"[{i}] {ativo} P{pos} {nome[:18]} HP:{vida:4d} EN:{ene:3d}", 730, y)
        y += 20


def _render_estado_turno(
    tela: pygame.Surface,
    fonte: pygame.font.Font,
    fonte_pequena: pygame.font.Font,
    turno: int,
    aliado_sel_idx: Optional[int],
    move_sel: Optional[str],
    alvo_sel: Optional[str],
    acoes_confirmadas: Dict[int, Dict],
    logs_recentes: List[str],
    equipe_aliada: List[Dict],
    equipe_inimiga: List[Dict],
) -> None:
    _render_texto(tela, fonte, f"Turno: {turno}", 30, 360, (255, 240, 120))

    if aliado_sel_idx is not None and aliado_sel_idx < len(equipe_aliada):
        poke = equipe_aliada[aliado_sel_idx]
        moves = _moves_viaveis_seguros(poke)
        _render_texto(tela, fonte, f"Selecionado: [{aliado_sel_idx}] {poke.get('Nome', '???')}", 30, 390)
        _render_texto(tela, fonte_pequena, "Ataques (1/2/3/4):", 30, 418, (180, 220, 255))
        for i in range(4):
            nome = _nome_move(moves[i]) if i < len(moves) else "(vazio)"
            _render_texto(tela, fonte_pequena, f"{i+1}) {nome}", 30, 440 + i * 18)

    ativos_inimigos = _ativos_vivos_indices(equipe_inimiga)
    _render_texto(tela, fonte_pequena, "Alvos (Q/W/E = inimigo ativo 1/2/3):", 30, 525, (255, 200, 200))
    for i in range(3):
        if i < len(ativos_inimigos):
            idx = ativos_inimigos[i]
            p = equipe_inimiga[idx]
            _render_texto(tela, fonte_pequena, f"{['Q','W','E'][i]} -> [{idx}] P{p.get('Pos')} {p.get('Nome')}", 30, 548 + i * 18)
        else:
            _render_texto(tela, fonte_pequena, f"{['Q','W','E'][i]} -> (sem alvo)", 30, 548 + i * 18)

    _render_texto(tela, fonte_pequena, f"Pré-seleção move: {move_sel}", 420, 390, (200, 220, 255))
    _render_texto(tela, fonte_pequena, f"Pré-seleção alvo: {alvo_sel}", 420, 410, (255, 200, 200))
    _render_texto(tela, fonte_pequena, f"Ações confirmadas: {len(acoes_confirmadas)}", 420, 430, (200, 255, 200))

    _render_texto(tela, fonte_pequena, "TAB troca aliado | SPACE confirma ação | ENTER executa rodada | R limpa | ESC sai", 30, 620, (180, 180, 180))

    _render_texto(tela, fonte, "LOGS RECENTES", 420, 460, (255, 220, 140))
    y = 490
    for linha in logs_recentes[-7:]:
        _render_texto(tela, fonte_pequena, linha, 420, y, (220, 220, 220))
        y += 18


def jogar_batalha_local_6v6() -> None:
    pygame.init()
    tela = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Simulador de Batalha Local 6v6")
    clock = pygame.time.Clock()
    fonte = pygame.font.SysFont("consolas", 22)
    fonte_pequena = pygame.font.SysFont("consolas", 17)

    equipe_1 = _gerar_equipe(6)
    equipe_2 = _gerar_equipe(6)
    _definir_ativos(equipe_1)
    _definir_ativos(equipe_2)
    sala = criar_e_inicializar_sala_local(equipe_1, equipe_2, "P1_LOCAL", "IA_LOCAL")

    turno = 1
    logs_recentes: List[str] = ["Batalha iniciada."]

    aliado_sel_ordem = 0
    pre_move: Optional[str] = None
    pre_alvo: Optional[str] = None
    acoes_confirmadas: Dict[int, Dict] = {}

    running = True
    while running:
        aliados_idx = _ativos_vivos_indices(sala["pokemons_jogador1"])
        inimigos_idx = _ativos_vivos_indices(sala["pokemons_jogador2"])

        if not aliados_idx or not inimigos_idx:
            vencedor = "Inimigos" if not aliados_idx else "Você"
            logs_recentes.append(f"Fim da batalha! Vencedor: {vencedor}")
            running = False

        aliado_sel_idx = aliados_idx[aliado_sel_ordem % len(aliados_idx)] if aliados_idx else None

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_TAB and aliados_idx:
                    aliado_sel_ordem = (aliado_sel_ordem + 1) % len(aliados_idx)
                    pre_move, pre_alvo = None, None
                elif ev.key == pygame.K_r:
                    acoes_confirmadas.clear()
                    pre_move, pre_alvo = None, None
                elif aliado_sel_idx is not None:
                    poke_sel = sala["pokemons_jogador1"][aliado_sel_idx]
                    moves = _moves_viaveis_seguros(poke_sel)

                    if ev.key in (pygame.K_1, pygame.K_KP1):
                        pre_move = _nome_move(moves[0]) if len(moves) > 0 else None
                    elif ev.key in (pygame.K_2, pygame.K_KP2):
                        pre_move = _nome_move(moves[1]) if len(moves) > 1 else None
                    elif ev.key in (pygame.K_3, pygame.K_KP3):
                        pre_move = _nome_move(moves[2]) if len(moves) > 2 else None
                    elif ev.key in (pygame.K_4, pygame.K_KP4):
                        pre_move = _nome_move(moves[3]) if len(moves) > 3 else None
                    elif ev.key == pygame.K_q:
                        pre_alvo = _alvo_inimigo_por_ordem(sala["pokemons_jogador2"], 0)
                    elif ev.key == pygame.K_w:
                        pre_alvo = _alvo_inimigo_por_ordem(sala["pokemons_jogador2"], 1)
                    elif ev.key == pygame.K_e:
                        pre_alvo = _alvo_inimigo_por_ordem(sala["pokemons_jogador2"], 2)
                    elif ev.key == pygame.K_SPACE:
                        if pre_move and pre_alvo:
                            acoes_confirmadas[aliado_sel_idx] = {
                                "agente": aliado_sel_idx,
                                "ataque": pre_move,
                                "alvo": [pre_alvo],
                            }
                            logs_recentes.append(f"Ação confirmada [{aliado_sel_idx}]: {pre_move} -> {pre_alvo}")
                            pre_move, pre_alvo = None, None
                        else:
                            logs_recentes.append("Selecione ataque (1-4) e alvo (Q/W/E) antes de confirmar.")
                    elif ev.key == pygame.K_RETURN:
                        jogadas_p1 = []
                        for idx in aliados_idx:
                            poke = sala["pokemons_jogador1"][idx]
                            if idx in acoes_confirmadas:
                                jogadas_p1.append(acoes_confirmadas[idx])
                            else:
                                jogadas_p1.append(_acao_mover_segura(poke, idx))

                        jogadas_p2 = _gerar_jogada_ia(sala["pokemons_jogador2"], sala["pokemons_jogador1"])

                        try:
                            log_turno, _ = receber_e_executar_jogadas(sala, jogadas_p1, jogadas_p2)
                            logs_recentes.append(f"Rodada {turno} executada. Eventos: {len(log_turno) if log_turno else 0}")
                            turno += 1
                        except Exception as exc:
                            logs_recentes.append(f"ERRO na rodada: {exc}")

                        acoes_confirmadas.clear()
                        pre_move, pre_alvo = None, None

        tela.fill((20, 24, 30))
        _render_equipes(tela, fonte_pequena, sala["pokemons_jogador1"], sala["pokemons_jogador2"], aliado_sel_idx)
        _render_estado_turno(
            tela,
            fonte,
            fonte_pequena,
            turno,
            aliado_sel_idx,
            pre_move,
            pre_alvo,
            acoes_confirmadas,
            logs_recentes,
            sala["pokemons_jogador1"],
            sala["pokemons_jogador2"],
        )
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def _main() -> None:
    jogar_batalha_local_6v6()


if __name__ == "__main__":
    _main()
