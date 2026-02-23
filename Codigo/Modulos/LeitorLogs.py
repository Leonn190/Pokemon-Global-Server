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

def LeitorLogs(LogRodada, parametros, 
               _anim_aliados, _anim_inimigos,
               _slots_esquerda, _slots_direita, Ataques, Projeteis, Icones):
    import time, json
    from Codigo.Cenas.Batalha import Fontes

    # -------- salvar rodada em JSON (debug) --------
    try:
        with open("LogRodada.json", "w", encoding="utf-8") as f:
            json.dump(LogRodada, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("[LEITOR] Falha ao salvar LogRodada.json:", e)

    # ---------- animadores ----------
    aliados  = [an for an, _ in _anim_aliados]
    inimigos = [an for an, _ in _anim_inimigos]
    todos_anim = aliados + inimigos

    # ---------- estado ----------
    st = parametros.setdefault("LeitorState", {
        "i": 0, "j": 0, "step": 0, "plan": None, "waiting_on": None, "_cache": {},
        "_contact_until": {}  # semáforo por agente p/ animações de CONTATO
    })
    # retrocompat: estados antigos podem existir sem chaves novas
    st.setdefault("_cache", {})
    st.setdefault("_contact_until", {})

    # cooldown entre logs
    if st.get("_cooldown_until"):
        if time.time() < st["_cooldown_until"]:
            return
        else:
            st.pop("_cooldown_until", None)

    # ---------- helpers (lado/pos) ----------
    def _poke_dict(anim):
        d = getattr(anim, "Pokemon", None)
        return d if isinstance(d, dict) else getattr(anim, "pokemon", {})

    def _other_side(s): return 2 if s == 1 else 1
    PLAYER_SIDE = int(parametros.get("Player", 1))

    # listas de referência para checar lado por equipe
    equipe_aliada  = parametros.get("EquipeAliada", []) or []
    equipe_inimiga = parametros.get("EquipeInimiga", []) or []

    aliada_ids  = {int(p.get("ID")) for p in equipe_aliada  if isinstance(p, dict) and "ID" in p}
    inimiga_ids = {int(p.get("ID")) for p in equipe_inimiga if isinstance(p, dict) and "ID" in p}

    def _anim_side(anim):
        """Resolve 1/2 usando membership em EquipeAliada/EquipeInimiga (identidade ou ID)."""
        p = _poke_dict(anim)
        pid = p.get("ID")
        if p and p in equipe_aliada:
            return PLAYER_SIDE
        if p and p in equipe_inimiga:
            return _other_side(PLAYER_SIDE)
        if pid is not None:
            try: pid_int = int(pid)
            except: pid_int = pid
            if pid_int in aliada_ids:
                return PLAYER_SIDE
            if pid_int in inimiga_ids:
                return _other_side(PLAYER_SIDE)
        return PLAYER_SIDE if anim in aliados else _other_side(PLAYER_SIDE)

    def _pos_code_view_from_anim(anim):
        """A# / I# no referencial local a partir de Pokemon['Pos'] numérico + lado do animador."""
        p = _poke_dict(anim)
        pos_val = p.get("Pos", None)
        try:
            idx = int(str(pos_val).strip())
        except Exception:
            return None
        prefix = "A" if _anim_side(anim) == PLAYER_SIDE else "I"
        return f"{prefix}{idx}"

    def _find_anim_by_slotcode_view(slot_code_view):
        code = str(slot_code_view).strip().upper()
        for anim in todos_anim:
            if _pos_code_view_from_anim(anim) == code:
                return anim
        return None

    def _code_from_log_to_view(code_log, log_player):
        """Converte I#/A# do LOG para o referencial LOCAL, usando Log['Player'] e parametros['Player']."""
        code_log = str(code_log).strip().upper()
        if int(log_player) == PLAYER_SIDE:
            return code_log
        if code_log.startswith("I"): return "A" + code_log[1:]
        if code_log.startswith("A"): return "I" + code_log[1:]
        return code_log

    def _slot_center(Log, slot_code_log):
        """Centro geométrico do retângulo do slot no referencial do LOG (para avanço/projétil)."""
        code = str(slot_code_log).strip().upper()
        lado = code[0]
        idx_slot = (int(code[1:]) if len(code) > 1 else 1) - 1  # 1-based → 0-based
        if lado == "I":
            lista = _slots_direita if int(Log["Player"]) == PLAYER_SIDE else _slots_esquerda
        else:
            lista = _slots_esquerda if int(Log["Player"]) == PLAYER_SIDE else _slots_direita
        idx_slot = max(0, min(idx_slot, len(lista) - 1))
        r = lista[idx_slot]
        return (int(r.centerx), int(r.centery))

    def _sublog_by_id_side(SubLogs):
        m = {}
        for sl in SubLogs:
            idx_s, pla_s = str(sl["Alvo"]).replace(" ", "").split("/")
            m[(int(idx_s), int(pla_s))] = sl
        return m

    def _build_sublog_maps(Log):
        """
        id_to_sublog: (id, side) -> SubLog
        slot_to_sublog: ViewSlotCode('A#'/'I#') -> SubLog (via animadores atuais)
        """
        id_map = _sublog_by_id_side(Log.get("SubLogs", []))
        slot_map = {}
        for anim in todos_anim:
            p = _poke_dict(anim)
            pid = p.get("ID")
            if pid is None:
                continue
            side = _anim_side(anim)
            sl = id_map.get((int(pid), int(side)))
            pos_code_view = _pos_code_view_from_anim(anim)
            if sl is not None and pos_code_view:
                slot_map[pos_code_view] = sl
        return id_map, slot_map

    def _find_anim_by_id(pid, player_side):
        pool = aliados if player_side == PLAYER_SIDE else inimigos
        for anim in pool:
            p = _poke_dict(anim)
            if p.get("ID") == pid:
                return anim
        return None

    def _resolve_agente(Log):
        idx_s, pla_s = str(Log["Agente"]).replace(" ", "").split("/")
        idx_ag, pla_ag = int(idx_s), int(pla_s)
        return _find_anim_by_id(idx_ag, pla_ag), idx_ag, pla_ag

    # ---------- helpers EXECUTIVOS (mutação oficial) ----------
    def _normalize_attr_key(k: str):
        """mapa de chaves do log -> chaves do dicionário oficial."""
        mapa = {
            "atk":  "Atk",  "def":  "Def",
            "spa":  "SpA",  "spd":  "SpD",
            "vel":  "Vel",  "vida": "Vida",
            "mag":  "Mag",  "per":  "Per",
            "ene":  "Energia",  "energia": "Energia", "enr":  "EnR",
            "crd":  "CrD",  "crc":  "CrC",
            "vamp": "Vamp", "asse": "Asse",
        }
        
        return mapa.get(str(k).lower(), str(k).capitalize())

    def _get_official_team(side_num: int):
        return (parametros.get("EquipeAliada", []),
                parametros.get("EquipeInimiga", []),
                PLAYER_SIDE)

    def _find_official_by_id_side(pid: int, side_num: int):
        aliada, inimiga, ps = _get_official_team(side_num)
        team = aliada if int(side_num) == int(ps) else inimiga
        for pok in team:
            try:
                if int(pok.get("ID")) == int(pid):
                    return pok
            except Exception:
                pass
        return None

    def _find_side_by_id(pid: int):
        """Descobre lado do pokémon pelo ID nas equipes oficiais."""
        aliada, inimiga, ps = _get_official_team(PLAYER_SIDE)
        for pok in aliada:
            try:
                if int(pok.get("ID")) == int(pid):
                    return int(ps)
            except Exception:
                pass
        for pok in inimiga:
            try:
                if int(pok.get("ID")) == int(pid):
                    return 2 if int(ps) == 1 else 1
            except Exception:
                pass
        return None

    def _add_delta(d: dict, key_candidates, delta):
        """soma delta na 1ª chave existente; se Vida/HP, limita mínimo 0."""
        if not isinstance(key_candidates, (list, tuple)):
            key_candidates = [key_candidates]
        for k in key_candidates:
            if k in d:
                try:
                    d[k] = d.get(k, 0) + delta
                    if k in ("Vida", "HP", "Hp"):
                        if d[k] < 0: d[k] = 0
                except Exception:
                    pass
                return True
        return False

    def _mutate_official_by_id_side(pid: int, side_num: int, changes: dict):
        """changes aceita chaves oficiais ('Vida','Barreira','Atk'...) ou brutas ('atk','hp'...)."""
        pok = _find_official_by_id_side(pid, side_num)
        if not pok:
            print(f"[LEITOR][EXEC] Não achei pokémon oficial ID={pid} side={side_num} para mutação.")
            return
        for k, v in changes.items():
            if k in ("Vida", "HP", "Hp") or str(k).lower() in ("vida", "hp"):
                if not _add_delta(pok, ("Vida", "HP", "Hp"), int(v)):
                    # se não existe, cria Vida
                    pok["Vida"] = max(0, int(pok.get("Vida", 0)) + int(v))
                continue
            if str(k).lower() in ("energia", "ene"):
                atual = float(pok.get("Energia", 0))
                novo = atual + float(v)
                teto = float(pok.get("Ene", novo))
                pok["Energia"] = max(0.0, min(novo, teto))
                continue
            if str(k).lower() == "barreira" or k == "Barreira":
                if not _add_delta(pok, ("Barreira",), int(v)):
                    pok["Barreira"] = int(v)
                continue
            # atributos em geral
            key = _normalize_attr_key(k)
            if key in pok:
                try:
                    pok[key] = pok.get(key, 0) + int(v)
                except Exception:
                    pass
            else:
                # se não existir, não cria (mantém conservador)
                pass

    def _apply_damage_mutation_from_sublog(alvo_anim, alvo_sublog):
        """Aplica dano oficial ao alvo do sublog."""
        try:
            p = _poke_dict(alvo_anim)
            pid = int(p.get("ID"))
            side = int(_anim_side(alvo_anim))
            # usa Dano Final; se não houver, cai para Dano Enviado
            dano = int(alvo_sublog.get("Dano Final", alvo_sublog.get("Dano Enviado", 0)) or 0)
            if dano > 0:
                _mutate_official_by_id_side(pid, side, {"Vida": -dano})
        except Exception as e:
            print("[LEITOR][EXEC] Falha aplicando dano oficial:", e)

    def _apply_regs_mutations(regs, agente_anim):
        """Percorre Registros e aplica mutações no alvo indicado (ou no próprio agente, se faltou Alvo)."""
        if not regs:
            return
        # fallback: agente
        ag_id = None; ag_side = None
        if agente_anim is not None:
            try:
                ag_id = int(_poke_dict(agente_anim).get("ID"))
                ag_side = int(_anim_side(agente_anim))
            except Exception:
                ag_id = None; ag_side = None

        for r in regs:
            # destino
            alvo_txt = r.get("Alvo")
            if alvo_txt:
                try:
                    idx_s, pla_s = str(alvo_txt).replace(" ", "").split("/")
                    pid_t, side_t = int(idx_s), int(pla_s)
                except Exception:
                    try:
                        pid_t = int(str(alvo_txt).strip())
                        side_t = _find_side_by_id(pid_t)
                    except Exception:
                        pid_t, side_t = ag_id, ag_side
            else:
                pid_t, side_t = ag_id, ag_side

            if pid_t is None or side_t is None:
                continue

            # para cada chave mutável no registro
            for k, v in r.items():
                if k == "Alvo" or v in (None, 0, "0"):
                    continue
                if str(k).lower() == "cura":
                    _mutate_official_by_id_side(pid_t, side_t, {"Vida": int(v)})
                elif str(k).lower() == "barreira":
                    _mutate_official_by_id_side(pid_t, side_t, {"Barreira": int(v)})
                else:
                    # atributos: log vem minúsculo (ex.: "atk": -4) → dicionário usa maiúsculo (ex.: "Atk")
                    _mutate_official_by_id_side(pid_t, side_t, { _normalize_attr_key(k): int(v) })

    # passo executável
    def _start_step(step):
        actor = step.get("actor"); meth = step.get("method"); kwargs = step.get("kwargs", {})
        if actor is None or meth is None:
            return "SKIP"
        fn = getattr(actor, meth, None)
        if fn is None:
            return "SKIP"
        try:
            fn(**kwargs)
        except Exception as e:
            print(f"[LEITOR] Erro executando {meth}: {e}")
            return "SKIP"
        step["armed"] = True
        if step.get("wait", True):
            st["waiting_on"] = actor
            return "WAIT"
        return "GO"

    # ---------- plano por SLOT BRUTO ----------
    def _build_plan_for_slot(Log, slot_index, cache):
        agente    = cache["agente"]
        atkanima  = cache["atkanima"]
        anima_key = cache["anima_key"]

        slot_code_log  = str(cache["alvos_brutos"][slot_index]).strip().upper()
        slot_code_view = _code_from_log_to_view(slot_code_log, Log["Player"])
        pos_mira       = _slot_center(Log, slot_code_log)

        # DEBUG: listar animadores com pos normalizada + info do slot
        anim_pos_list = []
        for anim in todos_anim:
            p = _poke_dict(anim)
            name = p.get("Nome", "?")
            pid  = p.get("ID", "?")
            anim_pos_list.append(f"{name}#{pid}@{_pos_code_view_from_anim(anim)}")
        print(f"[LEITOR][HIT-DEBUG]   AnimPos: {', '.join(anim_pos_list)}")
        print(f"[LEITOR][HIT-DEBUG] LogSlot={slot_code_log} (LogPlayer={Log['Player']}) → ViewSlot={slot_code_view} @ {pos_mira}")

        # alvo real + SubLog desse slot (no view local)
        alvo_real   = _find_anim_by_slotcode_view(slot_code_view)
        alvo_sublog = cache["slot_to_sublog"].get(slot_code_view)

        if alvo_real is None:
            print(f"[LEITOR][HIT-DEBUG]   → SEM pokémon no ViewSlot {slot_code_view}.")
        else:
            p = _poke_dict(alvo_real)
            pid = p.get("ID", "?")
            side = _anim_side(alvo_real)
            print(f"[LEITOR][HIT-DEBUG]   → alvo_real: {p.get('Nome','?')}#{pid} side={side} "
                  f"has_sublog={bool(alvo_sublog)}")

        # frames/fps do golpe visual
        anim_code = atkanima.get(anima_key) if anima_key else None
        frames    = Ataques.get(anim_code) if anim_code else None
        fps       = Parametros_Ataque.get(anim_code, 24)

        # contato/projétil e velocidade (tempo de execução)
        contato = atkanima.get("Contato", "-")
        proj    = atkanima.get("Projetil", "-")
        if atkanima["Velocidade"] != "-":
            vel = float(atkanima.get("Velocidade", 0.5))
        else:
            vel = 0.1

        steps = []
        def add(actor, method, wait=True, **kwargs):
            steps.append({"actor": actor, "method": method, "kwargs": kwargs, "wait": wait, "armed": False})

        # 1) deslocamento do agente (CONTATO respeita semáforo)
        if contato == "A":
            add(agente, "iniciar_avanco", True,  alvo_pos=pos_mira, dur=vel, pct_continue=0.6)
            # marca ocupação do agente até fim da animação de contato
            try:
                st["_contact_until"][(int(cache["idx_ag"]), int(cache["pla_ag"]))] = time.time() + vel
            except Exception:
                pass
        elif contato == "I":
            add(agente, "iniciar_investida", True, alvo_pos=pos_mira, dur=vel, pct_continue=0.6)
            # marca ocupação do agente até fim da animação de contato
            try:
                st["_contact_until"][(int(cache["idx_ag"]), int(cache["pla_ag"]))] = time.time() + vel
            except Exception:
                pass
        else:
            # projétil/fluxo não entra no semáforo
            if proj == "fluxo":
                add(agente, "iniciar_disparo", True, alvo_pos=pos_mira, dur=vel, pct_continue=0.92)
            elif proj != "-":
                add(agente, "iniciar_disparo", True, alvo_pos=pos_mira,
                    proj_img=Projeteis.get(proj), dur=vel, pct_continue=0.92)

        # 2) golpe visual no centro do slot (não-bloqueante → ramifica)
        hit_kwargs = {"pos": pos_mira, "pct_continue": 0.90}
        if frames is not None: hit_kwargs["frames"] = frames
        if fps    is not None: hit_kwargs["fps"]    = fps
        add(agente, "iniciar_aplicar_golpe", False, **hit_kwargs)

        # 3) efeitos no alvo real (se houver SubLog)
        if alvo_real is not None and alvo_sublog is not None:
            Dano     = int(alvo_sublog.get("Dano Final", 0))
            crit     = bool(alvo_sublog.get("Critico", False))
            acertou  = bool(alvo_sublog.get("Acertou", True))
            TemDano  = Dano > 0
            Miss     = not acertou
            matou    = bool(alvo_sublog.get("Matou", False))

            fonte = Fontes[18]
            cor_dano = (255, 0, 0) if crit else (255, 255, 0)
            cor_miss = (255, 255, 255)

            print(f"[LEITOR][HIT-DEBUG]   → SubLog alvo: dano={Dano} crit={crit} acertou={acertou} matou={matou}")
            if TemDano:
                if not matou:
                    add(alvo_real, "iniciar_tomardano", False,
                        dur=max(0.2, Dano/50.0), freq=12.0, pct_continue=0.3)
                add(alvo_real, "iniciar_cartucho", False,
                    cartucho_surf=Cartuchu(valor=Dano, cor=cor_dano, fonte=fonte, crit=(2 if crit else 5)))
                print("[LEITOR][HIT-DEBUG]   → agendado tomar_dano/cartucho (dano).")
                # ---------------- EXECUTIVO: aplicar dano oficial ----------------
                _apply_damage_mutation_from_sublog(alvo_real, alvo_sublog)
            elif Miss:
                add(alvo_real, "iniciar_cartucho", False,
                    cartucho_surf=Cartuchu(valor="Miss", cor=cor_miss, fonte=fonte, crit=0))
                print("[LEITOR][HIT-DEBUG]   → agendado cartucho (Miss).")
                # Miss: não aplica mutação
            else:
                print("[LEITOR][HIT-DEBUG]   → sem dano/miss; nada a agendar.")

        return steps

    # registros (após todos os slots do Log)
    def _build_plan_registros(regs, agente):
        steps = []
        if not regs or agente is None:
            return steps
        fonte = Fontes[18]
        ups_total, downs_total = [], []
        turnos_pos_total, turnos_neg_total = 0, 0
        barreira_total = 0
        for r in regs:
            cura = int(r.get("Cura", 0) or 0)
            if cura > 0:
                dur = 0.2 + cura * 0.005
                steps.append({"actor": agente, "method": "iniciar_curar",
                              "kwargs": {"dur": dur, "freq": 12.0, "pct_continue": 0.40},
                              "wait": True, "armed": False})
                steps.append({"actor": agente, "method": "iniciar_cartucho",
                              "kwargs": {"cartucho_surf": Cartuchu(valor=cura, cor=(0,255,0), fonte=fonte, crit=0)} ,
                              "wait": False, "armed": False})
            barreira_total += int(r.get("Barreira", 0) or 0)
            for a in atributos:
                v = int(r.get(a, 0) or 0)
                if v > 0: ups_total.append((a, v))
                elif v < 0: downs_total.append((a, v))
            for e in efeitos_positivos:
                turnos_pos_total += int(r.get(e, 0) or 0)
            for e in efeitos_negativos:
                turnos_neg_total += int(r.get(e, 0) or 0)

        if barreira_total > 0 or ups_total or turnos_pos_total > 0:
            dur_b = 0.45 + len(ups_total)*0.12 + barreira_total*0.002 + turnos_pos_total*0.15
            steps.append({"actor": agente, "method": "iniciar_buff",
                          "kwargs": {"dur": dur_b, "qtd": 6, "area": (60, 40), "cor": (90,200,255),
                                     "pct_continue": 0.50, "debuff": False},
                          "wait": True, "armed": False})
            if barreira_total > 0:
                steps.append({"actor": agente, "method": "iniciar_cartucho",
                              "kwargs": {"cartucho_surf": Cartuchu(valor=barreira_total, cor=(0,0,255), fonte=fonte, crit=0)} ,
                              "wait": False, "armed": False})
            for (atr, v) in ups_total:
                steps.append({"actor": agente, "method": "iniciar_cartucho",
                              "kwargs": {"cartucho_surf": Cartuchu(
                                  valor=f"+{v} {atr}", cor=(255,190,210), fonte=fonte,
                                  icon=Icones.get(atr), crit=3)}})

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
                                  icon=Icones.get(atr), crit=3)}})

        # ---------------- EXECUTIVO: aplicar mutações oficiais dos Registros ----------------
        _apply_regs_mutations(regs, agente)

        return steps

    # ===================== MOTOR (não bloqueante) ======================
    budget = 16
    while budget > 0:
        budget -= 1

        if st["i"] >= len(LogRodada):
            parametros["Pronto"] = False
            parametros["Processando"] = False
            parametros["LogAtual"] = []
            parametros["LeitorState"] = {
                "i": 0, "j": 0, "step": 0, "plan": None, "waiting_on": None,
                "_cache": {}, "_contact_until": {}
            }
            return

        Log = LogRodada[st["i"]]
        alvos_brutos = Log.get("AlvosBruto") or []
        num_slots = len(alvos_brutos)

        # fim do Log atual?
        if st["j"] >= num_slots:
            if st.get("_doing_regs") is None:
                # usa agente do cache se existir; senão resolve pelo Log
                ag = st.get("_cache", {}).get("agente")
                if ag is None:
                    ag, _, _ = _resolve_agente(Log)
                regs_steps = _build_plan_registros(Log.get("Registros", []), ag)
                if regs_steps:
                    st["plan"] = regs_steps
                    st["step"] = 0
                    st["_doing_regs"] = True
                    continue
                else:
                    st["_doing_regs"] = False

            # cooldown de 0.75s entre logs
            st["i"] += 1
            st["j"] = 0
            st["step"] = 0
            st["plan"] = None
            st.pop("_doing_regs", None)
            st["_cache"].clear()
            st["_cooldown_until"] = time.time() + 0.8
            return

        # preparar cache do alvo bruto (1x)
        if not st["plan"]:
            # agente (via campo Agente do Log)
            try:
                idx_s, pla_s = str(Log["Agente"]).replace(" ", "").split("/")
                idx_ag, pla_ag = int(idx_s), int(pla_s)
            except Exception:
                idx_ag, pla_ag = None, None
            agente = None
            if idx_ag is not None:
                for anim in todos_anim:
                    p = _poke_dict(anim)
                    if int(p.get("ID", -999)) == idx_ag and _anim_side(anim) == pla_ag:
                        agente = anim
                        break

            # animações do golpe do agente
            atkanimadf = dfa[dfa["Nome"] == Log.get("Code Ataque")]
            if len(atkanimadf):
                atkanima = atkanimadf.iloc[0].to_dict()
                anima_key = "Animação"
            else:
                atkanima = {"Contato": "-", "Projetil": "fluxo", "Velocidade": 0.4}
                anima_key = None

            id_to_sublog, slot_to_sublog = _build_sublog_maps(Log)

            st["_cache"] = {
                "agente": agente,
                "idx_ag": idx_ag, "pla_ag": pla_ag,
                "atkanima": atkanima, "anima_key": anima_key,
                "alvos_brutos": alvos_brutos,
                "id_to_sublog": id_to_sublog,
                "slot_to_sublog": slot_to_sublog,
            }

            # checagem de semáforo ANTES de montar o plano do alvo atual (para CONTATO)
            contato_preview = atkanima.get("Contato", "-")
            if atkanima.get("Velocidade", "-") != "-":
                try:
                    vel_preview = float(atkanima.get("Velocidade", 0.5))
                except Exception:
                    vel_preview = 0.5
            else:
                vel_preview = 0.1

            if contato_preview in ("A", "I") and (idx_ag is not None and pla_ag is not None):
                key = (int(idx_ag), int(pla_ag))
                busy_until = st["_contact_until"].get(key, 0.0)
                now = time.time()
                if now < busy_until:
                    st["_cooldown_until"] = busy_until
                    return

            st["plan"] = _build_plan_for_slot(Log, st["j"], st["_cache"])
            st["step"] = 0

            if not st["plan"]:
                st["j"] += 1
                st["plan"] = None
                continue

        # executar/avançar um step
        plan = st["plan"]
        k = st["step"]

        if k >= len(plan):
            st["j"] += 1
            st["step"] = 0
            st["plan"] = None
            st["waiting_on"] = None
            continue

        step = plan[k]

        if not step["armed"]:
            res = _start_step(step)
            if res == "WAIT":
                return
            elif res == "SKIP":
                st["step"] += 1
                continue
            st["step"] += 1
            continue

        if step.get("wait", True):
            actor = step["actor"]
            cont = getattr(actor, "Continue", None)
            if cont is None:
                st["waiting_on"] = None
                st["step"] += 1
                continue
            if not cont:
                st["waiting_on"] = actor
                return
            st["waiting_on"] = None
            st["step"] += 1
            continue
        else:
            st["step"] += 1
            continue
