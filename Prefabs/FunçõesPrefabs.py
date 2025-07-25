import pygame
import pyperclip
import os
import re
import sys

def resource_path(relative_path):
    """Garante o caminho correto mesmo quando empacotado em .exe com PyInstaller."""
    try:
        base_path = sys._MEIPASS  # Usado pelo PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def Carregar_Imagem(nome_arquivo, tamanho=None):
    caminho_completo = resource_path(os.path.join("Recursos", "Visual", nome_arquivo))
    extensao = os.path.splitext(nome_arquivo)[1].lower()

    try:
        imagem_original = pygame.image.load(caminho_completo)
        imagem_convertida = (
            imagem_original.convert_alpha() if extensao == ".png"
            else imagem_original.convert()
        )

        if tamanho is not None:
            imagem_convertida = pygame.transform.scale(imagem_convertida, tamanho)

        return imagem_convertida
    except pygame.error as erro:
        print(f"[Erro ao carregar imagem] {nome_arquivo}: {erro}")
        return None

def Carregar_Frames(pasta_relativa):
    def extrair_numero(nome):
        numeros = re.findall(r'\d+', nome)
        return int(numeros[0]) if numeros else -1

    caminho_completo = resource_path(os.path.join("Recursos", "Visual", pasta_relativa))
    
    if not os.path.isdir(caminho_completo):
        print(f"[Erro] Pasta não encontrada: {caminho_completo}")
        return []

    arquivos = [nome for nome in os.listdir(caminho_completo)
                if nome.lower().endswith((".png", ".jpg", ".jpeg"))]
    arquivos.sort(key=extrair_numero)

    frames = []
    for nome in arquivos:
        caminho = os.path.join(caminho_completo, nome)
        try:
            imagem = pygame.image.load(caminho).convert_alpha()
            frames.append(imagem)
        except pygame.error as erro:
            print(f"[Erro ao carregar frame] {nome}: {erro}")
            continue

    return frames

def quebrar_texto(texto, fonte, largura_max):
    palavras = texto.split()
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        teste = linha_atual + " " + palavra if linha_atual else palavra
        if fonte.size(teste)[0] <= largura_max:
            linha_atual = teste
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    return linhas

def Tooltip(area, local, texto, titulo, fonte_texto, fonte_titulo, tela):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    area_rect = pygame.Rect(area)
    local_rect = pygame.Rect(local)

    if not area_rect.collidepoint((mouse_x, mouse_y)):
        return

    # Prepara texto quebrado sem limite artificial de largura
    linhas_texto = quebrar_texto(texto, fonte_texto, local_rect.width - 20)
    altura_texto = fonte_texto.get_height() * len(linhas_texto)

    # Prepara título (sem quebra)
    titulo_render = fonte_titulo.render(titulo, True, (255, 255, 255))
    altura_titulo = titulo_render.get_height()

    # Cria fundo com transparência no tamanho definido por 'local'
    fundo = pygame.Surface((local_rect.width, local_rect.height), pygame.SRCALPHA)
    fundo.fill((0, 0, 0, 200))

    # Desenha o título centralizado horizontalmente no topo
    titulo_rect = titulo_render.get_rect(center=(local_rect.width // 2, altura_titulo // 2 + 5))
    fundo.blit(titulo_render, titulo_rect)

    # Desenha o texto abaixo, centralizado horizontalmente
    y_texto_inicio = altura_titulo + 10
    for i, linha in enumerate(linhas_texto):
        render_linha = fonte_texto.render(linha, True, (255, 255, 255))
        linha_rect = render_linha.get_rect(center=(local_rect.width // 2, y_texto_inicio + fonte_texto.get_height() // 2 + i * fonte_texto.get_height()))
        fundo.blit(render_linha, linha_rect)

    # Blita no local especificado
    tela.blit(fundo, local_rect.topleft)

def Animar(D_inicial,D_final,anima,tempo=200):
    
    if anima is None:
        anima = pygame.time.get_ticks()
    tempo_passado = pygame.time.get_ticks() - anima
    progresso = min(tempo_passado / tempo, 1.0)
    D = int(D_inicial + (D_final - D_inicial) * progresso)

    return D

def Barra_De_Texto(tela, espaço, fonte, cor_fundo, cor_borda, cor_texto,
                   eventos, texto_atual, ao_enviar=None, cor_selecionado=(255, 255, 255), selecionada=False,
                   tempo_held_backspace=70):

    x, y, largura, altura = espaço
    retangulo = pygame.Rect(x, y, largura, altura)

    texto_modificado = False

    # Configuração para apagar com tecla pressionada
    keys = pygame.key.get_pressed()
    tempo_atual = pygame.time.get_ticks()

    # Estado de controle estático da função
    if not hasattr(Barra_De_Texto, "backspace_timer"):
        Barra_De_Texto.backspace_timer = 0
        Barra_De_Texto.backspace_held = False

    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if retangulo.collidepoint(evento.pos):
                selecionada = not selecionada
            else:
                selecionada = False

        if selecionada and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_BACKSPACE:
                texto_atual = texto_atual[:-1]
                texto_modificado = True
                Barra_De_Texto.backspace_timer = tempo_atual
                Barra_De_Texto.backspace_held = True
            elif evento.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                texto_atual += pyperclip.paste()
                texto_modificado = True
            elif evento.key == pygame.K_RETURN:
                pass  # Enter ainda não faz nada
            else:
                texto_atual += evento.unicode
                texto_modificado = True

        if evento.type == pygame.KEYUP and evento.key == pygame.K_BACKSPACE:
            Barra_De_Texto.backspace_held = False

    # Lógica de repetição automática do backspace
    if selecionada and Barra_De_Texto.backspace_held:
        if tempo_atual - Barra_De_Texto.backspace_timer > tempo_held_backspace:
            texto_atual = texto_atual[:-1]
            texto_modificado = True
            Barra_De_Texto.backspace_timer = tempo_atual

    # Chama função de envio, se houver
    if texto_modificado and ao_enviar:
        ao_enviar(texto_atual)

    # Desenho visual
    cor_borda_atual = cor_selecionado if selecionada else cor_borda
    pygame.draw.rect(tela, cor_fundo, retangulo)
    pygame.draw.rect(tela, cor_borda_atual, retangulo, 2)

    texto_surface = fonte.render(str(texto_atual), True, cor_texto)
    tela.blit(texto_surface, (retangulo.x + 10, retangulo.y + (altura - texto_surface.get_height()) // 2))

    return texto_atual, selecionada

def Slider(tela, nome, x, y, largura, valor, min_val, max_val, cor_base, cor_botao, eventos, Mostragem=None):
    # Desenha a linha base
    pygame.draw.line(tela, cor_base, (x, y), (x + largura, y), 13)
    
    # Converte valor para posição
    proporcao = (valor - min_val) / (max_val - min_val)
    pos_botao = x + proporcao * largura
    
    # Desenha o botão do slider
    pygame.draw.circle(tela, cor_botao, (int(pos_botao), y), 20)
    
    # Nome e valor
    fonte = pygame.font.SysFont(None, 24)
    if Mostragem == "%":
        texto = fonte.render(f"{nome}: {int(proporcao * 100)}%", True, (0,0,0))
    else:
        texto = fonte.render(f"{nome}: {int(valor)}", True, (0,0,0))
    
    tela.blit(texto, (x + largura + 25, y - 10))

    # Verifica se está arrastando
    mouse = pygame.mouse.get_pos()
    clicando = pygame.mouse.get_pressed()[0]

    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN and abs(mouse[0] - pos_botao) < 20 and abs(mouse[1] - y) < 20:
            Slider.arrastando = nome  # Define qual slider está sendo arrastado
        if evento.type == pygame.MOUSEBUTTONUP:
            Slider.arrastando = None

    if Slider.arrastando == nome and clicando:
        # Atualiza valor com base no mouse
        novo_pos = max(x, min(mouse[0], x + largura))
        nova_proporcao = (novo_pos - x) / largura
        return min_val + nova_proporcao * (max_val - min_val)

    return valor

# Atributo estático para controlar arraste
Slider.arrastando = None
