import pygame
from Codigo.Prefabs.FunçõesPrefabs import cria_fundo_degrade

# Cores ajustadas
TIPO_CORES = {
    "normal":   ((250, 250, 250), (220, 220, 220)),        # mais branco
    "fogo":     ((255, 100, 0), (200, 0, 0)),
    "agua":     ((0, 150, 255), (0, 50, 200)),
    "eletrico": ((255, 255, 0), (255, 150, 0)),
    "planta":   ((50, 200, 50), (0, 100, 0)),
    "gelo":     ((150, 255, 255), (0, 200, 200)),
    "lutador":  ((255, 140, 40), (200, 90, 0)),            # laranja
    "venenoso": ((180, 0, 180), (100, 0, 100)),
    "terrestre":((200, 150, 50), (100, 70, 0)),
    "voador":   ((150, 200, 255), (50, 100, 200)),
    "psiquico": ((255, 100, 255), (180, 0, 180)),
    "inseto":   ((150, 200, 50), (80, 150, 0)),
    "pedra":    ((180, 150, 100), (100, 80, 50)),
    "fantasma": ((100, 50, 150), (50, 0, 100)),
    "dragao":   ((60, 120, 130), (0, 70, 80)),             # azul esverdeado escuro
    "sombrio":  ((60, 50, 40), (20, 15, 10)),              # mais escuro
    "metal":    ((180, 180, 200), (100, 100, 120)),
    "fada":     ((255, 180, 220), (230, 120, 170)),        # mais rosa
    "sonoro":   ((210, 210, 210), (170, 170, 170)),        # mais escuro que o normal
    "cosmico":  ((50, 50, 100), (0, 0, 40)),               # mais escuro
}

def cor_texto_para_fundo(c1, c2):
    """Determina se o texto deve ser branco ou preto baseado no brilho médio das cores."""
    brilho = (sum(c1) / 3 + sum(c2) / 3) / 2
    return (255, 255, 255) if brilho < 128 else (0, 0, 0)

def testar_fundos_degrade(tela):
    largura_tela, altura_tela = tela.get_size()
    tamanho_fundo = (160, 50)
    margem = 10
    colunas = 4
    fonte = pygame.font.SysFont(None, 22)

    for idx, (tipo, (cor1, cor2)) in enumerate(TIPO_CORES.items()):
        grad = cria_fundo_degrade(cor1, cor2, tamanho_fundo)
        
        linha = idx // colunas
        coluna = idx % colunas
        x = margem + coluna * (tamanho_fundo[0] + margem)
        y = margem + linha * (tamanho_fundo[1] + margem)
        
        tela.blit(grad, (x, y))

        cor_texto = cor_texto_para_fundo(cor1, cor2)
        texto = fonte.render(tipo.capitalize(), True, cor_texto)
        rect_texto = texto.get_rect(center=(x + tamanho_fundo[0]//2, y + tamanho_fundo[1]//2))
        tela.blit(texto, rect_texto)

# ----------------- TESTE -----------------
if __name__ == "__main__":
    pygame.init()
    tela = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    rodando = True
    while rodando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False

        tela.fill((30, 30, 30))
        testar_fundos_degrade(tela)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


