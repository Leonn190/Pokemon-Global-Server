from pypresence import Presence
import time

def iniciar_discord_presence():
    try:
        APP_ID = "1400921285009211543"
        rpc = Presence(APP_ID)
        rpc.connect()
        inicio = time.time()
        rpc.update(
            details="Pokémon Global Server Alpha",
            state="Jogando",
            start=inicio
        )
        print("Discord Presence iniciado.")
        return rpc
    except Exception as e:
        print("Erro ao conectar com o Discord:", e)
        return None
    