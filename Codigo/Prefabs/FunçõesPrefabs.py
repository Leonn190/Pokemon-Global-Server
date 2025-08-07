import pygame
import pyperclip
import os
import math
from collections import Counter
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
                   tempo_held_backspace=70, limite=0):

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
                conteudo_colado = pyperclip.paste()
                # Aplica limite se existir
                if limite > 0:
                    espaco_disponivel = limite - len(texto_atual)
                    conteudo_colado = conteudo_colado[:espaco_disponivel]
                texto_atual += conteudo_colado
                texto_modificado = True
            elif evento.key == pygame.K_RETURN:
                pass  # Enter ainda não faz nada
            else:
                # Só adiciona se não ultrapassar o limite
                if limite <= 0 or len(texto_atual) < limite:
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

def Slider(tela, nome, x, y, largura, valor, min_val, max_val, cor_base, cor_botao, eventos, Mostragem=None,Mostrar=True):
    # Desenha a linha base
    pygame.draw.line(tela, cor_base, (x, y), (x + largura, y), 13)
    
    # Converte valor para posição
    proporcao = (valor - min_val) / (max_val - min_val)
    pos_botao = x + proporcao * largura
    
    # Desenha o botão do slider
    pygame.draw.circle(tela, cor_botao, (int(pos_botao), y), 20)
    
    if Mostrar:
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

def extrair_cor_predominante(imagem):
    largura, altura = imagem.get_size()
    contador_cores = Counter()

    for y in range(altura):
        for x in range(largura):
            cor = imagem.get_at((x, y))
            if cor.a > 20:  # Ignora pixels transparentes
                contador_cores[(cor.r, cor.g, cor.b)] += 1

    if contador_cores:
        cor_mais_comum = contador_cores.most_common(1)[0][0]
        return pygame.Color(*cor_mais_comum)
    else:
        return pygame.Color("white")

def escurecer_cor(cor, fator=0.8):
    """Retorna uma cor mais escura baseada em um fator."""
    return pygame.Color(int(cor.r * fator), int(cor.g * fator), int(cor.b * fator))

def DesenharPlayer(tela, imagem_corpo, posicao):
    x, y = posicao

    # Extrair uma cor confiável do corpo
    cor_braco = extrair_cor_predominante(imagem_corpo)
    mouse_pos = pygame.mouse.get_pos()

    # Ângulo entre boneco e mouse
    dx, dy = mouse_pos[0] - x, mouse_pos[1] - y
    angulo = math.degrees(math.atan2(dy, dx))
    angulo_correcao = angulo - 90
    angulo_rad = math.radians(angulo)

    # Rotacionar o corpo
    corpo_rotacionado = pygame.transform.rotate(imagem_corpo, -angulo_correcao)
    corpo_rect = corpo_rotacionado.get_rect(center=posicao)
    tela.blit(corpo_rotacionado, corpo_rect)

    # Respiração: movimento para frente e para trás
    t = pygame.time.get_ticks() / 200
    respiracao = math.sin(t) * 4  # amplitude de 3 pixels

    distancia_braco_base = 58
    distancia_braco = distancia_braco_base
    profundidade = respiracao  # movimento ao longo do eixo do ângulo

    # Base dos braços (posição lateral)
    offset_x = math.cos(angulo_rad + math.pi / 2) * distancia_braco
    offset_y = math.sin(angulo_rad + math.pi / 2) * distancia_braco

    # Movimento respiratório (ao longo do corpo)
    depth_x = math.cos(angulo_rad) * profundidade
    depth_y = math.sin(angulo_rad) * profundidade

    pos_braco_esquerdo = (x - offset_x + depth_x, y - offset_y + depth_y)
    pos_braco_direito = (x + offset_x + depth_x, y + offset_y + depth_y)

    cor_borda = escurecer_cor(cor_braco)

    raio = 10
    raio_borda = 13  # ligeiramente maior para formar a borda

    # Desenha os braços com borda
    for pos in [pos_braco_esquerdo, pos_braco_direito]:
        pygame.draw.circle(tela, cor_borda, pos, raio_borda)  # borda
        pygame.draw.circle(tela, cor_braco, pos, raio)        # centro

def Barra(tela, posicao, tamanho, valor_atual, valor_maximo, cor, estado_barra, chave):
    """
    Desenha uma barra com animação suave.

    Args:
        tela: superfície pygame.
        posicao: (x, y) da barra.
        tamanho: (largura, altura).
        valor_atual: valor alvo atual da barra.
        valor_maximo: valor máximo da barra.
        cor: cor principal da barra.
        estado_barra: dicionário para guardar o valor visível atual.
        chave: identificador único da barra (ex: nome ou id).
    """
    x, y = posicao
    largura, altura = tamanho

    # Inicializa o valor visível se ainda não existir
    if chave not in estado_barra:
        estado_barra[chave] = float(valor_atual)

    # Suaviza a transição do valor visível para o atual
    visivel = estado_barra[chave]
    visivel += (valor_atual - visivel) * 0.15  # quanto menor, mais lenta a animação

    # Garante que fique dentro dos limites
    visivel = max(0, min(visivel, valor_maximo))
    estado_barra[chave] = visivel

    # Calcula a proporção da barra preenchida
    proporcao = visivel / valor_maximo if valor_maximo else 0
    largura_preenchida = int(largura * proporcao)

    # Desenha o fundo da barra
    pygame.draw.rect(tela, (50, 50, 50), (x, y, largura, altura))  # fundo cinza escuro

    # Desenha a parte preenchida
    pygame.draw.rect(tela, cor, (x, y, largura_preenchida, altura))

    # Desenha a borda da barra
    pygame.draw.rect(tela, (0, 0, 0), (x, y, largura, altura), 2)

def texto_com_borda(tela, texto, fonte, pos, cor_texto, cor_borda, espessura=2):

    x, y = pos
    texto_surface = fonte.render(texto, True, cor_texto)
    borda_surface = fonte.render(texto, True, cor_borda)

    for dx in range(-espessura, espessura + 1):
        for dy in range(-espessura, espessura + 1):
            if dx == 0 and dy == 0:
                continue
            tela.blit(borda_surface, (x + dx, y + dy))

    tela.blit(texto_surface, (x, y))

def Fluxo(tela, x1, y1, x2, y2, num_pontos=30, frequencia=4, velocidade=3, cor_base=(0, 255, 0), raio=3):

    dx = x2 - x1
    dy = y2 - y1
    dist_total = math.hypot(dx, dy)

    if dist_total == 0:
        return  # Evita divisão por zero

    # Normalizar direção
    dir_x = dx / dist_total
    dir_y = dy / dist_total

    # Tempo atual para animação
    t = pygame.time.get_ticks() / 1000  # em segundos

    for i in range(num_pontos):
        fator = i / num_pontos
        px = int(x1 + dir_x * fator * dist_total)
        py = int(y1 + dir_y * fator * dist_total)

        # Onda de pulsação (vai e volta)
        onda = 0.5 + 0.5 * math.sin(2 * math.pi * frequencia * fator - velocidade * t)

        # Alpha com base na onda
        alpha = int(onda * 255)
        cor = (*cor_base, alpha)

        # Desenhar com alpha
        superficie = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(superficie, cor, (raio, raio), raio)
        tela.blit(superficie, (px - raio, py - raio))
