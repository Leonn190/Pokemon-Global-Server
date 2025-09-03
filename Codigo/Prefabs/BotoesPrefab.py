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
    branco=False,
    Surface=False,
    arredondamento=0,   # <<< 0 = sem canto arredondado; quanto maior, mais arredondado
    Piscante=False,     # <<< piscar a borda (fade entre preto e a cor da borda)
    AlphaTexto=None,    # <<< NOVO: transparência do texto (0..255); None = padrão
):

    x, y, largura, altura = espaço

    # --- helper: aceita callable único OU lista/tupla de callables ---
    def _call_all(fns):
        if fns is None:
            return
        if isinstance(fns, (list, tuple)):
            for f in fns:
                if callable(f):
                    f()
        elif callable(fns):
            fns()

    # --- Se Surface=True e cor_fundo é uma Surface, usar o tamanho real da imagem ---
    using_surface_area = False
    if Surface and isinstance(cor_fundo, pygame.Surface):
        surf_w, surf_h = cor_fundo.get_size()
        largura, altura = surf_w, surf_h
        using_surface_area = True

    # --- input/mouse ---
    mouse = pygame.mouse.get_pos()
    mouse_sobre = (x <= mouse[0] <= x + largura) and (y <= mouse[1] <= y + altura)

    ativado_por_tecla_esq = False
    ativado_por_tecla_dir = False
    if eventos:
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if tecla_esquerda and evento.key == tecla_esquerda:
                    ativado_por_tecla_esq = True
                if tecla_direita and evento.key == tecla_direita:
                    ativado_por_tecla_dir = True

    # --- estado de seleção (mantemos seu estado_global padrão) ---
    if estado_global is not None:
        if "selecionado_esquerdo" not in estado_global:
            estado_global["selecionado_esquerdo"] = None
        if "selecionado_direito" not in estado_global:
            estado_global["selecionado_direito"] = None

    modo_selecionado = None
    if estado_global is not None:
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

    # ------------------------ FUNDO ------------------------
    if cor_fundo is not None:
        if isinstance(cor_fundo, pygame.Surface):
            if using_surface_area:
                tela.blit(cor_fundo, (x, y))
            else:
                img = pygame.transform.scale(cor_fundo, (largura, altura))
                tela.blit(img, (x, y))
        else:
            pygame.draw.rect(
                tela, cor_fundo, (x, y, largura, altura),
                border_radius=max(0, int(arredondamento))
            )

    # ------------------------ BORDA ------------------------
    if grossura and cor_borda_atual:
        # Piscante: fade entre preto e a cor atual da borda (onda triangular suave)
        draw_color = cor_borda_atual
        if Piscante:
            periodo_ms = 900  # velocidade da piscada
            t = pygame.time.get_ticks() % periodo_ms
            fase = t / float(periodo_ms)          # 0..1
            tri  = 1.0 - abs(fase * 2.0 - 1.0)    # 0->1->0 (onda triangular)
            r, g, b = cor_borda_atual
            draw_color = (int(r * tri), int(g * tri), int(b * tri))

        pygame.draw.rect(
            tela, draw_color, (x, y, largura, altura),
            max(1, int(grossura)), border_radius=max(0, int(arredondamento))
        )

    # ------------------------ TEXTO ------------------------
    if texto:
        cor_texto = (255, 255, 255) if branco else (0, 0, 0)
        texto_render = Fonte.render(str(texto), True, cor_texto)

        # >>> NOVO: aplica transparência do texto, se fornecida
        if AlphaTexto is not None:
            try:
                a = int(AlphaTexto)
            except Exception:
                a = 255
            a = max(0, min(255, a))
            # set_alpha define a opacidade global da surface do texto
            texto_render.set_alpha(a)

        texto_rect = texto_render.get_rect(center=(x + largura // 2, y + altura // 2))
        tela.blit(texto_render, texto_rect)

    # ------------------- SELEÇÃO/CALLBACKS -------------------
    def aplicar_selecao(modo):
        if estado_global is None:
            return
        if modo == "esquerdo":
            if estado_global["selecionado_esquerdo"] == id_botao:
                if desfazer_esquerdo: _call_all(desfazer_esquerdo)
                estado_global["selecionado_esquerdo"] = None
            else:
                if estado_global["selecionado_direito"] == id_botao:
                    if desfazer_direito: _call_all(desfazer_direito)
                    estado_global["selecionado_direito"] = None
                if estado_global["selecionado_esquerdo"] and desfazer_esquerdo:
                    _call_all(desfazer_esquerdo)
                estado_global["selecionado_esquerdo"] = id_botao
                if funcao_esquerdo: _call_all(funcao_esquerdo)
                if som: tocar(som)
        elif modo == "direito":
            if estado_global["selecionado_direito"] == id_botao:
                if desfazer_direito: _call_all(desfazer_direito)
                estado_global["selecionado_direito"] = None
            else:
                if estado_global["selecionado_esquerdo"] == id_botao:
                    if desfazer_esquerdo: _call_all(desfazer_esquerdo)
                    estado_global["selecionado_esquerdo"] = None
                if estado_global["selecionado_direito"] and desfazer_direito:
                    _call_all(desfazer_direito)
                estado_global["selecionado_direito"] = id_botao
                if funcao_direito: _call_all(funcao_direito)
                if som: tocar(som)

    if eventos:
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and mouse_sobre:
                if evento.button == 1 and cor_borda_esquerda:
                    if modo_selecionado == "direito" and desfazer_direito and estado_global:
                        _call_all(desfazer_direito)
                        estado_global["selecionado_direito"] = None
                    aplicar_selecao("esquerdo")
                elif evento.button == 3 and cor_borda_direita:
                    if modo_selecionado == "esquerdo" and desfazer_esquerdo and estado_global:
                        _call_all(desfazer_esquerdo)
                        estado_global["selecionado_esquerdo"] = None
                    aplicar_selecao("direito")
            elif evento.type == pygame.KEYDOWN:
                if evento.key == tecla_esquerda and cor_borda_esquerda:
                    if modo_selecionado == "direito" and desfazer_direito and estado_global:
                        _call_all(desfazer_direito)
                        estado_global["selecionado_direito"] = None
                    aplicar_selecao("esquerdo")
                elif evento.key == tecla_direita and cor_borda_direita:
                    if modo_selecionado == "esquerdo" and desfazer_esquerdo and estado_global:
                        _call_all(desfazer_esquerdo)
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

def Botao_invisivel(espaco, acao, clique_duplo=False, intervalo_duplo=300):
    """
    espaco: rect (x,y,l,a) do botão
    acao: função ou lista de funções para executar
    clique_duplo: bool, se True requer clique duplo para ativar
    intervalo_duplo: tempo em ms entre cliques para considerar duplo
    """

    mouse = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()

    rect = pygame.Rect(espaco)

    # Estado interno para clique duplo guardado em atributo da função (static)
    if not hasattr(Botao_invisivel, "_ultimo_click"):
        Botao_invisivel._ultimo_click = {}
    
    agora = pygame.time.get_ticks()  # tempo em ms desde o pygame.init()

    # Usamos a posição do botão como chave para diferenciar botões
    chave = (rect.x, rect.y, rect.w, rect.h)

    if rect.collidepoint(mouse) and clique[0]:
        # Evitar múltiplas execuções no mesmo clique (esperar mouse soltar)
        if not hasattr(Botao_invisivel, "_clicado"):
            Botao_invisivel._clicado = {}
        if Botao_invisivel._clicado.get(chave, False):
            # já foi clicado e ainda está pressionado, ignora
            return
        Botao_invisivel._clicado[chave] = True

        if clique_duplo:
            ultimo = Botao_invisivel._ultimo_click.get(chave, 0)
            if agora - ultimo <= intervalo_duplo:
                # Clique duplo detectado, executa ação
                if callable(acao):
                    acao()
                elif isinstance(acao, list):
                    for func in acao:
                        if callable(func):
                            func()
                # Resetar tempo para evitar triplo clique confuso
                Botao_invisivel._ultimo_click[chave] = 0
            else:
                # Primeiro clique, registra o tempo
                Botao_invisivel._ultimo_click[chave] = agora
        else:
            # Clique simples, executa direto
            if callable(acao):
                acao()
            elif isinstance(acao, list):
                for func in acao:
                    if callable(func):
                        func()

    elif not clique[0]:
        # Quando o botão do mouse soltar, marca que pode aceitar novo clique
        if hasattr(Botao_invisivel, "_clicado"):
            Botao_invisivel._clicado[chave] = False

def Botao_Surface(tela, espaço, surface, acao, eventos):
    """
    Desenha um botão baseado em uma surface.
    - espaço : (x,y,w,h) ou pygame.Rect
    - surface: pygame.Surface a desenhar
    - acao   : função ou lista de funções a executar quando clicado
    - eventos: lista de eventos pygame
    - tela   : surface onde será desenhado
    """
    if not isinstance(espaço, pygame.Rect):
        rect = pygame.Rect(espaço)
    else:
        rect = espaço

    # garante lista de ações
    if not isinstance(acao, (list, tuple)):
        acoes = [acao]
    else:
        acoes = list(acao)

    mouse_pos = pygame.mouse.get_pos()
    mouse_over = rect.collidepoint(mouse_pos)

    # adapta a imagem ao rect
    img = pygame.transform.smoothscale(surface, rect.size).convert_alpha()

    # hover → clareia suavemente sem apagar detalhes
    if mouse_over:
        overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        overlay.fill((40, 40, 40, 0))  # aumenta brilho em R,G,B
        img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # desenha
    if tela:
        tela.blit(img, rect.topleft)

    # eventos
    if eventos:
        for ev in eventos:
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if mouse_over:
                    for f in acoes:
                        if callable(f):
                            f()

