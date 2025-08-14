import pygame
import pyperclip
import os
import time
import math
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

def Barra(tela, posicao, tamanho, valor_atual, valor_maximo, cor, estado_barra, chave, vertical=False):
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

    if not vertical:
        # Barra horizontal: largura proporcional, altura fixa
        largura_preenchida = int(largura * proporcao)

        # Desenha o fundo da barra
        pygame.draw.rect(tela, (50, 50, 50), (x, y, largura, altura))  # fundo cinza escuro

        # Desenha a parte preenchida
        pygame.draw.rect(tela, cor, (x, y, largura_preenchida, altura))

        # Desenha a borda da barra
        pygame.draw.rect(tela, (0, 0, 0), (x, y, largura, altura), 2)
    else:
        # Barra vertical: altura proporcional, largura fixa
        altura_preenchida = int(altura * proporcao)
        y_preenchida = y + (altura - altura_preenchida)  # desenha preenchido de baixo para cima

        # Desenha o fundo da barra
        pygame.draw.rect(tela, (50, 50, 50), (x, y, largura, altura))  # fundo cinza escuro

        # Desenha a parte preenchida
        pygame.draw.rect(tela, cor, (x, y_preenchida, largura, altura_preenchida))

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

def Fluxo(tela, x1, y1, x2, y2, num_pontos=30, frequencia=4, velocidade=3, cor_base=(0, 255, 0), raio=5):

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

def Scrolavel(
    rect,
    eventos,
    lista,
    trechos=False,
    intervalo=1,
    loop=True,
    indice_atual=0,
    sensibilidade=1
):
    n = len(lista)
    if n == 0:
        return ([], 0) if trechos else (None, 0)

    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(rect)
    intervalo = max(1, int(intervalo))
    sensibilidade = max(1, int(sensibilidade))
    eff_sens = sensibilidade if trechos else 1  # só aplica sensibilidade em trechos

    mouse_dentro = rect.collidepoint(pygame.mouse.get_pos())

    delta_base = 0
    wheel_seen = False

    if mouse_dentro:
        # pygame 2: MOUSEWHEEL (ev.y: +1=up, -1=down)
        dy = 0
        for ev in eventos:
            if ev.type == pygame.MOUSEWHEEL:
                dy += ev.y
                wheel_seen = True

        if wheel_seen:
            delta_base = -dy  # down(-1) -> +1 (avança)
        else:
            # fallback: buttons 4/5
            for ev in eventos:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 4:   # up
                        delta_base -= 1
                    elif ev.button == 5: # down
                        delta_base += 1

    delta = delta_base * eff_sens

    if delta != 0:
        novo = indice_atual + delta
        if loop:
            indice_atual = novo % n
        else:
            if trechos:
                # impede passar do último trecho completo
                max_start = max(0, n - intervalo)
                indice_atual = max(0, min(max_start, novo))
            else:
                indice_atual = max(0, min(n - 1, novo))

    if not trechos:
        return (lista[indice_atual], indice_atual)

    if not loop:
        # slice clamped; tamanho pode ser < intervalo se n < intervalo
        start = indice_atual
        end = min(n, start + intervalo)
        return (lista[start:end], indice_atual)
    else:
        trecho = [lista[(indice_atual + k) % n] for k in range(intervalo)]
        return (trecho, indice_atual)

# ---------------- Estado do terminal ----------------
mensagens_terminal = []   # cada item: (texto, cor, timestamp)
ultimo_tempo_msg = 0.0

# Configurações
TERMINAL_LARGURA = 720
TERMINAL_ALTURA  = 300
TERMINO_VISIVEL  = 10.0   # segundos "cheio" de visibilidade
FADE_IN_DUR      = 0.4    # segundos
FADE_OUT_DUR     = 0.6    # segundos
ALPHA_MAX        = 190    # opacidade máxima do fundo (0-255)
MARGEM           = 10

def quebrar_linhas(texto, fonte, largura_max):
    """
    Quebra 'texto' em linhas para caber em 'largura_max' (px), usando 'fonte'.
    Retorna lista de linhas (strings).
    """
    palavras = str(texto).split()
    linhas = []
    atual = ""

    for p in palavras:
        tentativa = p if not atual else (atual + " " + p)
        if fonte.size(tentativa)[0] <= largura_max:
            atual = tentativa
        else:
            if atual:
                linhas.append(atual)
            # Se a palavra sozinha não cabe, quebra forçando
            while fonte.size(p)[0] > largura_max and len(p) > 1:
                # encontra maior prefixo que caiba
                i = len(p)
                while i > 0 and fonte.size(p[:i])[0] > largura_max:
                    i -= 1
                if i <= 0:
                    break
                linhas.append(p[:i])
                p = p[i:]
            atual = p
    if atual:
        linhas.append(atual)
    return linhas

def _alpha_terminal():
 
    if ultimo_tempo_msg <= 0:
        return 0
    t = time.time() - ultimo_tempo_msg
    total = FADE_IN_DUR + TERMINO_VISIVEL + FADE_OUT_DUR

    if t < 0:
        return 0
    if t <= FADE_IN_DUR:  # fade in
        k = t / FADE_IN_DUR
        return int(ALPHA_MAX * k)
    elif t <= FADE_IN_DUR + TERMINO_VISIVEL:  # cheio
        return ALPHA_MAX
    elif t <= total:  # fade out
        k = 1.0 - (t - FADE_IN_DUR - TERMINO_VISIVEL) / FADE_OUT_DUR
        return int(ALPHA_MAX * max(0.0, min(1.0, k)))
    else:
        return 0

def adicionar_mensagem_terminal(msg, cor=(255, 255, 255)):
    """
    Adiciona uma mensagem ao terminal (mantém no máximo 10).
    """
    global ultimo_tempo_msg, mensagens_terminal
    agora = time.time()
    mensagens_terminal.append((str(msg), cor, agora))
    # guarda só as 10 últimas (antigas no topo, novas no fim)
    if len(mensagens_terminal) > 10:
        mensagens_terminal = mensagens_terminal[-10:]
    ultimo_tempo_msg = agora

def terminal(tela, fonte):
    """
    Desenha o terminal em (0,0), 720x300, com fade in/out e quebra de linha.
    Primeira mensagem começa embaixo e sobe conforme novas chegam.
    """
    if not mensagens_terminal:
        return

    alpha_bg = _alpha_terminal()
    if alpha_bg <= 0:
        return

    # Fundo translúcido
    fundo = pygame.Surface((TERMINAL_LARGURA, TERMINAL_ALTURA), pygame.SRCALPHA)
    fundo.fill((0, 0, 0, alpha_bg))
    tela.blit(fundo, (0, 0))

    # Preparar linhas quebradas
    area_texto_w = TERMINAL_LARGURA - 2 * MARGEM
    linha_altura = fonte.get_height() + 4
    max_linhas_visiveis = max(1, (TERMINAL_ALTURA - 2 * MARGEM) // linha_altura)

    # Gera todas as linhas (na ordem das mensagens)
    linhas = []
    for texto, cor, ts in mensagens_terminal:
        for l in quebrar_linhas(texto, fonte, area_texto_w):
            linhas.append((l, cor, ts))

    # Mantém as ÚLTIMAS linhas que cabem (para garantir novas embaixo)
    if len(linhas) > max_linhas_visiveis:
        linhas = linhas[-max_linhas_visiveis:]

    # Alpha também no texto
    alpha_txt = alpha_bg

    # Começa de baixo para cima
    y = TERMINAL_ALTURA - MARGEM - (len(linhas) * linha_altura)
    for l, cor, _ in linhas:
        surf = fonte.render(l, True, cor)
        surf.set_alpha(alpha_txt)
        tela.blit(surf, (MARGEM, y))
        y += linha_altura
