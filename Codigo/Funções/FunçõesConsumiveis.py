import random

ConsumiveisDic = {}

def Pokeball(pokemon, player, dados, crit):
    return 1.0

def Greatball(pokemon, player, dados, crit):
    return 1.4

def Ultraball(pokemon, player, dados, crit):
    return 1.8

def Masterball(pokemon, player, dados, crit):
    return 5.0

def Levelball(pokemon, player, dados, crit):
    pokemon.Dados["Nivel"] = min(pokemon.Dados.get("Nivel", 1) + 5, 100)
    nivel_pokemon = pokemon.Dados.get("Nivel", 1)
    return 1 + nivel_pokemon / 90

def Furyball(pokemon, player, dados, crit):
    if pokemon.Irritado:
        return 500
    else:
        return 1.0

def Heavyball(pokemon, player, dados, crit):
    peso = pokemon.Dados.get("Peso", 1)
    return min(1.0 + peso / 200, 2.5)

def Aquaball(pokemon, player, dados, crit):
    from Codigo.Cenas.Mundo import mapa
    if mapa.GridBiomas[pokemon.Loc[0]][pokemon.Loc[1]] == 0:
        return 1.9
    return 1.0

def Attemptball(pokemon, player, dados, crit):
    tentativas = pokemon.Tentativas
    return min(1.0 + (tentativas * 0.15), 2.5)

def Premierball(pokemon, player, dados, crit):
    if pokemon.Batalhando:
        return 1.92
    else:
        return 1.02

def Candyball(pokemon, player, dados, crit):
    pokemon.DocesExtras *= 3
    return 1.03

def Loveball(pokemon, player, dados, crit):
    pokemon.Dados["Amizade"] = pokemon.Dados.get("Amizade", 0) + 20
    return 1.06

def Secretball(pokemon, player, dados, crit):
    atributos = ["Vida", "Atk", "Def", "SpA", "SpD", "Vel", "Mag", "Per", "Ene", "EnR", "CrD", "CrC"]
    ivs = []
    for atributo in atributos:
        chave_iv = f"IV_{atributo}"
        iv_atual = pokemon.Dados.get(chave_iv, 0)
        aumento = iv_atual * (random.uniform(0.05, 0.15))
        novo_iv = min(iv_atual + aumento, 100)
        pokemon.Dados[chave_iv] = round(novo_iv, 2)
        ivs.append(novo_iv)
    novo_iv_total = round(sum(ivs) / len(ivs), 2)
    pokemon.Dados["IV"] = novo_iv_total
    return 1.0

def Fastball(pokemon, player, dados, crit):
    velocidade = pokemon.Dados.get("Vel", 1)
    return min(1.0 + (int(velocidade) / 60), 2.5)

def Fruitball(pokemon, player, dados, crit):
    frutas_dadas = pokemon.Frutas
    return min(1.0 + (frutas_dadas * 0.3), 2.5)

def Tallball(pokemon, player, dados, crit):
    from Codigo.Cenas.Mundo import mapa
    raio = 5
    x, y = pokemon.Loc
    for dx in range(-raio, raio + 1):
        for dy in range(-raio, raio + 1):
            pos = (x + dx, y + dy)
            if pos in mapa.DicObjetos:
                return 1.9
    return 1.0

def Sniperball(pokemon, player, dados, crit):
    return 1.2

def Beastball(pokemon, player, dados, crit):
    if pokemon.Dados["Raridade"] == "-":
        return 2.0
    return 1.05

ConsumiveisDic["Pokeball"] = Pokeball
ConsumiveisDic["Greatball"] = Greatball
ConsumiveisDic["Ultraball"] = Ultraball
ConsumiveisDic["Masterball"] = Masterball
ConsumiveisDic["Levelball"] = Levelball
ConsumiveisDic["Furyball"] = Furyball
ConsumiveisDic["Heavyball"] = Heavyball
ConsumiveisDic["Aquaball"] = Aquaball
ConsumiveisDic["Attemptball"] = Attemptball
ConsumiveisDic["Premierball"] = Premierball
ConsumiveisDic["Candyball"] = Candyball
ConsumiveisDic["Loveball"] = Loveball
ConsumiveisDic["Secretball"] = Secretball
ConsumiveisDic["Fastball"] = Fastball
ConsumiveisDic["Fruitball"] = Fruitball
ConsumiveisDic["Tallball"] = Tallball
ConsumiveisDic["Sniperball"] = Sniperball
ConsumiveisDic["Beastball"] = Beastball

