import random

class CombateIA:
    def __init__(self, equipe, equipeInimiga, dificuldade=0):
        self.equipe = equipe
        self.equipeI = equipeInimiga
        self.dificuldade = dificuldade
        self.JogadaAtual = []

    def MontarJogada(self):
        self.JogadaAtual = []
        if self.dificuldade != 0:
            return self.JogadaAtual  # só nível 0 por enquanto

        for idx, poke in enumerate(self.equipe):
            # precisa estar ativo e com vida
            if not poke or not poke.get("Ativo") or poke.get("Vida", 0) <= 0:
                continue

            movs = list(poke.get("MoveList") or [])
            if not movs:
                continue

            # normaliza para dicts e remove entradas inválidas
            movs = [m for m in movs if isinstance(m, dict)]
            if not movs:
                continue

            def _custo_move(move):
                custo = move.get("custo", move.get("Custo", 0))
                try:
                    return int(float(custo))
                except (TypeError, ValueError):
                    return 0

            energia_atual = poke.get("Energia", 0)
            try:
                energia_atual = int(float(energia_atual))
            except (TypeError, ValueError):
                energia_atual = 0

            # escolhe 1 dos 4 primeiros, priorizando os que cabem na energia
            candidatos = movs[:4] if len(movs) >= 4 else movs
            candidatos_viaveis = [m for m in candidatos if _custo_move(m) <= energia_atual]
            if not candidatos_viaveis:
                continue  # não age neste turno

            move_escolhido = random.choice(candidatos_viaveis)

            # nome do move (apenas o nome vai em "Movimento")
            nome_mov = (move_escolhido.get("Nome")
                        or move_escolhido.get("nome")
                        or move_escolhido.get("Ataque")
                        or move_escolhido.get("ataque")
                        or str(move_escolhido))

            # gerar alvos (casas) de forma bem burra/aleatória, coerente com o alvo básico
            alvo_raw = (move_escolhido.get("Alvo") or move_escolhido.get("alvo") or "")
            txt = str(alvo_raw).strip().lower()

            # padrão: lista de casas
            alvos = []

            if "sem alvo" in txt or txt == "sem":
                alvos = []
            elif "self" in txt or "própr" in txt or "propr" in txt:
                try:
                    pos = int(poke.get("Pos", 1))
                except Exception:
                    pos = 1
                pos = max(1, min(9, pos))
                alvos = [f"A{pos}"]
            elif "all" in txt or "todos" in txt:
                # seu sistema aceita repassar o token de "all/todos"
                alvos = [alvo_raw]
            elif "linha" in txt:
                # 3 casas na mesma fileira; lado inferido ou aleatório
                if ("ini" in txt or txt.endswith(" i")):
                    lado = "I"
                elif ("ali" in txt or txt.endswith(" a")):
                    lado = "A"
                else:
                    lado = random.choice(["A", "I"])
                row = random.choice([0, 1, 2])
                base = row * 3
                alvos = [f"{lado}{base+1}", f"{lado}{base+2}", f"{lado}{base+3}"]
            else:
                # célula / escolha / padrão: 1 casa aleatória; lado aleatório se não especificado
                if ("ini" in txt or txt.endswith(" i")):
                    lado = "I"
                elif ("ali" in txt or txt.endswith(" a")):
                    lado = "A"
                else:
                    lado = random.choice(["A", "I"])
                pos = random.randint(1, 9)
                alvos = [f"{lado}{pos}"]

            self.JogadaAtual.append({
                "Atacante": idx,        # índice do atacante na equipe
                "Movimento": nome_mov,  # apenas o nome do ataque
                "Alvos": alvos,         # lista de casas (ex.: ["I7"], ["A1","A2","A3"], ou [])
            })

        return self.JogadaAtual
