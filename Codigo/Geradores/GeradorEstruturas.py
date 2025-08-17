import pygame
import random
import time
import pandas as pd

df = pd.read_csv("Dados/Itens.csv")

OBJ_NOMES = {
    0:  "Arvore",
    1:  "Palmeira",
    2:  "Arvore2",
    3:  "Pinheiro",
    4:  "Ouro",
    5:  "Diamante",
    6:  "Esmeralda",
    7:  "Rubi",
    8:  "Ametista",
    9:  "Cobre",
    10: "Pedra",
    11: "Arbusto",
    12: "Lava",
}

def GridToDic(grid_objetos):
    mapa_estruturas = {}
    for y, linha in enumerate(grid_objetos):
        for x, valor in enumerate(linha):
            nome = OBJ_NOMES.get(valor)
            if nome is None:       # pula vazio (-1) e qualquer valor não mapeado
                continue
            estrutura = Estrutura(nome, (x, y))
            mapa_estruturas[(x, y)] = estrutura
    return mapa_estruturas

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

        # Reduzir 10% do tamanho (5% de cada lado)
        reducao_w = largura * 0.15
        reducao_h = altura * 0.15
        novo_x = pos_img[0] + reducao_w / 2
        novo_y = pos_img[1] + reducao_h / 2
        novo_w = largura - reducao_w
        novo_h = altura - reducao_h

        # Atualizar rect de colisão reduzido
        self.rect = pygame.Rect(novo_x, novo_y, novo_w, novo_h)

        # Debug opcional
        pygame.draw.rect(tela, (255, 0, 0), self.rect, 2)

class Bau:
    RARIDADES = ["Comum", "Incomum", "Raro", "Epico", "Mitico", "Lendario"]

    def __init__(self, raridade, ID, Loc):
        self.raridade = self.traduzir_raridade(raridade)
        self.NUMraridade = raridade
        self.ID = ID
        self.Loc = Loc
        self.Aberto = False
        self.Animando = False
        self.TempoAposAbrir = 0
        self.rect = None
        self.Apagar = False

        self.tabela_probabilidades = [
            [55, 30, 10,  4, 1, 0],
            [44, 33, 15,  9, 3, 1],
            [25, 40, 17, 10, 5, 3],
            [20, 22, 28, 15,10, 5],
            [14, 14, 25, 25,13, 9],
            [13, 13, 19, 19,23,13]
        ]
        self.tabela_qtd_itens = {
            1: [1, 2],
            2: [1, 2, 3],
            3: [2, 3],
            4: [2, 3, 4],
            5: [3, 4],
            6: [3, 4, 5]
        }

    def traduzir_raridade(self, valor):
        if 1 <= valor <= 6:
            return self.RARIDADES[valor - 1]
        return "Desconhecida"
    
    def desenhar(self, tela, pos_tela, img):
        largura, altura = img.get_size()

        # Desenhar com o centro no tile
        pos_img = (pos_tela[0] - largura // 2, pos_tela[1] - altura // 2)
        tela.blit(img, pos_img)

        # Calcular rect de colisão 30% maior (15% extra para cada lado)
        aumento_w = int(largura * 1.2)
        aumento_h = int(altura * 1.2)

        novo_w = largura + aumento_w
        novo_h = altura + aumento_h

        novo_x = pos_img[0] - aumento_w // 2
        novo_y = pos_img[1] - aumento_h // 2

        self.rect = pygame.Rect(novo_x, novo_y, novo_w, novo_h)

        # Debug opcional
        pygame.draw.rect(tela, (255, 0, 0), self.rect, 2)
    
    def AbrirBau(self, player, parametros):

        self.Aberto = True
        player.BausAbertos += 1
        parametros["BausRemover"].append(self.ID)
        
        # 1. Quantidade de itens a adicionar
        possiveis_qtds = self.tabela_qtd_itens[self.NUMraridade]
        qtd_itens = random.choice(possiveis_qtds)

        # 2. Probabilidades da raridade dos itens
        probs_raridades = self.tabela_probabilidades[self.NUMraridade - 1]
        total = sum(probs_raridades)
        probs_norm = [p / total for p in probs_raridades]  # normalizar

        for _ in range(qtd_itens):
            # 3. Sortear raridade do item (de 1 a 6)
            raridade_item = random.choices(range(1, 7), weights=probs_norm)[0]

            # 4. Filtrar itens com essa raridade
            itens_possiveis = df.copy()

            # Aumenta raridade efetiva das frutas em +1 para sorteio
            itens_possiveis['RaridadeSorteio'] = itens_possiveis.apply(
                lambda row: min(int(row['Raridade']) + 1, 6) if row['Estilo'] == 'fruta' else int(row['Raridade']),
                axis=1
            )

            # Filtrar por raridade sorteada
            itens_filtrados = itens_possiveis[itens_possiveis['RaridadeSorteio'] == raridade_item]

            # Se não encontrar nada nessa raridade, tentar em qualquer uma
            if itens_filtrados.empty:
                itens_filtrados = itens_possiveis

            item_sorteado = itens_filtrados.sample().iloc[0]

            nome = item_sorteado['Nome']
            raridade = int(item_sorteado['Raridade'])  # raridade original
            estilo = item_sorteado['Estilo']
            descriçao = item_sorteado['Descrição']

            if estilo in ["bola", "fruta"]:
                M1 = "Lançar"
                M2 = "Mirar"
            else:
                M1 = "Tapa"
                M2 = "Nada"

            # 5. Adicionar ao inventário do player
            player.AdicionarAoInventario(player, nome, raridade, estilo, descriçao, M1, M2)

