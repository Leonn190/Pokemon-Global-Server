ComandosMundo = {}

def LevelUp(n=1):
    from Codigo.Cenas.Mundo import player
    player.Nivel += int(n)

# registra sem a barra
ComandosMundo.update({
    "LevelUp": LevelUp
})
