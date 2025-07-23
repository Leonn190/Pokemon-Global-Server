import pygame
import os
import sys

def resource_path(relative_path):
    """Garante o caminho correto mesmo quando empacotado em .exe com PyInstaller."""
    try:
        base_path = sys._MEIPASS  # Usado pelo PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def Carregar_Imagem(nome_arquivo, tamanho):
    caminho_completo = resource_path(nome_arquivo)
    extensao = os.path.splitext(nome_arquivo)[1].lower()

    try:
        imagem_original = pygame.image.load(caminho_completo)
        if extensao == ".png":
            imagem_convertida = imagem_original.convert_alpha()
        else:
            imagem_convertida = imagem_original.convert()
        return pygame.transform.scale(imagem_convertida, tamanho)
    except pygame.error as erro:
        print(f"[Erro ao carregar imagem] {nome_arquivo}: {erro}")
        return None

def Botao(tela, texto, espaço, cor_normal, cor_borda, cor_passagem,
           acao, Fonte, estado_clique, eventos, grossura=2, tecla_atalho=None,
           mostrar_na_tela=True, som=None):

    # Desempacota as dimensões do botão
    x, y, largura, altura = espaço

    # Obtém a posição e o clique atual do mouse
    mouse = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()

    # Verifica se o mouse está sobre o botão
    mouse_sobre = x <= mouse[0] <= x + largura and y <= mouse[1] <= y + altura

    # Verifica se uma tecla de atalho foi pressionada (caso tenha sido definida)
    tecla_ativada = False
    if tecla_atalho and eventos:
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key == tecla_atalho:
                tecla_ativada = True

    # Define a cor da borda: muda se o mouse estiver sobre ou se a tecla foi ativada
    cor_borda_atual = cor_passagem if mouse_sobre or tecla_ativada else cor_borda

    # Desenha o botão na tela (se for permitido)
    if mostrar_na_tela:
        # Se cor_normal for uma imagem (Surface), desenha a imagem no botão
        if isinstance(cor_normal, pygame.Surface):
            imagem = pygame.transform.scale(cor_normal, (largura, altura))
            tela.blit(imagem, (x, y))
        else:
            # Caso contrário, desenha o retângulo do botão
            pygame.draw.rect(tela, cor_normal, (x, y, largura, altura))

        # Desenha a borda do botão
        pygame.draw.rect(tela, cor_borda_atual, (x, y, largura, altura), grossura)

        # Desenha o texto centralizado dentro do botão (se houver texto)
        if texto:
            texto_render = Fonte.render(texto, True, (0, 0, 0))  # Texto preto
            texto_rect = texto_render.get_rect(center=(x + largura // 2, y + altura // 2))
            tela.blit(texto_render, texto_rect)

    # Se o mouse clicou sobre o botão e ainda não estava clicado anteriormente
    if mostrar_na_tela and mouse_sobre and clique[0] == 1 and not estado_clique.get("pressionado", False):
        estado_clique["pressionado"] = True  # Marca que o botão foi pressionado
        if som:
            tocar(som)  # Toca o som do botão
        if acao:
            acao()  # Executa a função atribuída ao botão

    # Reseta o estado de clique se o botão do mouse foi solto
    if clique[0] == 0:
        estado_clique["pressionado"] = False

    # Se a tecla de atalho foi pressionada e ainda não registrada
    if tecla_ativada and not estado_clique.get("pressionado_tecla", False):
        estado_clique["pressionado_tecla"] = True
        if som:
            tocar(som)
        if acao:
            acao()

    # Reseta o estado da tecla quando for solta
    if tecla_atalho and eventos:
        for evento in eventos:
            if evento.type == pygame.KEYUP and evento.key == tecla_atalho:
                estado_clique["pressionado_tecla"] = False

def Botao_Selecao(
    tela, espaço, texto, Fonte,
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
