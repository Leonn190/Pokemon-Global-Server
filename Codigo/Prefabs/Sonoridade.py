import pygame
pygame.mixer.init()

silencio = False
Volume = 0.0

def VerificaSonoridade(config):
    global silencio
    global Volume

    if config["Mudo"]:
        silencio = True
    else:
        silencio = False
    
    Volume = config["Volume"] 

Sons = {
    "Clique": {"Som": lambda: pygame.mixer.Sound("Recursos/Audio/Sons/Clique.wav"), "Volume": 0.75},
    "Bloq": {"Som": lambda: pygame.mixer.Sound("Recursos/Audio/Sons/Bloq.wav"), "Volume": 0.85}
}

def tocar(som):
    audio = Sons[som]["Som"]()
    volume = Sons[som]["Volume"] * Volume

    if silencio:
        volume = 0

    audio.set_volume(min(volume, 1))  # Garante que não passa de 1
    audio.play()
    if volume > 1:
        audio2 = Sons[som]["Som"]()
        audio2.set_volume(min(volume - 1, 1))
        audio2.play()

def Musica(Nome):

    pygame.mixer.music.load(f'Recursos/Audio/Musicas/{Nome}.ogg')  
    pygame.mixer.music.set_volume(Volume)
    pygame.mixer.music.play(-1)
