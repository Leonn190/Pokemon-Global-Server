import pygame
pygame.mixer.init()

silencio = {"Sim": False}

def VerificaModoSilencioso(config):
    global silencio
    if config["Modo silencioso"]:
        silencio["Sim"] = True
    else:
        silencio["Sim"] = False

Sons = {
    
}

def tocar(som):
    audio = Sons[som]["Som"]()
    volume = Sons[som]["Volume"]

    if silencio["Sim"]:
        volume = 0

    audio.set_volume(min(volume, 1))  # Garante que não passa de 1
    audio.play()
    if volume > 1:
        audio2 = Sons[som]["Som"]()
        audio2.set_volume(min(volume - 1, 1))
        audio2.play()