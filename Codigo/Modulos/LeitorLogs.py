import json
import pandas as pd

dfa = pd.read_csv("Dados/Animações.csv")

from Codigo.Prefabs.FunçõesPrefabs import Cartuchu

Parametros_Ataque = {
    "!None": 30,
    "LabaredaMultipla": 31.25,
    "Corte": 10.2,
    "BolhasVerdes": 20,
    "CorteDourado": 10.87,
    "ChuvaVermelha": 31.25,
    "ChuvaBrilhante": 33.33,
    "Agua": 23.81,
    "AtemporalRosa": 40,
    "BarreiraCelular": 12.5,
    "ChicoteMultiplo": 13.89,
    "CorteDuploRoxo": 33.33,
    "CorteMagico": 25,
    "CorteRicocheteadoRoxo": 8.93,
    "CorteRosa": 25,
    "DomoVerde": 11.76,
    "EnergiaAzul": 15.38,
    "Engrenagem": 8.7,
    "EspiralAzul": 22.22,
    "Estouro": 10.31,
    "EstouroMagico": 20,
    "EstouroVermelho": 21.74,
    "Explosao": 22.22,
    "ExplosaoPedra": 10.87,
    "ExplosaoVerde": 8.93,
    "ExplosaoVermelha": 33.33,
    "ExplosaoRoxa": 9.52,
    "FacasAzuis": 35.71,
    "FacasBrancas": 26.32,
    "FacasColoridas": 31.25,
    "FacasRosas": 40,
    "FeixeMagenta": 23.81,
    "FeixeRoxo": 10.42,
    "FluxoAzul": 15.38,
    "Fogo": 10.53,
    "Fumaça": 28.57,
    "GasRoxo": 12.82,
    "Garra": 12.5,
    "HexagonoLaminas": 27.78,
    "ImpactoRochoso": 8.7,
    "Karate": 11.11,
    "LuaAmarela": 55.56,
    "MagiaAzul": 38.46,
    "MagiaMagenta": 20.83,
    "MarcaBrilhosa": 26.32,
    "MarcaAmarela": 19.23,
    "MarcaAzul": 26.32,
    "Mordida": 8.7,
    "MultiplasFacas": 27.78,
    "OrbesRoxos": 35.71,
    "PedaçoColorido": 26.32,
    "RaioAzul": 83.33,
    "RajadaAmarela": 28.57,
    "RasgoMagenta": 38.46,
    "RasgosRosa": 35.71,
    "RedemoinhoAzul": 26.32,
    "RedemoinhoCosmico": 10.53,
    "SuperDescarga": 12.2,
    "SuperNova": 31.25,
    "TirosAmarelos": 40,
    "TornadoAgua": 25.64
}

efeitos_positivos = [
    "Regeneração",
    "Abençoado",
    "Imortal",
    "Fortificado",
    "Reforçado",
    "Amplificado",
    "Aprimorado",
    "Voando",
    "Flutuando",
    "Imune",
    "Energizado",
    "Preparado",
    "Provocando",
    "Furtivo",
    "Ilimitado",
    "Encantado",
    "Refletido",
    "Evasivo",
    "Focado",
    "Imparavel"
]

efeitos_negativos = [
    "Queimado",
    "Dormindo",
    "Envenenado",
    "Intoxicado",
    "Paralisado",
    "Incapacitado",
    "Vampirico",       
    "Encharcado",      
    "Quebrado",
    "Fragilizado",
    "Enfraquecido",
    "Neutralizado",
    "Enfeitiçado",
    "Atordoado",
    "Confuso",
    "Congelado",
    "Descarregado",
    "Bloqueado",
    "Amaldiçoado",
    "Enraizado"
]

atributos = [
    "Vida",
    "Atk",
    "Def",
    "SpA",
    "SpD",
    "Vel",
    "Mag",
    "Per",
    "Ene",
    "EnR",
    "CrD",
    "CrC",
    "Vamp",
    "Asse"
]

def LeitorLogs(LogRodada, parametros, _anim_aliados, _anim_inimigos,
               _slots_esquerda, _slots_direita, Ataques, Projeteis, Icones):
    """
    Leitor de logs NÃO bloqueante para rodar DENTRO do loop principal.
    Avança passo-a-passo com base em Animator.Continue da ÚLTIMA animação armada.
    Se não puder avançar agora, apenas retorna (na próxima chamada continua de onde parou).

    Estado incremental é salvo em parametros["LeitorState"].
    """

    # ---------- salvar log (debug) ----------
    with open("LogRodada.json", "w", encoding="utf-8") as f:
        json.dump(LogRodada, f, ensure_ascii=False, indent=4)

    # normaliza listas de animadores (somente os objetos)
    aliados  = [an for an, _ in _anim_aliados]
    inimigos = [an for an, _ in _anim_inimigos]

    # ---------- estado incremental ----------
    st = parametros.setdefault("LeitorState", {
        "i": 0,          # índice do Log na rodada
        "j": 0,          # índice do SubLog dentro do Log atual
        "step": 0,       # passo atual dentro do "plano" do SubLog
        "plan": None,    # lista de passos do SubLog atual
        "waiting_on": None,
        "_cache": {}
    })

    # helpers
    def _find_anim_by_id(pid, player_side):
        if player_side == parametros["Player"]:
            for anim in aliados:
                if anim.pokemon["ID"] == pid:
                    return anim
        else:
            for anim in inimigos:
                if anim.pokemon["ID"] == pid:
                    return anim
        return None

    def _resolve_agente(Log):
        ag_str = Log["Agente"].replace(" ", "")
        idx_s, pla_s = ag_str.split("/")
        idx_ag, pla_ag = int(idx_s), int(pla_s)
        agente = _find_anim_by_id(idx_ag, pla_ag)
        return agente, idx_ag, pla_ag

    def _resolve_alvo(SubLog):
        ag_str = SubLog["Alvo"].replace(" ", "")
        idx_s, pla_s = ag_str.split("/")
        idx_alvo, pla_alvo = int(idx_s), int(pla_s)
        alvo = _find_anim_by_id(idx_alvo, pla_alvo)
        return alvo, idx_alvo, pla_alvo

    def _slot_target(Log):
        pos_mira = None
        alvos_brutos = Log.get("AlvosBruto") or []
        if alvos_brutos:
            cod = str(alvos_brutos[0]).strip().upper()  # ex.: "I5" / "A2"
            lado = cod[0] if cod else "I"
            try:
                idx_slot = int(cod[1:])  # sem -1 (sua regra)
            except:
                idx_slot = 0

            # "I" e "A" relativos ao Player do LOG
            if lado == "I":
                lista_slots = _slots_direita if Log["Player"] == parametros["Player"] else _slots_esquerda
            else:  # 'A'
                lista_slots = _slots_esquerda if Log["Player"] == parametros["Player"] else _slots_direita

            if 0 <= idx_slot < len(lista_slots):
                srect = lista_slots[idx_slot]
                pos_mira = (int(srect.centerx), int(srect.centery))
        return pos_mira

    # Passo executável atômico
    def _start_step(step):
        """
        step = {
          "actor": Animator,
          "method": "iniciar_...",
          "kwargs": {...},         # inclui pct_continue quando aplicável
          "wait": True/False,      # se True, aguardamos actor.Continue
          "armed": False/True
        }
        """
        actor = step["actor"]
        meth  = step["method"]
        kwargs = step.get("kwargs", {})
        getattr(actor, meth)(**kwargs)     # dispara 1x
        step["armed"] = True
        if step.get("wait", True):
            st["waiting_on"] = actor
            return "WAIT"
        return "GO"

    # Constrói o plano (lista de passos) para um SubLog
    def _build_plan(Log, SubLog, cache):
        agente   = cache["agente"]
        alvo     = cache["alvo"]
        atkanima = cache["atkanima"]
        anima_key = cache["anima_key"]

        pos_mira = cache["pos_mira"] or alvo.pos

        # estado do sublog
        Dano = int(SubLog["Dano Final"])
        crit = bool(SubLog["Critico"])
        acertou = bool(SubLog["Acertou"])
        TemDano = Dano > 0
        Miss    = not acertou

        from Codigo.Cenas.Batalha import Fontes
        fonte = Fontes[18]
        cor_dano = (255, 0, 0) if crit else (255, 255, 0)
        cor_miss = (255, 255, 255)

        vel = float(atkanima["Velocidade"])

        steps = []

        def add(actor, method, wait=True, **kwargs):
            steps.append({"actor": actor, "method": method, "kwargs": kwargs, "wait": wait, "armed": False})

        # ====== tipo de contato / projétil ======
        contato = atkanima["Contato"]
        proj    = atkanima["Projetil"]

        if contato == "A":
            add(agente, "iniciar_avanco", True,
                alvo_pos=pos_mira, dur=vel, pct_continue=0.50)
            add(alvo, "iniciar_sofrergolpe", True,
                frames=Ataques[atkanima[anima_key]],
                fps=Parametros_Ataque[atkanima[anima_key]],
                pct_continue=0.85)

        elif contato == "I":
            add(agente, "iniciar_investida", True,
                alvo_pos=pos_mira, dur=vel, pct_continue=0.50)
            add(alvo, "iniciar_sofrergolpe", True,
                frames=Ataques[atkanima[anima_key]],
                fps=Parametros_Ataque[atkanima[anima_key]],
                pct_continue=0.85)

        else:
            if proj == "fluxo":
                add(agente, "iniciar_disparo", True,
                    alvo_pos=pos_mira, dur=vel, pct_continue=0.90)
                add(alvo, "iniciar_sofrergolpe", True,
                    frames=Ataques[atkanima[anima_key]],
                    fps=Parametros_Ataque[atkanima[anima_key]],
                    pct_continue=0.85)
            elif proj == "-":
                add(alvo, "iniciar_sofrergolpe", True,
                    frames=Ataques[atkanima[anima_key]],
                    fps=Parametros_Ataque[atkanima[anima_key]],
                    pct_continue=0.85)
            else:
                add(agente, "iniciar_disparo", True,
                    alvo_pos=pos_mira,
                    proj_img=Projeteis[proj],
                    dur=vel, pct_continue=0.90)
                add(alvo, "iniciar_sofrergolpe", True,
                    frames=Ataques[atkanima[anima_key]],
                    fps=Parametros_Ataque[atkanima[anima_key]],
                    pct_continue=0.85)

        # ====== pós-hit ======
        if TemDano:
            add(alvo, "iniciar_tomardano", True,
                dur=max(0.12, Dano/100.0), freq=12.0, pct_continue=0.25)
            add(alvo, "iniciar_cartucho", False,
                cartucho_surf=Cartuchu(valor=Dano, cor=cor_dano, fonte=fonte, crit=(2 if crit else 5)))
        elif Miss:
            add(alvo, "iniciar_cartucho", False,
                cartucho_surf=Cartuchu(valor="Miss", cor=cor_miss, fonte=fonte, crit=0))

        return steps

    # Constrói plano para REGISTROS pós-ataque (não bloqueante; encadeado por Continue)
    def _build_plan_registros(regs, agente):
        steps = []
        if not regs:
            return steps

        from Codigo.Cenas.Batalha import Fontes
        fonte = Fontes[18]

        ups_total, downs_total = [], []
        turnos_pos_total, turnos_neg_total = 0, 0
        barreira_total = 0

        for registro in regs:
            # Cura
            cura = int(registro.get("Cura", 0))
            if cura > 0:
                dur = 0.2 + cura * 0.005
                steps.append({"actor": agente, "method": "iniciar_curar",
                              "kwargs": {"dur": dur, "freq": 12.0, "pct_continue": 0.40},
                              "wait": True, "armed": False})
                steps.append({"actor": agente, "method": "iniciar_cartucho",
                              "kwargs": {"cartucho_surf": Cartuchu(valor=cura, cor=(0,255,0), fonte=fonte, crit=0)},
                              "wait": False, "armed": False})

            # Barreira
            barreira_total += int(registro.get("Barreira", 0))

            # ups & downs (usa listas globais presumidas)
            for a in atributos:
                v = int(registro.get(a, 0))
                if v > 0:
                    ups_total.append((a, v))
                elif v < 0:
                    downs_total.append((a, v))

            # turnos positivos/negativos (usa listas globais presumidas)
            turnos_pos_total += sum(int(registro.get(e, 0)) for e in efeitos_positivos)
            turnos_neg_total += sum(int(registro.get(e, 0)) for e in efeitos_negativos)

        # Buffs (positivos)
        if barreira_total > 0 or ups_total or turnos_pos_total > 0:
            dur_b = 0.40 + len(ups_total)*0.12 + barreira_total*0.002 + turnos_pos_total*0.15
            steps.append({"actor": agente, "method": "iniciar_buff",
                          "kwargs": {"dur": dur_b, "qtd": 6, "area": (60, 40), "cor": (90,200,255),
                                     "pct_continue": 0.50, "debuff": False},
                          "wait": True, "armed": False})

            if barreira_total > 0:
                steps.append({"actor": agente, "method": "iniciar_cartucho",
                              "kwargs": {"cartucho_surf": Cartuchu(valor=barreira_total, cor=(0,0,255), fonte=fonte, crit=0)},
                              "wait": False, "armed": False})

            for (atr, v) in ups_total:
                steps.append({"actor": agente, "method": "iniciar_cartucho",
                              "kwargs": {"cartucho_surf": Cartuchu(
                                  valor=f"+{v} {atr}", cor=(255,190,210), fonte=fonte,
                                  icon=Icones[atr], crit=3)},
                              "wait": False, "armed": False})

        # Debuffs (negativos)
        if downs_total or turnos_neg_total > 0:
            dur_d = 0.40 + len(downs_total)*0.12 + turnos_neg_total*0.15
            steps.append({"actor": agente, "method": "iniciar_buff",
                          "kwargs": {"dur": dur_d, "qtd": 6, "area": (60, 40), "cor": (255,120,120),
                                     "pct_continue": 0.50, "debuff": True},
                          "wait": True, "armed": False})

            for (atr, v) in downs_total:
                steps.append({"actor": agente, "method": "iniciar_cartucho",
                              "kwargs": {"cartucho_surf": Cartuchu(
                                  valor=f"{v} {atr}", cor=(255,190,210), fonte=fonte,
                                  icon=Icones[atr], crit=3)},
                              "wait": False, "armed": False})

        return steps

    # ===================== MOTOR DE AVANÇO (não bloqueante) ======================
    # Permite "pular" steps já resolvidos na volta, sem repetir efeitos.
    budget = 16  # limite de passos por chamada para evitar loop longo num único frame

    while budget > 0:
        budget -= 1

        # terminou a rodada?
        if st["i"] >= len(LogRodada):
            parametros["Pronto"] = False
            parametros["Rodou"] = True
            parametros["Processando"] = False
            parametros["LogAtual"] = []
            parametros["LeitorState"] = {"i": 0, "j": 0, "step": 0, "plan": None, "waiting_on": None, "_cache": {}}
            return

        Log = LogRodada[st["i"]]
        SubLogs = Log.get("SubLogs", [])

        # terminou o Log atual?
        if st["j"] >= len(SubLogs):
            if st.get("_doing_regs") is None:
                agente, _, _ = _resolve_agente(Log)
                regs_steps = _build_plan_registros(Log.get("Registros", []), agente)
                if regs_steps:
                    st["plan"] = regs_steps
                    st["step"] = 0
                    st["_doing_regs"] = True
                    continue
                else:
                    st["_doing_regs"] = False

            # fim do Log → próximo
            st["i"] += 1
            st["j"] = 0
            st["step"] = 0
            st["plan"] = None
            st["_cache"].clear()
            st.pop("_doing_regs", None)
            continue

        # ---------- prepara cache do SubLog (1x) ----------
        if not st["plan"]:
            SubLog = SubLogs[st["j"]]

            agente, idx_ag, pla_ag   = _resolve_agente(Log)
            alvo,   idx_alvo, pla_alvo = _resolve_alvo(SubLog)

            atkanimadf = dfa[dfa["Nome"] == Log["Code Ataque"]]
            atkanima = atkanimadf.iloc[0].to_dict()
            anima_key = "Animação" if (pla_alvo == parametros["Player"]) else "AnimaçãoAliado"

            pos_mira = _slot_target(Log)

            st["_cache"] = {
                "agente": agente, "alvo": alvo,
                "idx_ag": idx_ag, "pla_ag": pla_ag,
                "idx_alvo": idx_alvo, "pla_alvo": pla_alvo,
                "atkanima": atkanima, "anima_key": anima_key,
                "pos_mira": pos_mira
            }

            st["plan"] = _build_plan(Log, SubLog, st["_cache"])
            st["step"]  = 0

        # ---------- executar/avançar um step ----------
        plan = st["plan"]
        k = st["step"]

        if k >= len(plan):
            # terminou SubLog → próximo
            st["j"] += 1
            st["step"] = 0
            st["plan"] = None
            st["_cache"].clear()
            st["waiting_on"] = None
            continue

        step = plan[k]

        if not step["armed"]:
            result = _start_step(step)
            if result == "WAIT":
                return  # não bloqueia o loop principal
            st["step"] += 1
            continue

        if step.get("wait", True):
            actor = step["actor"]
            if not actor.Continue:
                st["waiting_on"] = actor
                return
            st["waiting_on"] = None
            st["step"] += 1
            continue
        else:
            st["step"] += 1
            continue

