import pygame
import random
import math
import pandas as pd
import numpy as np

df = pd.read_csv("Dados/Itens.csv")

# 0 agora = vazio
OBJ_NOMES = {
    1:  "Arvore",
    2:  "Palmeira",
    3:  "Arvore2",
    4:  "Pinheiro",
    5:  "Ouro",
    6:  "Diamante",
    7:  "Esmeralda",
    8:  "Rubi",
    9:  "Ametista",
    10: "Cobre",
    11: "Pedra",
    12: "Arbusto",
    13: "Lava",
}

OBJ_CONFIG = {
    1:  {"tipo": "circle", "tamanho": 35, "campo": 80,  "intensidade": 18},  # Arvore
    2:  {"tipo": "circle", "tamanho": 40, "campo": 95,  "intensidade": 18},  # Palmeira
    3:  {"tipo": "circle", "tamanho": 35, "campo": 70,  "intensidade": 18},  # Arvore2
    4:  {"tipo": "circle", "tamanho": 32, "campo": 80,  "intensidade": 18},  # Pinheiro

    5:  {"tipo": "circle", "tamanho": 45,  "campo": 75,  "intensidade": 20},  # Ouro (bloco)
    6:  {"tipo": "circle", "tamanho": 45,  "campo": 75,  "intensidade": 20},  # Diamante
    7:  {"tipo": "circle", "tamanho": 45,  "campo": 75,  "intensidade": 20},  # Esmeralda
    8:  {"tipo": "circle", "tamanho": 45,  "campo": 75,  "intensidade": 20},  # Rubi
    9:  {"tipo": "circle", "tamanho": 45,  "campo": 75,  "intensidade": 20},  # Ametista
    10: {"tipo": "circle", "tamanho": 45,  "campo": 75,  "intensidade": 20},  # Cobre

    11: {"tipo": "circle", "tamanho": 45, "campo": 75,  "intensidade": 20},  # Pedra
    12: {"tipo": "circle", "tamanho": 10, "campo": 50, "intensidade": 18},   # Arbusto
    13: {"tipo": "circle", "tamanho": 90, "campo": 120, "intensidade": 18},  # Lava
}

DEFAULT_OBJ = {"tipo": "rect", "tamanho": 0, "campo": 0, "intensidade": 0.0}

def GridToDic(grid_objetos, obj_nomes=OBJ_NOMES, obj_config=OBJ_CONFIG):
    mapa_estruturas = {}

    if not isinstance(grid_objetos, np.ndarray):
        grid_objetos = np.array(grid_objetos, dtype=np.uint8)

    # np.ndenumerate percorre direto índices (y, x) e valor
    for (y, x), valor in np.ndenumerate(grid_objetos):
        if valor == 0:
            continue  # 0 = vazio 

        nome = obj_nomes.get(int(valor))
        if nome is None:  # pula valores inválidos
            continue

        cfg = obj_config.get(int(valor), DEFAULT_OBJ)

        estrutura = Estrutura(
            nome,
            (x, y),
            tipo_colisao=("circle" if cfg.get("tipo", "rect") == "circle" else "rect"),
            tamanho=int(cfg.get("tamanho", 0)),
            campo=int(cfg.get("campo", 0)),
            intensidade=float(cfg.get("intensidade", 0.0)),
        )

        mapa_estruturas[(x, y)] = estrutura

    return mapa_estruturas

class Estrutura:
    def __init__(self, nome, pos, tipo_colisao="circle", tamanho=50, campo=120, intensidade=20.0):
        """
        pos: posição central NO MUNDO (tiles) — você já usa assim.
        tipo_colisao: "rect" ou "circle" (mantive compatível com seu debug)
        tamanho: se "circle", raio base em PX para a hitbox
        campo: margem em PX além da hitbox para aplicar força
        intensidade: força do empurrão do campo (em TILES/segundo)
        """
        self.nome = nome
        self.pos = pos
        self.tipo_colisao = tipo_colisao
        self.tamanho = tamanho
        self.Campo = campo
        self.Intensidade = intensidade

        # armazenos de desenho/colisão (em TELA, como seu fluxo atual)
        self.rect = None          # retângulo reduzido em tela (caso RECT)
        self.HitBox = None        # ("rect", Rect) ou ("circle", (cx,cy), r)
        self._center_tela = None  # cx,cy da sprite em TELA (para círculos)

    def _circle_rect_collide(self, circle_center, circle_radius, rect_obj):
        """Teste preciso circle-rect em TELA."""
        cx, cy = circle_center
        x = max(rect_obj.left,  min(cx, rect_obj.right))
        y = max(rect_obj.top,   min(cy, rect_obj.bottom))
        dx = cx - x
        dy = cy - y
        return (dx*dx + dy*dy) <= (circle_radius * circle_radius)

    def verifica_colisao_player(self, player_rect_tela):
        """True se o player tocar a HITBOX (núcleo) — TELA vs TELA (como seu código usa)."""
        if not self.HitBox:
            return False

        tipo = self.HitBox[0]
        if tipo == "rect":
            hit_rect = self.HitBox[1]
            return player_rect_tela.colliderect(hit_rect)

        # circle
        _, center, raio = self.HitBox
        return self._circle_rect_collide(center, raio, player_rect_tela)

    def aplicar_campo_forca(self, player_rect_tela, move_tiles_vec, tile_px, delta_time):
        """
        Ajusta (dx,dy) em TILES/frame com base no CAMPO.
        - player_rect_tela: pygame.Rect do player em TELA
        - move_tiles_vec: (dx,dy) em TILES/frame
        - tile_px: px por tile
        - delta_time: s
        """
        if not self.HitBox or self.Campo <= 0:
            return move_tiles_vec

        dx_tiles, dy_tiles = move_tiles_vec
        mvx_px = dx_tiles * tile_px
        mvy_px = dy_tiles * tile_px

        tipo = self.HitBox[0]

        # Função auxiliar: devolve vetor "para fora" do núcleo e um t em [0..1]
        def _rect_core_push(core_rect):
            # zona = core inflado pelo Campo
            zona = core_rect.inflate(self.Campo * 2, self.Campo * 2)
            if not zona.colliderect(player_rect_tela):
                return None

            # Ponto do player mais próximo do núcleo: clamp do centro do player no core
            pcx, pcy = player_rect_tela.center
            nx = min(max(pcx, core_rect.left),  core_rect.right)
            ny = min(max(pcy, core_rect.top),   core_rect.bottom)
            vx = pcx - nx
            vy = pcy - ny
            dist = math.hypot(vx, vy)
            if dist == 0:
                # Se estiver exatamente colado/na borda, usa normal pelo centro do core
                cx, cy = core_rect.center
                vx = (pcx - cx) or 1.0
                vy = (pcy - cy) or 0.0
                dist = math.hypot(vx, vy)
            dirx = vx / dist
            diry = vy / dist

            # quão perto do core: 0 na borda da zona, 1 colado no core
            # aprox por distância até o core (0..Campo)
            t = max(0.0, min(1.0, 1.0 - (dist / max(self.Campo, 1))))
            return (dirx, diry, t)

        if tipo == "rect":
            core = self.HitBox[1]
            out = _rect_core_push(core)
            if out is not None:
                dirx, diry, t = out
                # reduz componente "toward" (contra o core)
                towardx, towardy = -dirx, -diry
                comp_toward = mvx_px * towardx + mvy_px * towardy
                if comp_toward > 0:
                    atenuacao = 0.7 * t
                    mvx_px -= towardx * (comp_toward * atenuacao)
                    mvy_px -= towardy * (comp_toward * atenuacao)

                # empurrão para fora (tiles/s -> px/frame)
                push_tiles = self.Intensidade * t * delta_time
                mvx_px += dirx * (push_tiles * tile_px)
                mvy_px += diry * (push_tiles * tile_px)

        else:  # "circle"
            center, raio = self.HitBox[1], self.HitBox[2]
            cx, cy = center

            # 1) testa zona com circle-rect usando raio expandido
            raio_zona = raio + self.Campo
            if not self._circle_rect_collide((cx, cy), raio_zona, player_rect_tela):
                return (mvx_px / tile_px, mvy_px / tile_px)

            # 2) direção para fora baseada no ponto do player mais próximo do centro
            pcx, pcy = player_rect_tela.center
            vx = pcx - cx
            vy = pcy - cy
            dist = math.hypot(vx, vy)
            if dist == 0:
                vx, vy, dist = 1.0, 0.0, 1.0
            dirx = vx / dist
            diry = vy / dist

            # 3) intensidade normalizada (0 na borda da zona, 1 no centro)
            limite = float(raio_zona)
            t = max(0.0, min(1.0, 1.0 - (dist / limite)))

            # 4) reduz componente "toward" (apenas se estiver avançando)
            towardx, towardy = -dirx, -diry
            comp_toward = mvx_px * towardx + mvy_px * towardy
            if comp_toward > 0:
                atenuacao = 0.7 * t
                mvx_px -= towardx * (comp_toward * atenuacao)
                mvy_px -= towardy * (comp_toward * atenuacao)

            # 5) empurrão para fora
            push_tiles = self.Intensidade * t * delta_time
            mvx_px += dirx * (push_tiles * tile_px)
            mvy_px += diry * (push_tiles * tile_px)

        # volta para TILES/frame
        return (mvx_px / tile_px, mvy_px / tile_px)
    
    def desenhar(self, tela, pos_tela, img):
        """
        Mantém seu desenho em TELA. Aqui definimos a HitBox (núcleo) também em TELA.
        """
        largura, altura = img.get_size()
        pos_img = (pos_tela[0] - largura // 2, pos_tela[1] - altura // 2)
        tela.blit(img, pos_img)

        # rect de desenho (opcional)
        self.draw_rect = pygame.Rect(pos_img[0], pos_img[1], largura, altura)

        # --- rect reduzido para NÚCLEO quando for retângulo ---
        reducao_w = largura * 0.15
        reducao_h = altura * 0.15
        novo_x = pos_img[0] + reducao_w / 2
        novo_y = pos_img[1] + reducao_h / 2
        novo_w = largura - reducao_w
        novo_h = altura - reducao_h
        self.rect = pygame.Rect(novo_x, novo_y, novo_w, novo_h)  # continua como antes

        # === definir HITBOX: respeita self.tipo_colisao ===
        if self.tipo_colisao == "circle":
            # centro em TELA (do sprite) e raio = self.tamanho (px)
            cx, cy = int(pos_tela[0]), int(pos_tela[1])
            raio = int(self.tamanho) if self.tamanho else int(min(largura, altura) * 0.35)
            self._center_tela = (cx, cy)
            self.HitBox = ("circle", (cx, cy), raio)
        else:
            # retângulo reduzido como núcleo
            self.HitBox = ("rect", self.rect)

        # --- Debug (opcional) ---
        if self.tipo_colisao == "circle":
            # Campo (raio expandido)
            pygame.draw.circle(tela, (0, 100, 0), self._center_tela,
                               int((self.HitBox[2] + self.Campo)), 1)
            # Núcleo
            pygame.draw.circle(tela, (0, 200, 0), self._center_tela,
                               int(self.HitBox[2]), 1)
        else:
            pygame.draw.rect(tela, (0, 200, 0), self.rect, 1)  # núcleo
            pygame.draw.rect(tela, (0, 100, 0), self.rect.inflate(self.Campo*2, self.Campo*2), 1)  # campo

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
        aumento_w = int(largura * 1.5)
        aumento_h = int(altura * 1.5)

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

