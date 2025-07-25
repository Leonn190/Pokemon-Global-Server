import pygame

from Prefabs.Sonoridade import tocar

def Botao(tela, texto, espaço, cor_normal, cor_borda, cor_passagem,
           acao, Fonte, estado_clique, eventos, grossura=2, tecla_atalho=None,
           mostrar_na_tela=True, som=None, cor_texto=(0, 0, 0)):
    
    x, y, largura, altura = espaço

    mouse = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()

    mouse_sobre = x <= mouse[0] <= x + largura and y <= mouse[1] <= y + altura

    tecla_ativada = False
    if tecla_atalho and eventos:
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key == tecla_atalho:
                tecla_ativada = True

    cor_borda_atual = cor_passagem if mouse_sobre or tecla_ativada else cor_borda

    # --- Início da adaptação para lista de imagens (animação simples) ---
    frames = None
    if isinstance(cor_normal, list) and cor_normal and all(isinstance(f, pygame.Surface) for f in cor_normal):
        frames = cor_normal
        # Inicializa estado se necessário
        if "_frame_index" not in estado_clique:
            estado_clique["_frame_index"] = 0
            estado_clique["_last_time"] = pygame.time.get_ticks()

        agora = pygame.time.get_ticks()
        intervalo = 50  # milissegundos por frame (pode ajustar)

        if mouse_sobre:
            # Atualiza frame se tempo passou
            if agora - estado_clique["_last_time"] > intervalo:
                estado_clique["_frame_index"] = (estado_clique["_frame_index"] + 1) % len(frames)
                estado_clique["_last_time"] = agora
        else:
            # Mouse saiu, volta para frame 0
            estado_clique["_frame_index"] = 0

        # Pega o frame atual para desenhar e escala
        frame_atual = pygame.transform.scale(frames[estado_clique["_frame_index"]], (largura, altura))
        if mostrar_na_tela:
            tela.blit(frame_atual, (x, y))

    else:
        # Se cor_normal for imagem única
        if mostrar_na_tela:
            if isinstance(cor_normal, pygame.Surface):
                imagem = pygame.transform.scale(cor_normal, (largura, altura))
                tela.blit(imagem, (x, y))
            else:
                pygame.draw.rect(tela, cor_normal, (x, y, largura, altura))

    if mostrar_na_tela and not frames:
        pygame.draw.rect(tela, cor_borda_atual, (x, y, largura, altura), grossura)

        if texto:
            texto_render = Fonte.render(texto, True, cor_texto)  # Usa cor_texto aqui
            texto_rect = texto_render.get_rect(center=(x + largura // 2, y + altura // 2))
            tela.blit(texto_render, texto_rect)
    elif mostrar_na_tela and frames:
        # Desenha borda e texto mesmo se animado
        pygame.draw.rect(tela, cor_borda_atual, (x, y, largura, altura), grossura)
        if texto:
            texto_render = Fonte.render(texto, True, cor_texto)  # Usa cor_texto aqui também
            texto_rect = texto_render.get_rect(center=(x + largura // 2, y + altura // 2))
            tela.blit(texto_render, texto_rect)

    if mostrar_na_tela and mouse_sobre and clique[0] == 1 and not estado_clique.get("pressionado", False):
        estado_clique["pressionado"] = True
        if som:
            tocar(som)
        if acao:
            if isinstance(acao, (list, tuple)):
                for func in acao:
                    if callable(func):
                        func()
            elif callable(acao):
                acao()

    if clique[0] == 0:
        estado_clique["pressionado"] = False

    if tecla_ativada and not estado_clique.get("pressionado_tecla", False):
        estado_clique["pressionado_tecla"] = True
        if som:
            tocar(som)
        if acao:
            if isinstance(acao, (list, tuple)):
                for func in acao:
                    if callable(func):
                        func()
            elif callable(acao):
                acao()

    if tecla_atalho and eventos:
        for evento in eventos:
            if evento.type == pygame.KEYUP and evento.key == tecla_atalho:
                estado_clique["pressionado_tecla"] = False

def Botao_Selecao(
    tela, texto, espaço, Fonte,
    cor_fundo, cor_borda_normal,
    cor_borda_esquerda=None, cor_borda_direita=None,
    cor_passagem=None, id_botao=None,
    estado_global=None, eventos=None,
    funcao_esquerdo=None, funcao_direito=None,
    desfazer_esquerdo=None, desfazer_direito=None,
    tecla_esquerda=None, tecla_direita=None,
    grossura=5, som=None,
    branco=False  # NOVO ARGUMENTO
):
    x, y, largura, altura = espaço
    mouse = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()
    mouse_sobre = x <= mouse[0] <= x + largura and y <= mouse[1] <= y + altura

    if "selecionado_esquerdo" not in estado_global:
        estado_global["selecionado_esquerdo"] = None
    if "selecionado_direito" not in estado_global:
        estado_global["selecionado_direito"] = None

    ativado_por_tecla_esq = False
    ativado_por_tecla_dir = False
    if eventos:
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if tecla_esquerda and evento.key == tecla_esquerda:
                    ativado_por_tecla_esq = True
                if tecla_direita and evento.key == tecla_direita:
                    ativado_por_tecla_dir = True

    modo_selecionado = None
    if estado_global["selecionado_esquerdo"] == id_botao:
        modo_selecionado = "esquerdo"
    elif estado_global["selecionado_direito"] == id_botao:
        modo_selecionado = "direito"

    cor_borda_atual = cor_borda_normal
    if modo_selecionado == "esquerdo" and cor_borda_esquerda:
        cor_borda_atual = cor_borda_esquerda
    elif modo_selecionado == "direito" and cor_borda_direita:
        cor_borda_atual = cor_borda_direita
    elif mouse_sobre and cor_passagem:
        cor_borda_atual = cor_passagem

    # Desenhar fundo como imagem ou cor
    if cor_fundo is not None:
        if isinstance(cor_fundo, pygame.Surface):
            imagem_redimensionada = pygame.transform.scale(cor_fundo, (largura, altura))
            tela.blit(imagem_redimensionada, (x, y))
        else:
            pygame.draw.rect(tela, cor_fundo, (x, y, largura, altura))

    pygame.draw.rect(tela, cor_borda_atual, (x, y, largura, altura), grossura)

    cor_texto = (255, 255, 255) if branco else (0, 0, 0)  # NOVA LÓGICA
    texto_render = Fonte.render(texto, True, cor_texto)
    texto_rect = texto_render.get_rect(center=(x + largura // 2, y + altura // 2))
    tela.blit(texto_render, texto_rect)

    def aplicar_selecao(modo):
        if modo == "esquerdo":
            if estado_global["selecionado_esquerdo"] == id_botao:
                if desfazer_esquerdo:
                    desfazer_esquerdo()
                estado_global["selecionado_esquerdo"] = None
            else:
                if estado_global["selecionado_direito"] == id_botao:
                    if desfazer_direito:
                        desfazer_direito()
                    estado_global["selecionado_direito"] = None

                if estado_global["selecionado_esquerdo"] and desfazer_esquerdo:
                    desfazer_esquerdo()
                estado_global["selecionado_esquerdo"] = id_botao
                if funcao_esquerdo:
                    funcao_esquerdo()
                if som:
                    tocar(som)

        elif modo == "direito":
            if estado_global["selecionado_direito"] == id_botao:
                if desfazer_direito:
                    desfazer_direito()
                estado_global["selecionado_direito"] = None
            else:
                if estado_global["selecionado_esquerdo"] == id_botao:
                    if desfazer_esquerdo:
                        desfazer_esquerdo()
                    estado_global["selecionado_esquerdo"] = None

                if estado_global["selecionado_direito"] and desfazer_direito:
                    desfazer_direito()
                estado_global["selecionado_direito"] = id_botao
                if funcao_direito:
                    funcao_direito()
                if som:
                    tocar(som)

    if eventos:
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and mouse_sobre:
                if evento.button == 1 and cor_borda_esquerda:
                    if modo_selecionado == "direito" and desfazer_direito:
                        desfazer_direito()
                        estado_global["selecionado_direito"] = None
                    aplicar_selecao("esquerdo")
                elif evento.button == 3 and cor_borda_direita:
                    if modo_selecionado == "esquerdo" and desfazer_esquerdo:
                        desfazer_esquerdo()
                        estado_global["selecionado_esquerdo"] = None
                    aplicar_selecao("direito")
            elif evento.type == pygame.KEYDOWN:
                if evento.key == tecla_esquerda and cor_borda_esquerda:
                    if modo_selecionado == "direito" and desfazer_direito:
                        desfazer_direito()
                        estado_global["selecionado_direito"] = None
                    aplicar_selecao("esquerdo")
                elif evento.key == tecla_direita and cor_borda_direita:
                    if modo_selecionado == "esquerdo" and desfazer_esquerdo:
                        desfazer_esquerdo()
                        estado_global["selecionado_esquerdo"] = None
                    aplicar_selecao("direito")

def Botao_Alavanca(tela, espaço, fonte, estado, eventos, 
                   valor_atual, valor1, valor2, valor3=None,
                   cor1=(100,100,100), cor2=(150,150,150), cor3=None,
                   cor_passagem=(200,200,200), cor_borda=(0,0,0),
                   texto1="", texto2="", texto3="",
                   som=None, grossura_borda=2):  # nova variável

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    x, y, w, h = espaço
    rect = pygame.Rect(espaço)

    # Verifica se mouse está sobre o botão
    dentro = rect.collidepoint(mouse)
    pygame.draw.rect(tela, cor_borda, rect, width=grossura_borda, border_radius=10)

    # Escolhe cor e texto de acordo com o valor atual
    if valor_atual == valor1:
        cor_fundo = cor1
        texto = texto1
    elif valor_atual == valor2:
        cor_fundo = cor2
        texto = texto2
    elif valor_atual == valor3:
        cor_fundo = cor3 if cor3 else cor2
        texto = texto3
    else:
        cor_fundo = cor1
        texto = texto1

    # Aplica cor de passagem
    if dentro:
        pygame.draw.rect(tela, cor_passagem, rect.inflate(-4, -4), border_radius=8)
    else:
        pygame.draw.rect(tela, cor_fundo, rect.inflate(-4, -4), border_radius=8)

    # Desenha texto
    if texto:
        texto_render = fonte.render(texto, True, (0, 0, 0))
        texto_rect = texto_render.get_rect(center=rect.center)
        tela.blit(texto_render, texto_rect)

    # Detecta clique
    if dentro and click and not estado.get("pressionado", False):
        estado["pressionado"] = True
        if som:
            tocar(som)
        # Alterna valor
        if valor_atual == valor1:
            return valor2
        elif valor_atual == valor2 and valor3 is not None:
            return valor3
        else:
            return valor1
    elif not click:
        estado["pressionado"] = False

    return valor_atual
