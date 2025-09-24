AtkDic = {}

# 1 — Enraivecer (s): Se vida < 50%, ganha Aprimorado (se SpA > Atk) senão ganha Amplificado.
def Enraivecer_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):

    # Se Vida abaixo de 50%:
    #     - Ganha Aprimorado se SpA > Atk
    #     - Caso contrário, ganha Amplificado

    if Atacante.vida < Atacante.base_vida * 0.5:
        if Atacante.spA > Atacante.atk:
            Atacante.AplicarEfeito("Aprimorado", Atacante, Log)
        else:
            Atacante.AplicarEfeito("Amplificado", Atacante, Log)

# 2 — Recarga (f): Recupera 200% do custo de energia e aumenta SpA em 5%.
def Recarga_f(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, dano_final):

    # Recupera 200% do custo de energia e aumenta SpA em 5%

    custo = ataque["Custo"]
    energia_recuperada = int(custo * 2)
    Atacante.Energia = min(Atacante.ene, Atacante.Energia + energia_recuperada)

    aumento = int(Atacante.base_spA * 0.05)
    Atacante.ModificarStatus("spA", aumento, Log)

    if Log is not None:
        if "Curas" not in Log:
            Log["Curas"] = []
        Log["Curas"].append({
            "Alvo": Atacante.ID,
            "Energia": energia_recuperada
        })
    return dano_final

# 3 — Provocar (s): Aplica Provocar no alvo ao acertar.
def Provocar_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):

    # Aplica Provocar no alvo

    if Acertou:
        Atacante.AplicarEfeito("Provocando", Alvo, Log)

# 4 — Rosnar (s): Reduz o Atk do inimigo em 15% ao acertar.
def Rosnar_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):

    # Reduz Atk do inimigo em 15%

    if Acertou:
        reducao = int(Alvo.base_atk * 0.15)
        Alvo.ModificarStatus("atk", -reducao, Log)

# 5 — biscoito (s): Atacante e 1 aliado adjacente ganham 1 Biscoito; cada Biscoito cura 4% da própria Mag.
def biscoito_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):
    # Esse Pokémon e o aliado mais próximo ganham 1 Biscoito (atributo próprio).
    # Para cada Biscoito no alvo, cura 4% da própria Mag imediatamente.

    def _aliados_do_atacante():
        # decide o lado do atacante
        if Atacante in Partida.pokemons_jogador1:
            return Partida.pokemons_jogador1
        return Partida.pokemons_jogador2

    def _aliado_mais_proximo():
        aliados = [p for p in _aliados_do_atacante() if p.vivo and p is not Atacante]
        if not aliados:
            return None
        # tenta usar adjacentes() se existir
        try:
            from Codigo.Localidades.ControleBatalha import adjacentes  # caminho conforme seu projeto; ajuste se necessário
        except Exception:
            # fallback: escolhe o primeiro aliado ativo mais “próximo” por posição
            try:
                base = int(Atacante.local) if Atacante.local is not None else 5
                aliados.sort(key=lambda x: abs(int(x.local) - base) if x.local is not None else 99)
                return aliados[0] if aliados else None
            except Exception:
                return aliados[0] if aliados else None
        else:
            try:
                adjs = adjacentes(Atacante, aliados)
                if adjs:
                    return adjs[0]
                # se não houver adjacente, cai num fallback leve
                return aliados[0]
            except Exception:
                return aliados[0] if aliados else None

    # monta lista de afetados: atacante e 1 aliado
    afetados = [Atacante]
    aliado = _aliado_mais_proximo()
    if aliado:
        afetados.append(aliado)

    for poke in afetados:
        # garante atributo Biscoitos com try/except
        try:
            poke.Biscoitos += 1
        except Exception:
            try:
                poke.Biscoitos = 1
            except Exception:
                # se até set falhar, aborta só para esse alvo
                continue

        # cura 4% * Mag * (total de biscoitos)
        try:
            total = int(poke.Biscoitos)
            cura = int(poke.mag * 0.04 * total)
        except Exception:
            # fallback seguro
            cura = int(getattr(poke, "mag", 0) * 0.04)

        # registra no log e aplica a cura
        poke.ReceberCura(cura, Log)

# 8 — tapa_magico (m): Modifica cálculo do dano usando MAG como poder de ataque.
def tapa_magico_m(Atacante, Alvo, AlvosAliados, ataque, Partida,
                  poder_ataque, defesa_alvo, dano_base,
                  critico, bonus_critico, Acertou, Protegido):
    # Modifica a forma de calcular o dano → usa MAG como poder de ataque
    poder_ataque = Atacante.mag
    return poder_ataque, defesa_alvo, critico, bonus_critico, Acertou, Protegido

# 9 — resetar (s): Zera todas as variações de atributos do atacante (permanentes e temporárias), exceto efeitos.
def resetar_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):
    # Zera TODAS as variações de atributos (permanentes e temporárias), exceto efeitos
    for stat in ["atk","def","spA","spD","vel","mag","per","ene","enR","crD","crC","vamp","asse"]:
        setattr(Atacante, f"var_per_{stat}", 0)
        setattr(Atacante, f"var_temp_{stat}", 0)

    return

# 10 — golpe_critico (m): Este ataque é sempre crítico.
def golpe_critico_m(Atacante, Alvo, AlvosAliados, ataque, Partida,
                    poder_ataque, defesa_alvo, dano_base,
                    critico, bonus_critico, Acertou, Protegido):
    # Esse ataque é SEMPRE crítico
    critico = True
    return poder_ataque, defesa_alvo, critico, bonus_critico, Acertou, Protegido

# 12 — Estocada (m): +30% de dano se o atacante for o Pokémon ativo com MAIOR Velocidade no campo.
def estocada_m(Atacante, Alvo, AlvosAliados, ataque, Partida,
               poder_ataque, defesa_alvo, dano_base,
               critico, bonus_critico, Acertou, Protegido):
    ativos = [p for p in (Partida.pokemons_jogador1 + Partida.pokemons_jogador2) if p.vivo and p.ativo]
    if ativos:
        maior_vel = max(p.vel for p in ativos)
        if Atacante.ativo and Atacante.vel >= maior_vel:
            poder_ataque = int(poder_ataque * 1.3)
    return poder_ataque, defesa_alvo, critico, bonus_critico, Acertou, Protegido

# 13 — Transformar (s): Clona o alvo e substitui o atacante; vida do clone = 75% da vida do alvo.
def transformar_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):
    import copy
    if Atacante in Partida.pokemons_jogador1:
        equipe = Partida.pokemons_jogador1
    else:
        equipe = Partida.pokemons_jogador2
    idx = equipe.index(Atacante)

    novo = copy.deepcopy(Alvo)
    novo.vida = max(1, int(Alvo.vida * 0.75))

    equipe[idx] = novo

# 14 — Resetar Forçado (s): Zera variações do alvo (permanentes e temporárias), exceto efeitos.
def resetar_forcado_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):
    for stat in ["atk","def","spA","spD","vel","mag","per","ene","enR","crD","crC","vamp","asse"]:
        setattr(Alvo, f"var_per_{stat}", 0)
    Alvo.Verifica(Partida)

# 15 — Manobra Evasiva (p): Se for crítico, o atacante ganha Evasivo.
def manobra_evasiva_p(Atacante, Alvo, AlvosAliados, ataque, Partida, Log,
                      dano_aplicado, Acertou, Protegido, critico, morreu):
    if critico:
        Atacante.AplicarEfeito("Evasivo", Atacante, Log)

# 16 — Barragem (s): Ganhe barreira igual a 35% da Mag; se for crítico, ganhe 40%.
def barragem_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):
    ganho = 0.40 if critico else 0.35
    valor = int(getattr(Atacante, "mag", 0) * ganho)
    Alvo.ReceberBarreira(valor, Log)

# 17 — Investida (p): Causa 10% do dano aplicado ao alvo como dano de recuo ao atacante.
def investida_p(Atacante, Alvo, AlvosAliados, ataque, Partida, Log,
                dano_aplicado, Acertou, Protegido, critico, morreu):
    if dano_aplicado and dano_aplicado > 0:
        recuo = int(dano_aplicado * 0.10)
        if Log["SubLogs"]:
            pass
        else:
            Log["SubLogs"] = []
        SubLog = {
            "Alvo": Atacante
        }
        Atacante.TomarDano(recuo, SubLog)
        Log["SubLogs"].append(SubLog)

# 18 — Grito de Guerra (s): Aumenta Atk de todos os aliados em 10%.
def grito_de_guerra_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):
    # identifica a equipe do atacante
    equipe = Partida.pokemons_jogador1 if Atacante in Partida.pokemons_jogador1 else Partida.pokemons_jogador2
    for aliado in equipe:
        if aliado is Atacante or not getattr(aliado, "vivo", True):
            continue
        aumento = int(getattr(aliado, "base_atk", 0) * 0.10)
        aliado.ModificarStatus("atk", aumento, Log)

# 20 — Inflar (s): Ganhe barreira igual a 25% da Vida atual.
def inflar_s(Atacante, Alvo, AlvosAliados, ataque, Partida, Log, Acertou, critico):
    valor = int(getattr(Atacante, "vida", 0) * 0.25)
    Alvo.ReceberBarreira(valor, Log)

AtkDic.update({
    "1s": Enraivecer_s,          # 1 — Enraivecer (s)
    "2f": Recarga_f,             # 2 — Recarga (f)
    "3s": Provocar_s,            # 3 — Provocar (s)
    "4s": Rosnar_s,              # 4 — Rosnar (s)
    "5s": biscoito_s,            # 5 — biscoito (s)
    "8m": tapa_magico_m,         # 8 — tapa_magico (m)
    "9s": resetar_s,             # 9 — resetar (s)
    "10m": golpe_critico_m,      # 10 — golpe_critico (m)
    "12m": estocada_m,           # 12 — Estocada (m)
    "13s": transformar_s,        # 13 — Transformar (s)
    "14s": resetar_forcado_s,    # 14 — Resetar Forçado (s)
    "15p": manobra_evasiva_p,    # 15 — Manobra Evasiva (p)
    "16s": barragem_s,           # 16 — Barragem (s)
    "17p": investida_p,          # 17 — Investida (p)
    "18s": grito_de_guerra_s,    # 18 — Grito de Guerra (s)
    "20s": inflar_s,             # 20 — Inflar (s)
})
