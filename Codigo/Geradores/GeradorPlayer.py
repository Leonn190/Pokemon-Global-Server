import math
import pygame

from Codigo.Prefabs.FunçõesPrefabs import texto_com_borda, Fluxo
from Codigo.Prefabs.Mensagens import adicionar_mensagem_item
from Codigo.Modulos.DesenhoPlayer import PegarRotaçao, CacheExtrairCor, escurecer_cor
from Codigo.Geradores.GeradorOutros import Projetil

ConsumiveisIMG = None

class Player:

    def __init__(self, Informações, Skins, Particulas):

        self.Code = Informações["Code"]
        self.Nome = Informações["Nome"]
        self.ID = Informações.get("ID", self.Nome + str(self.Code))

        self.Particulas = Particulas

        self.Pokemons = Informações["Pokemons"]
        self.Inventario = Informações["Inventario"]
        self.Ouro = Informações["Ouro"]
        self.SkinNumero = Informações["Skin"]
        self.Skin = Skins[self.SkinNumero]
        self.SkinRedimensionada = pygame.transform.scale(self.Skin, (83, 66))
        self.SkinsLiberadas = Informações.get("SkinsLiberadas", [1,2,3,4,5,6,7,8,9,10,11,12])
        self.Nivel = Informações["Nivel"]
        self.Xp = Informações["XP"]

        self.BatalhasVencidasPVP = Informações.get("BatalhasVencidasPVP", 0)
        self.BatalhasVencidasBOT = Informações.get("BatalhasVencidasBOT", 0)
        self.BausAbertos = Informações.get("BausAbertos", 0)
        self.PokemonsCapturados = Informações.get("PokemonsCapturados", 0)
        self.Passos = Informações.get("Passos", 0)
        self.TempoDeJogo = Informações.get("TempoDeJogo", 0)
        
        self.Mochila = Informações["Mochila"]
        self.Velocidade = Informações["Velocidade"]
        self.Maestria = Informações["Maestria"]

        self.Equipes = Informações["Equipes"]

        self.MaxItens = 100 * (self.Mochila + 1)
        self.Itens = sum([k["numero"] if k is not None else 0 for k in self.Inventario])

        self.Loc = Informações["Loc"]

        self.Selecionado = Informações.get("Selecionado",65)
        self.Angulo = 90

        self.estado_tapa = {"tapando": False, "inicio_tapa": 0, "tempo_ultimo_tapa": 0}

        self.rect = pygame.Rect(0, 0, 83, 66)
        self.rect.center = (self.Loc[0], self.Loc[1])  # Pos inicial

        self.mouse_anterior = pygame.mouse.get_pressed()
        self.Mirando = False

        self.Projeteis = []

        self.tile = 70

    def Atualizar(self, tela, delta_time, mapa, fonte, parametros, ItensIMG):
        # Movimento e projéteis
        self.mover(delta_time, mapa, parametros)

        self.TempoDeJogo += delta_time

        for projetil in self.Projeteis:
            projetil.atualizar(tela, self.Loc, self, delta_time)

        # Centro da tela
        largura_tela, altura_tela = tela.get_size()
        x_centro = largura_tela // 2
        y_centro = altura_tela // 2
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Ângulo (em graus e radianos)
        dx, dy = mouse_x - x_centro, mouse_y - y_centro
        angulo = math.degrees(math.atan2(dy, dx))
        angulo_correcao = angulo - 90
        angulo_rad = math.radians(angulo)
        self.angulo = angulo

        # Imagem e cor do corpo (cacheadas)
        imagem_corpo = self.SkinRedimensionada
        cor_braco = CacheExtrairCor(imagem_corpo)                         # cache de cor
        corpo_rotacionado = PegarRotaçao(imagem_corpo, angulo_correcao)   # cache de rotação

        # ===== DESENHO =====
        corpo_rect = corpo_rotacionado.get_rect(center=(x_centro, y_centro))
        tela.blit(corpo_rotacionado, corpo_rect)

        # Guarde o rect de desenho separadamente (para UI/debug), não use para colisão:
        self.draw_rect = corpo_rect

        # ===== COLISÃO / HITBOX =====
        # Crie um rect fixo (baseado na imagem SEM rotação), reduzido para evitar quinas de ar.
        # Ajuste self.hitbox_scale se quiser mais/menos folga.
        if not hasattr(self, "hitbox_scale"):
            self.hitbox_scale = 0.70  # 70% do tamanho do sprite base

        base_w, base_h = imagem_corpo.get_size()
        hit_w = max(4, int(base_w * self.hitbox_scale))
        hit_h = max(4, int(base_h * self.hitbox_scale))

        # Reuse o mesmo objeto Rect quando possível (menos GC)
        if not hasattr(self, "_hit_rect") or self._hit_rect.size != (hit_w, hit_h):
            self._hit_rect = pygame.Rect(0, 0, hit_w, hit_h)

        self._hit_rect.center = (x_centro, y_centro)

        # Este é o rect que TODA a lógica de colisão deve usar:
        self.rect = self._hit_rect

        # Braços (usa cor cacheada e ângulo em rad)
        self.desenhar_bracos(
            tela,
            (x_centro, y_centro),
            cor_braco,
            angulo_rad,
            ItensIMG,
            mapa.PokemonsColisão
        )

        flutuacao = math.sin(pygame.time.get_ticks() / 200) * 5

        # mede o texto
        txt_surf = fonte.render(self.Nome, True, (255, 255, 255))
        txt_w, txt_h = txt_surf.get_size()

        # ancora o apelido no centro do player e 8px acima da cabeça
        x_txt = int(corpo_rect.centerx - txt_w // 2)
        y_txt = int(corpo_rect.top - 8 - txt_h + flutuacao)

        texto_com_borda(tela, self.Nome, fonte, (x_txt, y_txt), (255, 255, 255), (0, 0, 0))
    
    def desenhar_bracos(self, tela, centro, cor_braco, angulo_rad, ItensIMG, PokemonsColisão):
        x_centro, y_centro = centro
        tempo = pygame.time.get_ticks()

        distancia_braco = 60
        ciclo_tapa_ms = 700
        tapa_amplitude = 60
        profundidade_amplitude = 4

        def calcular_respiração():
            profundidade = math.sin(tempo / 500) * profundidade_amplitude
            dx = math.cos(angulo_rad) * profundidade
            dy = math.sin(angulo_rad) * profundidade
            return dx, dy

        def calcular_base_braco(offset_lado=1):
            offset_x = math.cos(angulo_rad + offset_lado * math.pi / 2) * distancia_braco
            offset_y = math.sin(angulo_rad + offset_lado * math.pi / 2) * distancia_braco
            return x_centro + offset_x, y_centro + offset_y

        def aplicar_respiração(base, depth):
            return base[0] + depth[0], base[1] + depth[1]

        def calcular_movimento_mao(base):
            estado = self.estado_tapa
            mouse = pygame.mouse.get_pressed()
            tempo_atual = pygame.time.get_ticks()

            mao = self.Inventario[self.Selecionado] if self.Selecionado < len(self.Inventario) else None
            m1_pressionado = mouse[0]
            m2_pressionado = mouse[2]

            mx, my = pygame.mouse.get_pos()
            dx_mouse = mx - base[0]
            dy_mouse = my - base[1]
            angulo_mouse = math.atan2(dy_mouse, dx_mouse)

            m1_click = m1_pressionado and not self.mouse_anterior[0]
            m2_click = m2_pressionado and not self.mouse_anterior[2]

            # Parâmetros ajustáveis
            cooldown_tapa = 150   # ms
            cooldown_lancar = 1000 # ms

            def acao_tapa():
                if not estado["tapando"]:
                    if m1_pressionado:
                        if tempo_atual - estado["tempo_ultimo_tapa"] >= cooldown_tapa:
                            estado["tapando"] = True
                            estado["inicio_tapa"] = tempo_atual
                            estado["tempo_ultimo_tapa"] = tempo_atual

                if estado["tapando"]:
                    t = (tempo_atual - estado["inicio_tapa"]) / ciclo_tapa_ms
                    if t >= 1:
                        estado["tapando"] = False
                        t = 1

                    movimento = math.sin(t * math.pi)
                    angulo_tapa = angulo_mouse - math.pi / 18
                    dx = math.cos(angulo_tapa) * movimento * tapa_amplitude
                    dy = math.sin(angulo_tapa) * movimento * tapa_amplitude
                    return base[0] + dx, base[1] + dy

                return base

            def acao_mirar():
                dist = math.hypot(dx_mouse, dy_mouse) or 1
                dir_x = dx_mouse / dist
                dir_y = dy_mouse / dist

                alcance = 500
                destino_x = int(base[0] + dir_x * alcance)
                destino_y = int(base[1] + dir_y * alcance)
                Fluxo(tela, base[0], base[1], destino_x, destino_y, cor_base=(180, 150, 255))

                movimento = 0.5 + 0.5 * math.sin((tempo_atual % 1000) / 1000 * math.pi)
                offset = -20 * movimento
                dx = math.cos(angulo_mouse) * offset
                dy = math.sin(angulo_mouse) * offset
                self.Mirando = True

                return base[0] + dx, base[1] + dy

            def acao_lancar():
                # Inicializa variáveis que precisam persistir
                if "t_anterior" not in estado:
                    estado["t_anterior"] = 0

                # Início do arremesso
                if not estado["tapando"]:
                    if m1_pressionado:
                        if tempo_atual - estado["tempo_ultimo_tapa"] >= cooldown_lancar:
                            estado["tapando"] = True
                            estado["inicio_tapa"] = tempo_atual
                            estado["tempo_ultimo_tapa"] = tempo_atual

                # Enquanto arremessa
                if estado["tapando"]:
                    t = (tempo_atual - estado["inicio_tapa"]) / (ciclo_tapa_ms // 2)
                    if t >= 1:
                        estado["tapando"] = False
                        t = 1

                    movimento = math.sin(t * math.pi)
                    angulo_lancar = angulo_mouse - math.pi / 18
                    dx = math.cos(angulo_lancar) * movimento * tapa_amplitude
                    dy = math.sin(angulo_lancar) * movimento * tapa_amplitude

                    # Detectar ponto máximo (t cruza 0.5)
                    if estado["t_anterior"] < 0.5 <= t:
                        self.Projeteis.append(Projetil((base[0] + dx, base[1] + dy), self.Loc, self.Inventario[self.Selecionado], ItensIMG[self.Inventario[self.Selecionado]["nome"]], PokemonsColisão))

                    estado["t_anterior"] = t

                    self.Mirando = True
                    return base[0] + dx, base[1] + dy

                return base

           # ======= Lógica principal =======
            if mao:
                m1_acao = mao.get("M1")
                m2_acao = mao.get("M2")
                self.Mirando = False

                # MOUSE 1
                if m1_acao == "Tapa":
                    if m1_pressionado or self.estado_tapa["tapando"]:
                        return acao_tapa()
                elif m1_acao == "Mirar":
                    if m1_pressionado:
                        return acao_mirar()
                elif m1_acao == "Lançar":
                    if m1_pressionado or self.estado_tapa["tapando"]:
                        return acao_lancar()

                # MOUSE 2
                if m2_acao == "Tapa":
                    if m2_pressionado or self.estado_tapa["tapando"]:
                        return acao_tapa()
                elif m2_acao == "Mirar":
                    if m2_pressionado:
                        return acao_mirar()
                elif m2_acao == "Lançar":
                    if m2_pressionado or self.estado_tapa["tapando"]:
                        return acao_lancar()

                return base
            else:
                # sem item na mão
                if m1_pressionado or self.estado_tapa["tapando"]:
                        return acao_tapa()
                else:
                    return base

        def desenhar_item_na_mao(pos_mao):
            item = self.Inventario[self.Selecionado]
            if item != None:
                nome_item = item.get("nome")
                imagem_item = ItensIMG.get(nome_item)
                if imagem_item:
                    imagem_ajustada = pygame.transform.scale(imagem_item, (35, 35))
                    rect_img = imagem_ajustada.get_rect(center=(int(pos_mao[0]), int(pos_mao[1])))
                    tela.blit(imagem_ajustada, rect_img.topleft)

        # ===== APLICAÇÃO =====
        depth = calcular_respiração()

        # MÃO DIREITA
        base_dir = aplicar_respiração(calcular_base_braco(offset_lado=1), depth)
        pos_braco_direito = calcular_movimento_mao(base_dir)

        # MÃO ESQUERDA (apenas visual + respiração)
        base_esq = aplicar_respiração(calcular_base_braco(offset_lado=-1), depth)

        # Desenhar braço esquerdo (sem ação)
        pygame.draw.circle(tela, cor_braco, (int(base_esq[0]), int(base_esq[1])), 10)
        cor_borda = escurecer_cor(cor_braco)
        pygame.draw.circle(tela, cor_borda, base_esq, 13)
        pygame.draw.circle(tela, cor_braco, base_esq, 10)

        # Desenhar braço direito
        pygame.draw.circle(tela, cor_braco, (int(pos_braco_direito[0]), int(pos_braco_direito[1])), 10)
        pygame.draw.circle(tela, cor_borda, pos_braco_direito, 13)
        pygame.draw.circle(tela, cor_braco, pos_braco_direito, 10)

        # Item na mão direita
        desenhar_item_na_mao(pos_braco_direito)
        self.mouse_anterior = pygame.mouse.get_pressed()

    def mover(self, delta_time, mapa, parametros):

        if parametros["ModoTeclado"]:
            return

        ObjetosColisão = mapa.ObjetosColisão
        BausColisão = mapa.BausColisão
        PokemonsColisão = mapa.PokemonsColisão

        teclas = pygame.key.get_pressed()
        direcao_x = 0
        direcao_y = 0

        if teclas[pygame.K_w]:
            direcao_y -= 1
        if teclas[pygame.K_s]:
            direcao_y += 1
        if teclas[pygame.K_a]:
            direcao_x -= 1
        if teclas[pygame.K_d]:
            direcao_x += 1

        magnitude = math.hypot(direcao_x, direcao_y)

        if magnitude > 0:
            direcao_x /= magnitude
            direcao_y /= magnitude
            velocidade = (self.Velocidade * 0.5) + 3.5

            # --- deslocamento pretendido (em TILES por frame, como no seu código) ---
            dx = direcao_x * velocidade * delta_time
            dy = direcao_y * velocidade * delta_time

            # --- deslocamento pretendido (em TILES/frame, como no seu código) ---
            dx = direcao_x * velocidade * delta_time
            dy = direcao_y * velocidade * delta_time

            # >>> NOVO: aplicar o campo sobre o RETÂNGULO PREVISTO (antes do resolve por eixo)
            tmp_rect = self.rect.copy()
            tmp_rect.centerx += int(round(dx * self.tile))
            tmp_rect.centery += int(round(dy * self.tile))

            for estrutura in ObjetosColisão.values():
                # usa o retângulo previsto do player para checar a zona (mais preciso)
                dx, dy = estrutura.aplicar_campo_forca(
                    tmp_rect,            # rect previsto do player (TELA)
                    (dx, dy),            # movimento em TILES/frame
                    self.tile,           # px por tile
                    delta_time
                )

            # ====== depois segue igual ao seu fluxo atual ======
            # EIXO X
            nova_pos_tela_x = self.rect.centerx + dx * self.tile
            novo_rect_x = self.rect.copy()
            novo_rect_x.centerx = nova_pos_tela_x

            self.ColideComPokemons(PokemonsColisão, parametros)
            self.ColideComBaus(novo_rect_x, BausColisão, parametros)
            colidiu_x = False
            for estrutura in ObjetosColisão.values():
                if estrutura.verifica_colisao_player(novo_rect_x):
                    colidiu_x = True
                    break

            if not colidiu_x:
                self.Loc[0] += dx
                if dx != 0:
                    self.Passos += 0.01

            # EIXO Y
            nova_pos_tela_y = self.rect.centery + dy * self.tile
            novo_rect_y = self.rect.copy()
            novo_rect_y.centery = nova_pos_tela_y

            self.ColideComBaus(novo_rect_y, BausColisão, parametros)
            colidiu_y = False
            for estrutura in ObjetosColisão.values():
                if estrutura.verifica_colisao_player(novo_rect_y):
                    colidiu_y = True
                    break

            if not colidiu_y:
                self.Loc[1] += dy
                if dy != 0:
                    self.Passos += 0.01

    def GanharXp(self, Xp):
        if self.Nivel >= 15:
            return

        self.Xp += Xp

        # loop para subir de nível várias vezes se necessário
        while self.Nivel < 15:
            needed = 100 + int(self.Nivel) * 20
            if self.Xp >= needed:
                self.Xp -= needed
                self.Nivel += 1
                self.Particulas.adicionar_estouro(
                    self.Rect.center, 100, 90,
                    [(255, 182, 193), (199, 21, 133)],
                    duracao_ms=600
                )
            else:
                break

        # se chegou no nível máximo, trava o XP
        if self.Nivel >= 15:
            self.Xp = 0
    
    def ColideComBaus(self, novo_rect, BausColisão, parametros):
        for Bau in BausColisão.values():
            if Bau.rect and novo_rect.colliderect(Bau.rect):
                if Bau.Aberto is False:
                    Bau.AbrirBau(self, parametros)

    def ColideComEstruturas(self, novo_rect, ObjetosColisão):
        for estrutura in ObjetosColisão.values():
            if estrutura.rect and novo_rect.colliderect(estrutura.rect):
                return True
        return False

    def ColideComPokemons(self, PokemonsColisao, parametros):
        for pokemon in PokemonsColisao.values():
            if self.rect.colliderect(pokemon.Rect):
                    parametros["Confronto"]["ConfrontoIniciado"] = True
                    parametros["Confronto"]["BatalhaSimples"] = True
                    parametros["Confronto"]["AlvoConfronto"] = pokemon

    def AdicionarAoInventario(self, item):
        """
        Simples: só aceita dict de item materializado e empilha por nome.
        """
        global ConsumiveisIMG

        if ConsumiveisIMG is None:
            from Codigo.Cenas.Mundo import Consumiveis
            ConsumiveisIMG = Consumiveis

        # sem espaço
        if self.Itens >= self.MaxItens:
            return

        inventario = self.Inventario  # player.Inventario se este método for do player

        # tentar empilhar por nome
        for slot in inventario:
            if slot is not None and slot.get("nome") == item["nome"]:
                slot["numero"] += item.get("numero", 1)
                self.Itens += item.get("numero", 1)
                adicionar_mensagem_item(item["nome"], ConsumiveisIMG)
                return

        # colocar em espaço vazio
        for i in range(len(inventario)):
            if inventario[i] is None:
                inventario[i] = item
                self.Itens += item.get("numero", 1)
                adicionar_mensagem_item(item["nome"], ConsumiveisIMG)
                return

    def ToDicParcial(self):
        return {
            "Nome": self.Nome,
            "Skin": self.SkinNumero,
            "Nivel": self.Nivel,
            "Loc": self.Loc,
            "Velocidade": self.Velocidade,
            "Selecionado": self.Selecionado,
            "Angulo": self.Angulo,
            "ID": self.ID
        }
    
    def ToDicTotal(self):
        return {
            "Nome": self.Nome,
            "Code": self.Code,
            "Skin": self.SkinNumero,
            "Nivel": self.Nivel,
            "Pokemons": self.Pokemons,
            "Inventario": self.Inventario,
            "XP": self.Xp,
            "Ouro": self.Ouro,
            "Velocidade": self.Velocidade,
            "Mochila": self.Mochila,
            "Maestria": self.Maestria,
            "Equipes": self.Equipes,
            "Loc": self.Loc,
            "Selecionado": self.Selecionado,
            "SkinsLiberadas": self.SkinsLiberadas,
            "BatalhasVencidasPVP": self.BatalhasVencidasPVP,
            "BatalhasVencidasBOT": self.BatalhasVencidasBOT,
            "BausAbertos": self.BausAbertos,
            "PokemonsCapturados": self.PokemonsCapturados,
            "TempoDeJogo": self.TempoDeJogo,
            "Passos": self.Passos,
            "ID": self.ID
        }
    