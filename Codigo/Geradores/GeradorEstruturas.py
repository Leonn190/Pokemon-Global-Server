import pygame

class Estrutura:
    def __init__(self, nome, pos):
        self.nome = nome
        self.pos = pos  # posição central no mundo (x, y) em tiles
        self.rect = None  # será atualizado dinamicamente

    def desenhar(self, tela, pos_tela, img):
        largura, altura = img.get_size()

        # Desenhar com o centro no tile
        pos_img = (pos_tela[0] - largura // 2, pos_tela[1] - altura // 2)
        tela.blit(img, pos_img)

        # Atualizar o rect da estrutura para refletir a posição da imagem
        self.rect = pygame.Rect(pos_img[0], pos_img[1], largura, altura)

        # Debug opcional
        # pygame.draw.rect(tela, (255, 0, 0), self.rect, 2)

def GridToDic(grid_numerica):

    mapa_estruturas = {}
    
    for y, linha in enumerate(grid_numerica):
        for x, valor in enumerate(linha):
            if valor == 0:
                continue

            if valor == 1:
                nome = "Arvore"
            elif valor == 2:
                nome = "Pedra"
            elif valor == 3:
                nome = "Moita"
            else:
                continue  # ignora valores não mapeados

            estrutura = Estrutura(nome, (x, y))
            mapa_estruturas[(x, y)] = estrutura

    return mapa_estruturas

