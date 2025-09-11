import json
import pandas as pd

dfa = pd.read_csv("Dados/Animações.csv")

from Codigo.Prefabs.FunçõesPrefabs import Cartuchu

Parametros_Ataque = {
    "LabaredaMultipla": {"fps": 31.25},
    "Corte": {"fps": 10.2},
    "BolhasVerdes": {"fps": 20},
    "CorteDourado": {"fps": 10.87},
    "ChuvaVermelha": {"fps": 31.25},
    "ChuvaBrilhante": {"fps": 33.33},
    "Agua": {"fps": 23.81},
    "AtemporalRosa": {"fps": 40},
    "BarreiraCelular": {"fps": 12.5},
    "ChicoteMultiplo": {"fps": 13.89},
    "CorteDuploRoxo": {"fps": 33.33},
    "CorteMagico": {"fps": 25},
    "CorteRicocheteadoRoxo": {"fps": 8.93},
    "CorteRosa": {"fps": 25},
    "DomoVerde": {"fps": 11.76},
    "EnergiaAzul": {"fps": 15.38},
    "Engrenagem": {"fps": 8.7},
    "EspiralAzul": {"fps": 22.22},
    "Estouro": {"fps": 10.31},
    "EstouroMagico": {"fps": 20},
    "EstouroVermelho": {"fps": 21.74},
    "Explosao": {"fps": 22.22},
    "ExplosaoPedra": {"fps": 10.87},
    "ExplosaoVerde": {"fps": 8.93},
    "ExplosaoVermelha": {"fps": 33.33},
    "ExplosaoRoxa": {"fps": 9.52},
    "FacasAzuis": {"fps": 35.71},
    "FacasBrancas": {"fps": 26.32},
    "FacasColoridas": {"fps": 31.25},
    "FacasRosas": {"fps": 40},
    "FeixeMagenta": {"fps": 23.81},
    "FeixeRoxo": {"fps": 10.42},
    "FluxoAzul": {"fps": 15.38},
    "Fogo": {"fps": 10.53},
    "Fumaça": {"fps": 28.57},
    "GasRoxo": {"fps": 12.82},
    "Garra": {"fps": 12.5},
    "HexagonoLaminas": {"fps": 27.78},
    "ImpactoRochoso": {"fps": 8.7},
    "Karate": {"fps": 11.11},
    "LuaAmarela": {"fps": 55.56},
    "MagiaAzul": {"fps": 38.46},
    "MagiaMagenta": {"fps": 20.83},
    "MarcaBrilhosa": {"fps": 26.32},
    "MarcaAmarela": {"fps": 19.23},
    "MarcaAzul": {"fps": 26.32},
    "Mordida": {"fps": 8.7},
    "MultiplasFacas": {"fps": 27.78},
    "OrbesRoxos": {"fps": 35.71},
    "PedaçoColorido": {"fps": 26.32},
    "RaioAzul": {"fps": 83.33},
    "RajadaAmarela": {"fps": 28.57},
    "RasgoMagenta": {"fps": 38.46},
    "RasgosRosa": {"fps": 35.71},
    "RedemoinhoAzul": {"fps": 26.32},
    "RedemoinhoCosmico": {"fps": 10.53},
    "SuperDescarga": {"fps": 12.2},
    "SuperNova": {"fps": 31.25},
    "TirosAmarelos": {"fps": 40},
    "TornadoAgua": {"fps": 25.64}}

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

def LeitorLogs(LogRodada, parametros, _anim_aliados, _anim_inimigos, Ataques, Projeteis, nome_arquivo="LogRodada.json"):
    # Abre o arquivo em modo escrita e salva o log em formato JSON
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(LogRodada, f, ensure_ascii=False, indent=4)
    print(f"✅ Log da rodada salvo em '{nome_arquivo}'") 

    for Log in LogRodada:

        Log["Agente"].strip("/")
        idx, pla = Log["Agente"]
        if pla == parametros["Player"]:
            agenteLOG = _anim_aliados[idx]
        else:
            agenteLOG = _anim_inimigos[idx]

        atkanimadf = dfa[dfa["Nome"] == Log["Code Ataque"]]
        atkanima = atkanimadf.iloc[0].to_dict()

        if atkanima["Alvo"] == "U":
            pass

        for SubLog in Log["SubLogs"]:

            SubLog["Alvo"].strip("/")
            idx, pla = SubLog["Alvo"]
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
            else:
                TemDano = False
                Miss = True
            
            from Codigo.Cenas.Batalha import Fontes
            fonte = Fontes[18]
            
            if atkanima["Contato"] == "A":
                if TemDano:
                    agenteLOG.iniciar_avanco(
                        alvo_pos= Alvo.pos,
                        dur=atkanima["Velocidade"],
                        gatilho_pct=0.5,
                        on_gatilho=Alvo.iniciar_sofrergolpe(
                            frames=Ataques[atkanima[anima]],
                            fps=Parametros_Ataque[atkanima[anima]],
                            gatilho_pct=0.85,
                            on_gatilho=Alvo.iniciar_tomardano(
                                dur=Dano / 100,
                                gatilho_pct=0.25,
                                on_gatilho=Alvo.iniciar_cartucho(
                                    cartucho_surf=Cartuchu(
                                        valor=Dano,
                                        cor=cor,
                                        fonte=fonte,
                                        crit= 2 if SubLog["Critico"] else 5
                                    )
                                )
                            )
                        )
                    )
                elif Miss:
                    agenteLOG.iniciar_avanco(
                        alvo_pos= Alvo.pos,
                        dur=atkanima["Velocidade"],
                        gatilho_pct=0.5,
                        on_gatilho=Alvo.iniciar_cartucho(
                                    cartucho_surf=Cartuchu(
                                        valor="Miss",
                                        cor=cor,
                                        fonte=fonte,
                                        crit= 0
                                    )
                                )
                            )
                else:
                    agenteLOG.iniciar_avanco(
                        alvo_pos= Alvo.pos,
                        dur=atkanima["Velocidade"],
                        gatilho_pct=0.5,
                        on_gatilho=Alvo.iniciar_sofrergolpe(
                            frames=Ataques[atkanima[anima]],
                            fps=Parametros_Ataque[atkanima[anima]]
                            )
                        )

            elif atkanima["Contato"] == "I":
                if TemDano:
                    agenteLOG.iniciar_investida(
                        alvo_pos= Alvo.pos,
                        dur=atkanima["Velocidade"],
                        gatilho_pct=0.5,
                        on_gatilho=Alvo.iniciar_sofrergolpe(
                            frames=Ataques[atkanima[anima]],
                            fps=Parametros_Ataque[atkanima[anima]],
                            gatilho_pct=0.85,
                            on_gatilho=Alvo.iniciar_tomardano(
                                dur=Dano / 100,
                                gatilho_pct=0.25,
                                on_gatilho=Alvo.iniciar_cartucho(
                                    cartucho_surf=Cartuchu(
                                        valor=Dano,
                                        cor=cor,
                                        fonte=fonte,
                                        crit= 2 if SubLog["Critico"] else 5
                                    )
                                )
                            )
                        )
                    )
                elif Miss:
                    agenteLOG.iniciar_investida(
                        alvo_pos= Alvo.pos,
                        dur=atkanima["Velocidade"],
                        gatilho_pct=0.5,
                        on_gatilho=Alvo.iniciar_cartucho(
                                    cartucho_surf=Cartuchu(
                                        valor="Miss",
                                        cor=cor,
                                        fonte=fonte,
                                        crit= 0
                                    )
                                )
                            )
                else:
                    agenteLOG.iniciar_investida(
                        alvo_pos= Alvo.pos,
                        dur=atkanima["Velocidade"],
                        gatilho_pct=0.5,
                        on_gatilho=Alvo.iniciar_sofrergolpe(
                            frames=Ataques[atkanima[anima]],
                            fps=Parametros_Ataque[atkanima[anima]]
                            )
                        )

            else:
                if atkanima["Projetil"] == "fluxo":
                    if TemDano:
                        agenteLOG.iniciar_disparo(
                            alvo_pos= Alvo.pos,
                            dur=atkanima["Velocidade"],
                            gatilho_pct=0.9,
                            on_gatilho=Alvo.iniciar_sofrergolpe(
                                frames=Ataques[atkanima[anima]],
                                fps=Parametros_Ataque[atkanima[anima]],
                                gatilho_pct=0.85,
                                on_gatilho=Alvo.iniciar_tomardano(
                                    dur=Dano / 100,
                                    gatilho_pct=0.25,
                                    on_gatilho=Alvo.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor=Dano,
                                            cor=cor,
                                            fonte=fonte,
                                            crit= 2 if SubLog["Critico"] else 5
                                        )
                                    )
                                )
                            )
                        )
                    elif Miss:
                        agenteLOG.iniciar_disparo(
                            alvo_pos= Alvo.pos,
                            dur=atkanima["Velocidade"],
                            gatilho_pct=0.9,
                            on_gatilho=Alvo.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor="Miss",
                                            cor=cor,
                                            fonte=fonte,
                                            crit= 0
                                        )
                                    )
                                )
                    else:
                        agenteLOG.iniciar_disparo(
                            alvo_pos= Alvo.pos,
                            dur=atkanima["Velocidade"],
                            gatilho_pct=0.9,
                            on_gatilho=Alvo.iniciar_sofrergolpe(
                                frames=Ataques[atkanima[anima]],
                                fps=Parametros_Ataque[atkanima[anima]]
                                )
                            )

                elif atkanima["Projetil"] == "-":
                    if TemDano:
                        Alvo.iniciar_sofrergolpe(
                                frames=Ataques[atkanima[anima]],
                                fps=Parametros_Ataque[atkanima[anima]],
                                gatilho_pct=0.85,
                                on_gatilho=Alvo.iniciar_tomardano(
                                    dur=Dano / 100,
                                    gatilho_pct=0.25,
                                    on_gatilho=Alvo.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor=Dano,
                                            cor=cor,
                                            fonte=fonte,
                                            crit= 2 if SubLog["Critico"] else 5
                                        )
                                    )
                                )
                            )
                    elif Miss:
                        Alvo.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor="Miss",
                                            cor=cor,
                                            fonte=fonte,
                                            crit= 0
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
                            alvo_pos= Alvo.pos,
                            proj_img= Projeteis[atkanima["Projetil"]],
                            dur=atkanima["Velocidade"],
                            gatilho_pct=0.9,
                            on_gatilho=Alvo.iniciar_sofrergolpe(
                                frames=Ataques[atkanima[anima]],
                                fps=Parametros_Ataque[atkanima[anima]],
                                gatilho_pct=0.85,
                                on_gatilho=Alvo.iniciar_tomardano(
                                    dur=Dano / 100,
                                    gatilho_pct=0.25,
                                    on_gatilho=Alvo.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor=Dano,
                                            cor=cor,
                                            fonte=fonte,
                                            crit= 2 if SubLog["Critico"] else 5
                                        )
                                    )
                                )
                            )
                        )
                    elif Miss:
                        agenteLOG.iniciar_disparo(
                            alvo_pos= Alvo.pos,
                            proj_img= Projeteis[atkanima["Projetil"]],
                            dur=atkanima["Velocidade"],
                            gatilho_pct=0.9,
                            on_gatilho=Alvo.iniciar_cartucho(
                                        cartucho_surf=Cartuchu(
                                            valor="Miss",
                                            cor=cor,
                                            fonte=fonte,
                                            crit= 0
                                        )
                                    )
                                )
                    else:
                        agenteLOG.iniciar_disparo(
                            alvo_pos= Alvo.pos,
                            proj_img= Projeteis[atkanima["Projetil"]],
                            dur=atkanima["Velocidade"],
                            gatilho_pct=0.9,
                            on_gatilho=Alvo.iniciar_sofrergolpe(
                                frames=Ataques[atkanima[anima]],
                                fps=Parametros_Ataque[atkanima[anima]]
                                )
                            )

            if "Registros" in SubLog:
                for registro in SubLog["Registros"]:
                    registro["Alvo"].strip("/")
                    idx, pla = registro["Alvo"]
                    if pla == parametros["Player"]:
                        agente = _anim_aliados[idx]
                    else:
                        agente = _anim_inimigos[idx]

                    fallbacks = []
                    
                    if "Cura" in registro:
                        fallbacks.append(agente.iniciar_curar())
                    
                    if "Barreira" in registro:
                        fallbacks.append(agente.iniciar_buff())
                    
                    statUP = []
                    statDOWN = []

                    for atributo in atributos:
                        if atributo in registro:
                            if registro[atributo] > 0:
                                statUP.append((atributo,registro[atributo]))
                            else:
                                statDOWN.append((atributo,registro[atributo]))
                    
                    if statUP is not []:
                        fallbacks.append(agente.iniciar_buff())
                    if statDOWN is not []:
                        fallbacks.append(agente.iniciar_buff())
                    
                    efectPOS = []
                    efectNEG = []

                    for efeito in efeitos_positivos:
                        if efeito in registro:
                            efectPOS.append((efeito,registro[efeito]))
                    for efeito in efeitos_negativos:
                        if efeito in registro:
                            efectNEG.append((efeito,registro[efeito]))
                    
                    if efectPOS is not []:
                        fallbacks.append(agente.iniciar_buff())
                    if efectNEG is not []:
                        fallbacks.append(agente.iniciar_buff())

    parametros["Pronto"] = False
    parametros["LogAtual"] = []
