ComandosMundo = {}

def Xp(n=1):
    from Codigo.Cenas.Mundo import player
    player.GanharXp(n)

def Give(identificador,n=1):
    from Codigo.Geradores.GeradorEstruturas import MaterializarItem
    from Codigo.Cenas.Mundo import player
    item = MaterializarItem(identificador)
    item["numero"] = n
    player.AdicionarAoInventario(item)

def GivePokemon(identificador, mod):
    from Codigo.Geradores.GeradorPokemon import (
        criar_pokemon_especifico,
        desserializar_pokemon,
        MaterializarPokemon
    )

    # cria o pokémon
    pokemon = desserializar_pokemon(criar_pokemon_especifico(identificador))

    # aplica as modificações
    if mod:
        partes = mod.split("/")
        for parte in partes:
            if "=" not in parte:
                continue
            chave, valor = parte.split("=", 1)

            # converte para número se der, senão fica string
            if valor.isdigit():
                valor = int(valor)
            elif valor.replace(".", "", 1).isdigit():
                valor = float(valor)

            if isinstance(pokemon[chave],list):
                pokemon[chave].append(valor)
            else:
                pokemon[chave] = valor

    return MaterializarPokemon(pokemon)

def Tp(x,y):
    from Codigo.Cenas.Mundo import player
    player.Loc = [x,y]

# registra sem a barra
ComandosMundo.update({
    "Xp": Xp,
    "Give": Give,
    "GivePokemon": GivePokemon,
    "Tp": Tp
})
