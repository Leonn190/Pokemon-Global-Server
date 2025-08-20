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

Musicas = {
    "TelaInicio": {
        "arquivo": "Recursos/Audio/Musicas/TelaInicio.ogg",
        "loop": 12.7,
        "fimloop": 110.55
    },
    "ConfrontoDoVale": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoVale.ogg",
        "loop": 2.34,
        "fimloop": 83.6
    },
    "ConfrontoDaNeve": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDaNeve.ogg",
        "loop": 2.32,
        "fimloop": 83.6
    },
    "ConfrontoDoMar": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoMar.ogg",
        "loop": 2.27,
        "fimloop": 83.64
    },
    "ConfrontoDoDeserto": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoDeserto.ogg",
        "loop": 2.33,
        "fimloop": 83.655
    },
    "ConfrontoDoVulcao": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoVulcao.ogg",
        "loop": 2.34,
        "fimloop": 83.62
    },
    "Vale": {
        "arquivo": "Recursos/Audio/Musicas/Vale.ogg",
        "loop": 3.2,
        "fimloop": 111.9
    },
    "Neve": {
        "arquivo": "Recursos/Audio/Musicas/Neve.ogg",
        "loop": 4.2,
        "fimloop": 68.35
    },
    "Deserto": {
        "arquivo": "Recursos/Audio/Musicas/Deserto.ogg",
        "loop": 0.2,
        "fimloop": 87.45
    }
}

# Variáveis de controle
_musica_atual = None
_loop_point = 0.0
_fimloop_point = 0.0

def Musica(nome):
    """Inicia a música e define os pontos de loop."""
    global _musica_atual, _loop_point, _fimloop_point
    if nome not in Musicas:
        print(f"[ERRO] Música '{nome}' não encontrada.")
        return

    dados = Musicas[nome]
    _musica_atual = nome
    _loop_point = dados["loop"]
    _fimloop_point = dados["fimloop"]

    pygame.mixer.music.load(dados["arquivo"])
    pygame.mixer.music.set_volume(Volume)
    pygame.mixer.music.play()  # toca do início

def AtualizarMusica():
    """Chamar dentro do loop principal a cada frame para manter o loop perfeito."""
    if _musica_atual and pygame.mixer.music.get_busy():
        pos = pygame.mixer.music.get_pos() / 1000.0
        if pos >= _fimloop_point:
            pygame.mixer.music.play(-1, start=_loop_point)


