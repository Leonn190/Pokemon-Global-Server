import pygame

from Codigo.Prefabs.BotoesPrefab import Botao, Botao_Alavanca
from Codigo.Prefabs.FunçõesPrefabs import Slider
from Codigo.Prefabs.Sonoridade import VerificaSonoridade

B1= {}
B2 = {}

GerouSurface = False
surface = None

def aplicar_claridade(tela, claridade):
    global GerouSurface, surface

    if GerouSurface is False:
        surface = pygame.Surface(tela.get_size())
        surface = surface.convert_alpha()
        GerouSurface = True

    if claridade == 75:
        return  # valor neutro, sem efeito

    if claridade < 75:
        # Escurece com preto
        intensidade = int((75 - claridade) / 50 * 50)  # 25 → 150, 74 → quase 0
        surface.fill((0, 0, 0, intensidade))
    else:
        # Clareia com branco
        intensidade = int((claridade - 75) / 25 * 70)  # 100 → 150, 76 → pequeno valor
        surface.fill((255, 255, 255, intensidade))

    tela.blit(surface, (0, 0))

def SalvarConfig(Config):
    with open("ConfigFixa.py", "w", encoding="utf-8") as f:
        f.write("# Arquivo gerado automaticamente para armazenar configurações fixas\n\n")
        f.write(f"Config = {repr(Config)}\n")

def TelaConfigurações(tela, estados, eventos, parametros):
    from Codigo.Cenas.Inicio import Fontes, Cores, Texturas, Outros

    if parametros["TelaConfigurações"]["Entrou"]:
        if pygame.mouse.get_pressed()[0]:
            return
        else:
            parametros["TelaConfigurações"]["Entrou"] = False

    Voltar = parametros["TelaConfigurações"]["Voltar"]

    x = 510
    y = 200
    largura = 900
    altura = 600

    pygame.mixer.music.set_volume(parametros["Config"]["Volume"])

    # Fundo do painel
    pygame.draw.rect(tela, (50, 50, 50), (x, y, largura, altura))  # Painel escuro
    pygame.draw.rect(tela, (200, 200, 200), (x, y, largura, altura), 4)  # Borda clara

    # Título no topo central
    titulo = Fontes[60].render("Configurações", True, Cores["branco"])
    titulo_rect = titulo.get_rect(center=(x + largura // 2, y + 40))
    tela.blit(titulo, titulo_rect)

    # Sliders
    parametros["Config"]["Volume"] = Slider(tela, "Volume", x + 50, y + 110, 670, parametros["Config"]["Volume"], 0.0, 0.8, (180, 180, 180), (255, 255, 255), eventos, "%")
    parametros["Config"]["Claridade"] = Slider(tela, "Claridade", x + 50, y + 180, 670, parametros["Config"]["Claridade"], 0, 100, (180, 180, 180), (255, 255, 255), eventos, "%")
    parametros["Config"]["FPS"] = Slider(tela, "FPS", x + 50, y + 250, 670, parametros["Config"]["FPS"], 20, 240, (180, 180, 180), (255, 255, 255), eventos)

    # Botões alavanca
        # Botão Mudo
    texto_mudo = Fontes[30].render("Mudo:", True, Cores["branco"])
    tela.blit(texto_mudo, (x + 110, y + 300))
    parametros["Config"]["Mudo"] = Botao_Alavanca(
        tela, (x + 240, y + 295, 150, 50), Fontes[30], estados.setdefault("Mudo", {}), eventos,
        parametros["Config"].get("Mudo", False),
        valores=[False, True],
        cores=[(100, 0, 0), (0, 150, 0)],
        textos=["Desligado", "Ligado"],
        som="Clique"
    )

    texto_fps = Fontes[30].render("Mostrar FPS:", True, Cores["branco"])
    tela.blit(texto_fps, (x + 460, y + 300))
    parametros["Config"]["FPS Visivel"] = Botao_Alavanca(
        tela, (x + 670, y + 295, 150, 50), Fontes[30], estados.setdefault("FPS Visivel", {}), eventos,
        parametros["Config"].get("FPS Visivel", False),
        valores=[False, True],
        cores=[(100, 0, 0), (0, 150, 0)],
        textos=["Desligado", "Ligado"],
        som="Clique"
    )

    texto_cords = Fontes[30].render("Mostrar Cords:", True, Cores["branco"])
    tela.blit(texto_cords, (x + 25, y + 380))
    parametros["Config"]["Cords Visiveis"] = Botao_Alavanca(
        tela, (x + 240, y + 375, 150, 50), Fontes[30], estados.setdefault("Cords Visiveis", {}), eventos,
        parametros["Config"].get("Cords Visiveis", False),
        valores=[False, True],
        cores=[(100, 0, 0), (0, 150, 0)],
        textos=["Desligado", "Ligado"],
        som="Clique"
    )

    texto_ping = Fontes[30].render("Mostrar Ping:", True, Cores["branco"])
    tela.blit(texto_ping, (x + 460, y + 380))
    parametros["Config"]["Ping Visivel"] = Botao_Alavanca(
        tela, (x + 670, y + 375, 150, 50), Fontes[30], estados.setdefault("Ping Visivel", {}), eventos,
        parametros["Config"].get("Ping Visivel", False),
        valores=[False, True],
        cores=[(100, 0, 0), (0, 150, 0)],
        textos=["Desligado", "Ligado"],
        som="Clique"
    )

    texto_precarregamento = Fontes[30].render("Pré-Carregamento:", True, Cores["branco"])
    tela.blit(texto_precarregamento, (x + 450, y + 460))
    parametros["Config"]["Pré-Carregamento"] = Botao_Alavanca(
        tela, (x + 670, y + 455, 150, 50), Fontes[30], estados.setdefault("Pré-Carregamento", {}), eventos,
        parametros["Config"].get("Pré-Carregamento", False),
        valores=[False, True],
        cores=[(100, 0, 0), (0, 150, 0)],
        textos=["Desligado", "Ligado"],
        som="Clique"
    )

    # Botões de Voltar e Salvar
    Botao(tela, "Voltar", (x + largura - 470 - 390, y + altura - 85, 390, 70), Texturas["azul"], Cores["preto"], Cores["branco"],
          [lambda: Voltar(),lambda: VerificaSonoridade(parametros["Config"]), lambda: parametros.update({"TelaConfigurações": {"Entrou": True}})], Fontes[40], estados.setdefault("Voltar", {}), eventos=eventos)

    Botao(tela, "Salvar", (x + largura - 40 - 390, y + altura - 85, 390, 70), Texturas["verde"], Cores["preto"], Cores["branco"],
          [lambda: SalvarConfig(parametros["Config"]), lambda: Voltar(), VerificaSonoridade(parametros["Config"]), lambda: parametros.update({"TelaConfigurações": {"Entrou": True}})], Fontes[40], estados.setdefault("Salvar", {}), eventos=eventos)
    