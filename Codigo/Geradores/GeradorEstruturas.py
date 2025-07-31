
class Estrutura:
    def __init__(self, nome, pos):
        self.nome = nome
        self.pos = pos  # (x, y)

    def desenhar(self, tela, pos_tela, img):
        tela.blit(img, pos_tela)

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
