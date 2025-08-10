import pygame

from Codigo.Prefabs.Sonoridade import tocar

def Botao(tela, texto, espaço, cor_normal, cor_borda, cor_passagem,
           acao, Fonte, estado_clique, eventos, grossura=2, tecla_atalho=None,
           mostrar_na_tela=True, som=None, cor_texto=(0, 0, 0), aumento=None):
    
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

    # ---------- AUMENTO DE TAMANHO SUAVE ----------
    escalar = 1.0
    if aumento:
        if "_escala" not in estado_clique:
            estado_clique["_escala"] = 1.0
        alvo = aumento if mouse_sobre else 1.0
        velocidade_escala = 0.01  # ajuste a suavidade aqui
        atual = estado_clique["_escala"]
        if abs(atual - alvo) > 0.01:
            atual += velocidade_escala if atual < alvo else -velocidade_escala
            atual = max(min(atual, aumento), 1.0)
            estado_clique["_escala"] = atual
        escalar = estado_clique["_escala"]

    # Ajusta espaço com base na escala
    esc_largura = int(largura * escalar)
    esc_altura = int(altura * escalar)
    esc_x = x - (esc_largura - largura) // 2
    esc_y = y - (esc_altura - altura) // 2

    # --- Animação com imagens ---
    frames = None
    if isinstance(cor_normal, list) and cor_normal and all(isinstance(f, pygame.Surface) for f in cor_normal):
        frames = cor_normal
        if "_frame_index" not in estado_clique:
            estado_clique["_frame_index"] = 0
            estado_clique["_last_time"] = pygame.time.get_ticks()

        agora = pygame.time.get_ticks()
        intervalo = 50
        if mouse_sobre:
            if agora - estado_clique["_last_time"] > intervalo:
                estado_clique["_frame_index"] = (estado_clique["_frame_index"] + 1) % len(frames)
                estado_clique["_last_time"] = agora
        else:
            estado_clique["_frame_index"] = 0

        frame_atual = pygame.transform.scale(frames[estado_clique["_frame_index"]], (esc_largura, esc_altura))
        if mostrar_na_tela:
            tela.blit(frame_atual, (esc_x, esc_y))
    else:
        if mostrar_na_tela:
            if isinstance(cor_normal, pygame.Surface):
                imagem = pygame.transform.scale(cor_normal, (esc_largura, esc_altura))
                tela.blit(imagem, (esc_x, esc_y))
            else:
                pygame.draw.rect(tela, cor_normal, (esc_x, esc_y, esc_largura, esc_altura))

    if mostrar_na_tela and not frames:
        pygame.draw.rect(tela, cor_borda_atual, (esc_x, esc_y, esc_largura, esc_altura), grossura)
        if texto:
            texto_render = Fonte.render(texto, True, cor_texto)
            texto_rect = texto_render.get_rect(center=(esc_x + esc_largura // 2, esc_y + esc_altura // 2))
            tela.blit(texto_render, texto_rect)
    elif mostrar_na_tela and frames:
        pygame.draw.rect(tela, cor_borda_atual, (esc_x, esc_y, esc_largura, esc_altura), grossura)
        if texto:
            texto_render = Fonte.render(texto, True, cor_texto)
            texto_rect = texto_render.get_rect(center=(esc_x + esc_largura // 2, esc_y + esc_altura // 2))
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
                   valor_atual, valores,
                   cores=None, textos=None,
                   cor_passagem=(200, 200, 200), cor_borda=(0, 0, 0),
                   som=None, grossura_borda=2):

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    x, y, w, h = espaço
    rect = pygame.Rect(espaço)

    pygame.draw.rect(tela, cor_borda, rect, width=grossura_borda, border_radius=10)

    # Determina índice do valor atual
    try:
        idx = valores.index(valor_atual)
    except ValueError:
        idx = 0  # se não achar, usa primeiro valor como padrão

    cor_fundo = cores[idx] if cores and idx < len(cores) else (100, 100, 100)
    texto = textos[idx] if textos and idx < len(textos) else ""

    if rect.collidepoint(mouse):
        pygame.draw.rect(tela, cor_passagem, rect.inflate(-4, -4), border_radius=8)
    else:
        pygame.draw.rect(tela, cor_fundo, rect.inflate(-4, -4), border_radius=8)

    if texto:
        texto_render = fonte.render(texto, True, (0, 0, 0))
        texto_rect = texto_render.get_rect(center=rect.center)
        tela.blit(texto_render, texto_rect)

    if rect.collidepoint(mouse) and click and not estado.get("pressionado", False):
        estado["pressionado"] = True
        if som:
            tocar(som)
        proximo_idx = (idx + 1) % len(valores)
        return valores[proximo_idx]
    elif not click:
        estado["pressionado"] = False

    return valor_atual

def Botao_Tecla(tecla, acao):

    keys = pygame.key.get_pressed()
    
    # Dicionário para suportar nomes especiais de teclas
    teclas_especiais = {
        "esc": pygame.K_ESCAPE,
        "space": pygame.K_SPACE,
        "enter": pygame.K_RETURN,
        "tab": pygame.K_TAB,
        "shift": pygame.K_LSHIFT,  # ou RSHIFT se quiser
        "ctrl": pygame.K_LCTRL,    # idem
    }

    tecla_formatada = tecla.strip().lower()
    tecla_codigo = teclas_especiais.get(tecla_formatada, getattr(pygame, f'K_{tecla_formatada}', None))

    if tecla_codigo and keys[tecla_codigo]:
        if callable(acao):
            acao()
        elif isinstance(acao, list):
            for a in acao:
                if callable(a):
                    a()

def Botao_invisivel(espaco, acao):
    mouse = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()

    # Convertendo a tupla em um Rect
    rect = pygame.Rect(espaco)

    if rect.collidepoint(mouse) and clique[0]:
        if callable(acao):
            acao()
        elif isinstance(acao, list):
            for func in acao:
                if callable(func):
                    func()
