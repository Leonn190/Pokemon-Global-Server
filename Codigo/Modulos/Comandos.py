ComandosMundo = {}

def LevelUp(n=1):
    from Codigo.Cenas.Mundo import player
    player.GanharXp((100 + player.Nivel * 20) * n)

# registra sem a barra
ComandosMundo.update({
    "LevelUp": LevelUp
})
