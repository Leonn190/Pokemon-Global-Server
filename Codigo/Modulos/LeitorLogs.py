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

def LeitorLogs(LogRodada, parametros, _anim_aliados, _anim_inimigos, Ataques, Projeteis, Icones, nome_arquivo="LogRodada.json"):
    # Abre o arquivo em modo escrita e salva o log em formato JSON
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(LogRodada, f, ensure_ascii=False, indent=4)
    print(f"✅ Log da rodada salvo em '{nome_arquivo}'")

    animaliados = []
    for anima, _ in _anim_aliados:
        animaliados.append(anima)
    
    animainimigos = []
    for anima, _ in _anim_inimigos:
        animainimigos.append(anima)
    
    _anim_aliados = animaliados
    _anim_inimigos = animainimigos

    for Log in LogRodada:

        ag_str = Log["Agente"].replace(" ", "")
        idx_s, pla_s = ag_str.split("/")
        idx = int(idx_s)
        pla = int(pla_s)
        if pla == parametros["Player"]:
            agenteLOG = _anim_aliados[idx]
        else:
            agenteLOG = _anim_inimigos[idx]

        atkanimadf = dfa[dfa["Nome"] == Log["Code Ataque"]]
        atkanima = atkanimadf.iloc[0].to_dict()

        if atkanima["Alvo"] == "U":
            pass

        for SubLog in Log["SubLogs"]:

            ag_str = Log["Agente"].replace(" ", "")
            idx_s, pla_s = ag_str.split("/")
            idx = int(idx_s)
            pla = int(pla_s)
            if pla == parametros["Player"]:
                Alvo = _anim_aliados[idx]
                anima = "Animação"
            else:
                Alvo = _anim_inimigos[idx]
                anima = "AnimaçãoAliado"
            
            if SubLog["Dano Final"] > 0:
                TemDano = True
                Miss = False
                Dano = SubLog["Dano Final"]
                if SubLog["Critico"]:
                    cor = (255, 0, 0)
                else:
                    cor = (255, 255, 0)
            elif SubLog["Acertou"]:
                TemDano = False
                Miss = False
                cor = (255, 255, 255)
            else:
                TemDano = False
                Miss = True
                cor = (255, 255, 255)
            
            from Codigo.Cenas.Batalha import Fontes
            fonte = Fontes[18]
            
            if atkanima["Contato"] == "A":
                if TemDano:
                    agenteLOG.iniciar_avanco(
                        alvo_pos=Alvo.pos,
                        dur=float(atkanima["Velocidade"]),
                        gatilho_pct=0.5,
                        on_gatilho=(
                            lambda a=Alvo, anim=atkanima, anima_key=anima, Ataques_=Ataques, Params=Parametros_Ataque,
                                dano=Dano, cor_=cor, fonte_=fonte, sub=SubLog: a.iniciar_sofrergolpe(
                                frames=Ataques_[anim[anima_key]],
                                fps=Params[anim[anima_key]],
                                gatilho_pct=0.85,
                                on_gatilho=(
                                    lambda a2=a, d=dano, c=cor_, f=fonte_, sub2=sub: a2.iniciar_tomardano(
                                        dur=d/100,
                                        gatilho_pct=0.25,
                                        on_gatilho=(lambda a3=a2, d2=d, c2=c, f2=f, sub3=sub2: a3.iniciar_cartucho(
                                            cartucho_surf=Cartuchu(
                                                valor=d2,
                                                cor=c2,
                                                fonte=f2,
                                                crit=(2 if sub3["Critico"] else 5)
                                            )
                                        ))
                                    )
                                )
                            )
                        )
                    )
                elif Miss:
                    agenteLOG.iniciar_avanco(
                        alvo_pos=Alvo.pos,
                        dur=float(atkanima["Velocidade"]),
                        gatilho_pct=0.5,
                        on_gatilho=(lambda a=Alvo, c=cor, f=fonte: a.iniciar_cartucho(
                            cartucho_surf=Cartuchu(
                                valor="Miss",
                                cor=c,
                                fonte=f,
                                crit=0
                            )
                        ))
                    )
                else:
                    agenteLOG.iniciar_avanco(
                        alvo_pos=Alvo.pos,
                        dur=float(atkanima["Velocidade"]),
                        gatilho_pct=0.5,
                        on_gatilho=(lambda a=Alvo, anim=atkanima, anima_key=anima, Ataques_=Ataques, Params=Parametros_Ataque: a.iniciar_sofrergolpe(
                            frames=Ataques_[anim[anima_key]],
                            fps=Params[anim[anima_key]]
                        ))
                    )

            elif atkanima["Contato"] == "I":
                if TemDano:
                    agenteLOG.iniciar_investida(
                        alvo_pos=Alvo.pos,
                        dur=float(atkanima["Velocidade"]),
                        gatilho_pct=0.5,
                        on_gatilho=(lambda a=Alvo, anim=atkanima, anima_key=anima, Ataques_=Ataques, Params=Parametros_Ataque,
                                        dano=Dano, cor_=cor, fonte_=fonte, sub=SubLog: a.iniciar_sofrergolpe(
                            frames=Ataques_[anim[anima_key]],
                            fps=Params[anim[anima_key]],
                            gatilho_pct=0.85,
                            on_gatilho=(lambda a2=a, d=dano, c=cor_, f=fonte_, sub2=sub: a2.iniciar_tomardano(
                                dur=d/100,
                                gatilho_pct=0.25,
                                on_gatilho=(lambda a3=a2, d2=d, c2=c, f2=f, sub3=sub2: a3.iniciar_cartucho(
                                    cartucho_surf=Cartuchu(
                                        valor=d2,
                                        cor=c2,
                                        fonte=f2,
                                        crit=(2 if sub3["Critico"] else 5)
                                    )
                                ))
                            ))
                        ))
                    )
                elif Miss:
                    agenteLOG.iniciar_investida(
                        alvo_pos=Alvo.pos,
                        dur=float(atkanima["Velocidade"]),
                        gatilho_pct=0.5,
                        on_gatilho=(lambda a=Alvo, c=cor, f=fonte: a.iniciar_cartucho(
                            cartucho_surf=Cartuchu(
                                valor="Miss",
                                cor=c,
                                fonte=f,
                                crit=0
                            )
                        ))
                    )
                else:
                    agenteLOG.iniciar_investida(
                        alvo_pos=Alvo.pos,
                        dur=float(atkanima["Velocidade"]),
                        gatilho_pct=0.5,
                        on_gatilho=(lambda a=Alvo, anim=atkanima, anima_key=anima, Ataques_=Ataques, Params=Parametros_Ataque: a.iniciar_sofrergolpe(
                            frames=Ataques_[anim[anima_key]],
                            fps=Params[anim[anima_key]]
                        ))
                    )

            else:
                if atkanima["Projetil"] == "fluxo":
                    if TemDano:
                        agenteLOG.iniciar_disparo(
                            alvo_pos=Alvo.pos,
                            dur=float(atkanima["Velocidade"]),
                            gatilho_pct=0.9,
                            on_gatilho=(lambda a=Alvo, anim=atkanima, anima_key=anima, Ataques_=Ataques, Params=Parametros_Ataque,
                                            dano=Dano, cor_=cor, fonte_=fonte, sub=SubLog: a.iniciar_sofrergolpe(
                                frames=Ataques_[anim[anima_key]],
                                fps=Params[anim[anima_key]],
                                gatilho_pct=0.85,
                                on_gatilho=(lambda a2=a, d=dano, c=cor_, f=fonte_, sub2=sub: a2.iniciar_tomardano(
                                    dur=d/100,
                                    gatilho_pct=0.25,
                                    on_gatilho=(lambda a3=a2, d2=d, c2=c, f2=f, sub3=sub2: a3.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor=d2,
                                            cor=c2,
                                            fonte=f2,
                                            crit=(2 if sub3["Critico"] else 5)
                                        )
                                    ))
                                ))
                            ))
                        )
                    elif Miss:
                        agenteLOG.iniciar_disparo(
                            alvo_pos=Alvo.pos,
                            dur=float(atkanima["Velocidade"]),
                            gatilho_pct=0.9,
                            on_gatilho=(lambda a=Alvo, c=cor, f=fonte: a.iniciar_cartucho(
                                cartucho_surf=Cartuchu(
                                    valor="Miss",
                                    cor=c,
                                    fonte=f,
                                    crit=0
                                )
                            ))
                        )
                    else:
                        agenteLOG.iniciar_disparo(
                            alvo_pos=Alvo.pos,
                            dur=float(atkanima["Velocidade"]),
                            gatilho_pct=0.9,
                            on_gatilho=(lambda a=Alvo, anim=atkanima, anima_key=anima, Ataques_=Ataques, Params=Parametros_Ataque: a.iniciar_sofrergolpe(
                                frames=Ataques_[anim[anima_key]],
                                fps=Params[anim[anima_key]]
                            ))
                        )

                elif atkanima["Projetil"] == "-":
                    if TemDano:
                        Alvo.iniciar_sofrergolpe(
                            frames=Ataques[atkanima[anima]],
                            fps=Parametros_Ataque[atkanima[anima]],
                            gatilho_pct=0.85,
                            on_gatilho=(lambda a=Alvo, d=Dano, c=cor, f=fonte, sub=SubLog: a.iniciar_tomardano(
                                dur=d/100,
                                gatilho_pct=0.25,
                                on_gatilho=(lambda a2=a, d2=d, c2=c, f2=f, sub2=sub: a2.iniciar_cartucho(
                                    cartucho_surf=Cartuchu(
                                        valor=d2,
                                        cor=c2,
                                        fonte=f2,
                                        crit=(2 if sub2["Critico"] else 5)
                                    )
                                ))
                            ))
                        )
                    elif Miss:
                        Alvo.iniciar_cartucho(
                            cartucho_surf=Cartuchu(
                                valor="Miss",
                                cor=cor,
                                fonte=fonte,
                                crit=0
                            )
                        )
                    else:
                        Alvo.iniciar_sofrergolpe(
                            frames=Ataques[atkanima[anima]],
                            fps=Parametros_Ataque[atkanima[anima]]
                        )
                else:
                    if TemDano:
                        agenteLOG.iniciar_disparo(
                            alvo_pos=Alvo.pos,
                            proj_img=Projeteis[atkanima["Projetil"]],
                            dur=float(atkanima["Velocidade"]),
                            gatilho_pct=0.9,
                            on_gatilho=(lambda a=Alvo, anim=atkanima, anima_key=anima, Ataques_=Ataques, Params=Parametros_Ataque,
                                            dano=Dano, cor_=cor, fonte_=fonte, sub=SubLog: a.iniciar_sofrergolpe(
                                frames=Ataques_[anim[anima_key]],
                                fps=Params[anim[anima_key]],
                                gatilho_pct=0.85,
                                on_gatilho=(lambda a2=a, d=dano, c=cor_, f=fonte_, sub2=sub: a2.iniciar_tomardano(
                                    dur=d/100,
                                    gatilho_pct=0.25,
                                    on_gatilho=(lambda a3=a2, d2=d, c2=c, f2=f, sub3=sub2: a3.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor=d2,
                                            cor=c2,
                                            fonte=f2,
                                            crit=(2 if sub3["Critico"] else 5)
                                        )
                                    ))
                                ))
                            ))
                        )
                    elif Miss:
                        agenteLOG.iniciar_disparo(
                            alvo_pos=Alvo.pos,
                            proj_img=Projeteis[atkanima["Projetil"]],
                            dur=float(atkanima["Velocidade"]),
                            gatilho_pct=0.9,
                            on_gatilho=(lambda a=Alvo, c=cor, f=fonte: a.iniciar_cartucho(
                                cartucho_surf=Cartuchu(
                                    valor="Miss",
                                    cor=c,
                                    fonte=f,
                                    crit=0
                                )
                            ))
                        )
                    else:
                        agenteLOG.iniciar_disparo(
                            alvo_pos=Alvo.pos,
                            proj_img=Projeteis[atkanima["Projetil"]],
                            dur=float(atkanima["Velocidade"]),
                            gatilho_pct=0.9,
                            on_gatilho=(lambda a=Alvo, anim=atkanima, anima_key=anima, Ataques_=Ataques, Params=Parametros_Ataque: a.iniciar_sofrergolpe(
                                frames=Ataques_[anim[anima_key]],
                                fps=Params[anim[anima_key]]
                            ))
                        )

            while any(_anima_.acao_em_andamento() for _anima_ in _anim_aliados + _anim_inimigos):
                pass

            if "Registros" in SubLog:
                for registro in SubLog["Registros"]:
                    ag_str = Log["Agente"].replace(" ", "")
                    idx_s, pla_s = ag_str.split("/")
                    idx, pla = int(idx_s), int(pla_s)
                    agente = _anim_aliados[idx] if pla == parametros["Player"] else _anim_inimigos[idx]

                    # --- valores brutos do registro ---
                    qtd_cura     = registro.get("Cura", 0)
                    qtd_barreira = registro.get("Barreira", 0)

                    ups   = [(a, registro[a]) for a in atributos if a in registro and registro[a] > 0]
                    downs = [(a, registro[a]) for a in atributos if a in registro and registro[a] < 0]

                    turnos_pos = sum(registro[e] for e in efeitos_positivos if e in registro)
                    turnos_neg = sum(registro[e] for e in efeitos_negativos if e in registro)

                    # --- AÇÕES (cura, buff, debuff) ---
                    acoes = []

                    if qtd_cura > 0:
                        dur = 0.2 + qtd_cura * 0.005
                        acoes.append(lambda on_done=None, a=agente, d=dur, val=qtd_cura:
                            a.iniciar_curar(
                                dur=d,
                                on_gatilho=lambda a2=a, v=val: a2.iniciar_cartucho(
                                    cartucho_surf=Cartuchu(valor=v, cor=(0,255,0), fonte=fonte, crit=0),
                                    on_gatilho=(lambda: on_done() if on_done else None)
                                )
                            )
                        )

                    if qtd_barreira > 0 or ups or turnos_pos > 0:
                        dur = 0.4 + len(ups)*0.18 + qtd_barreira*0.002 + turnos_pos*0.15
                        acoes.append(lambda on_done=None, a=agente, d=dur, ups=ups, qb=qtd_barreira:
                            a.iniciar_buff(
                                dur=d, debuff=False,
                                on_gatilho=lambda a2=a: (
                                    a2.iniciar_cartucho(cartucho_surf=Cartuchu(valor=qb, cor=(0,0,255), fonte=fonte, crit=0)) if qb>0 else None,
                                    [a2.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor=f"+{v} {atr}",
                                            cor=(255,190,210),  # rosa claro
                                            fonte=fonte,
                                            icon=Icones[atr],
                                            crit=3
                                        )
                                    ) for atr,v in ups],
                                    on_done() if on_done else None
                                )
                            )
                        )

                    if downs or turnos_neg > 0:
                        dur = 0.4 + len(downs)*0.18 + turnos_neg*0.15
                        acoes.append(lambda on_done=None, a=agente, d=dur, downs=downs:
                            a.iniciar_buff(
                                dur=d, debuff=True,
                                on_gatilho=lambda a2=a: (
                                    [a2.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor=f"{v} {atr}",
                                            cor=(255,190,210),
                                            fonte=fonte,
                                            icon=Icones[atr],
                                            crit=3
                                        )
                                    ) for atr,v in downs],
                                    on_done() if on_done else None
                                )
                            )
                        )

                    # --- Encadeia tudo (cura -> buff -> debuff) ---
                    def encadear(lista):
                        on_done = None
                        for st in reversed(lista):
                            prev = on_done
                            on_done = (lambda st_=st, cb=prev: (lambda: st_(cb)))
                        if on_done: on_done()

                    encadear(acoes)

    parametros["Pronto"] = False
    parametros["LogAtual"] = []
