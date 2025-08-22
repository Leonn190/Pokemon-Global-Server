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

def GivePokemon(identificador,mod):
    from Codigo.Geradores.GeradorPokemon import criar_pokemon_especifico, desserializar_pokemon, MaterializarPokemon
    pokemon = desserializar_pokemon(criar_pokemon_especifico(identificador))

    #area q usa o mod

    pokemon = MaterializarPokemon(pokemon)

def Tp(x,y):
    from Codigo.Cenas.Mundo import player
    player.Loc = [x,y]

def 

# registra sem a barra
ComandosMundo.update({
    "Xp": Xp,
    "Give": Give,
    "GivePokemon": GivePokemon,
    "Tp": Tp
})
