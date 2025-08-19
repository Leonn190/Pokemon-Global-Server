import pygame
import pyperclip
import os
import math
import re
import sys
import numpy as np

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

    keys = pygame.key.get_pressed()
    tempo_atual = pygame.time.get_ticks()

    # Estado estático (mantém entre chamadas)
    if not hasattr(Barra_De_Texto, "backspace_timer"):
        Barra_De_Texto.backspace_timer = 0
        Barra_De_Texto.backspace_held = False
        Barra_De_Texto.cursor_timer = 0
        Barra_De_Texto.cursor_visivel = True
        Barra_De_Texto.ultimo_input = 0

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
                Barra_De_Texto.ultimo_input = tempo_atual
            elif evento.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                conteudo_colado = pyperclip.paste()
                if limite > 0:
                    espaco_disponivel = limite - len(texto_atual)
                    conteudo_colado = conteudo_colado[:espaco_disponivel]
                texto_atual += conteudo_colado
                texto_modificado = True
                Barra_De_Texto.ultimo_input = tempo_atual
            elif evento.key == pygame.K_RETURN:
                pass
            else:
                if limite <= 0 or len(texto_atual) < limite:
                    texto_atual += evento.unicode
                    texto_modificado = True
                    Barra_De_Texto.ultimo_input = tempo_atual

        if evento.type == pygame.KEYUP and evento.key == pygame.K_BACKSPACE:
            Barra_De_Texto.backspace_held = False

    # Lógica de repetição automática do backspace
    if selecionada and Barra_De_Texto.backspace_held:
        if tempo_atual - Barra_De_Texto.backspace_timer > tempo_held_backspace:
            texto_atual = texto_atual[:-1]
            texto_modificado = True
            Barra_De_Texto.backspace_timer = tempo_atual
            Barra_De_Texto.ultimo_input = tempo_atual

    # Chama função de envio
    if texto_modificado and ao_enviar:
        ao_enviar(texto_atual)

    # --- Cursor piscante ---
    if selecionada:
        if tempo_atual - Barra_De_Texto.ultimo_input > 400:  # começa a piscar depois de 0.4s sem input
            if tempo_atual - Barra_De_Texto.cursor_timer > 500:  # troca estado a cada 0.5s
                Barra_De_Texto.cursor_visivel = not Barra_De_Texto.cursor_visivel
                Barra_De_Texto.cursor_timer = tempo_atual
        else:
            Barra_De_Texto.cursor_visivel = True  # enquanto digita, cursor sempre ligado
            Barra_De_Texto.cursor_timer = tempo_atual

    # --- Desenho ---
    cor_borda_atual = cor_selecionado if selecionada else cor_borda
    pygame.draw.rect(tela, cor_fundo, retangulo)
    pygame.draw.rect(tela, cor_borda_atual, retangulo, 2)

    texto_surface = fonte.render(str(texto_atual), True, cor_texto)
    tela.blit(texto_surface, (retangulo.x + 10, retangulo.y + (altura - texto_surface.get_height()) // 2))

    # Desenha cursor
    if selecionada and Barra_De_Texto.cursor_visivel:
        cursor_x = retangulo.x + 10 + texto_surface.get_width() + 2
        cursor_y = retangulo.y + (altura - texto_surface.get_height()) // 2
        cursor_h = texto_surface.get_height()
        pygame.draw.line(tela, cor_texto, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)

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

def BarraMovel(
    tela, pos, lista, idx, tamanho,
    orientacao="vertical",
    tempo_sem_mudar_ms=3000,
    fade_ms=350
):
    """
    Barra de progresso/rolagem apenas visual.
    - tela: Surface destino.
    - pos: pygame.Rect ou (x, y, largura, altura_inicial). A espessura vem daqui.
    - lista: sequência usada para calcular a posição relativa.
    - idx: índice atual (0..len(lista)-1).
    - tamanho: comprimento da barra (altura se vertical, largura se horizontal).
    - orientacao: "vertical" (padrão) ou "horizontal".
    - tempo_sem_mudar_ms: após esse tempo sem mudar idx, faz fade out.
    - fade_ms: duração do fade in/out.
    """
    if not isinstance(pos, pygame.Rect):
        pos = pygame.Rect(pos)

    # Ajusta apenas o comprimento (grossura permanece a do pos original)
    if orientacao == "vertical":
        pos.height = int(max(1, tamanho))
    else:
        pos.width  = int(max(1, tamanho))

    # --- estado por barra (chaveada por posição + orientação) ---
    now = pygame.time.get_ticks()
    key = (pos.x, pos.y, orientacao)
    states = getattr(BarraMovel, "_states", {})
    st = states.get(key)
    if st is None:
        st = {"last_idx": idx, "last_change": now, "alpha": 0, "last_tick": now}
        states[key] = st
        setattr(BarraMovel, "_states", states)

    # Mudança de índice => fade in
    if idx != st["last_idx"]:
        st["last_idx"] = idx
        st["last_change"] = now

    # Alvo de alpha: 255 se mexeu nos últimos X ms, senão 0
    ativo = (now - st["last_change"]) < tempo_sem_mudar_ms
    alpha_target = 255 if ativo else 0

    # Suavização
    dt = max(0, now - st["last_tick"])
    st["last_tick"] = now
    if fade_ms <= 0:
        st["alpha"] = alpha_target
    else:
        passo = int(255 * (dt / float(fade_ms)))
        if st["alpha"] < alpha_target:
            st["alpha"] = min(255, st["alpha"] + passo)
        elif st["alpha"] > alpha_target:
            st["alpha"] = max(0, st["alpha"] - passo)

    alpha = st["alpha"]
    if alpha <= 0:
        return  # invisível, nada a desenhar

    # --- posição do knob conforme idx ---
    n = max(1, len(lista))
    idx = max(0, min(idx, n - 1))
    progresso = 0.0 if n == 1 else (idx / float(n - 1))

    # Estilo
    cor_trilho = (255, 255, 255, 70)
    cor_knob   = (255, 255, 255, 180)
    track_radius = max(2, min(pos.width, pos.height) // 2)

    # Trilho
    trilho = pygame.Surface((pos.width, pos.height), pygame.SRCALPHA)
    pygame.draw.rect(trilho, cor_trilho, trilho.get_rect(), border_radius=track_radius)
    trilho.set_alpha(alpha)
    tela.blit(trilho, pos.topleft)

    # Knob com tamanho proporcional (comprimento varia, grossura fixa)
    if orientacao == "vertical":
        knob_len_min = 20
        knob_len = max(knob_len_min, int(pos.height / max(3, n)))
        desloc = int((pos.height - knob_len) * progresso)
        knob_rect = pygame.Rect(pos.x, pos.y + desloc, pos.width, knob_len)
    else:
        knob_len_min = 20
        knob_len = max(knob_len_min, int(pos.width / max(3, n)))
        desloc = int((pos.width - knob_len) * progresso)
        knob_rect = pygame.Rect(pos.x + desloc, pos.y, knob_len, pos.height)

    knob = pygame.Surface((knob_rect.width, knob_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(knob, cor_knob, knob.get_rect(), border_radius=track_radius)
    knob.set_alpha(alpha)
    tela.blit(knob, knob_rect.topleft)

def SurfaceAtaque(novoataque, fontes, icones, main=False, size=(160, 32)):
    """
    Renderiza a 'pílula' de ataque.
    - Agora recebe apenas `fontes` (lista indexada pelo tamanho: fontes[18], fontes[16], fontes[14], etc).
    - A fonte do NOME é escolhida automaticamente: tenta 18, depois 16, depois 14.
    - main=False: só nome + fundo (largura mínima 155)
    - main=True : nome + bloco de custo/ícone (largura mínima 185)
    - size: (w,h) desejado; se menor que o mínimo para o modo, é forçado.
    """

    # Paleta por tipo (fallback para 'normal')
    TIPO_CORES = {
        "normal":   ((250, 250, 250), (220, 220, 220)),
        "fogo":     ((255, 100, 0),   (200, 0, 0)),
        "agua":     ((0, 150, 255),   (0, 50, 200)),
        "eletrico": ((255, 255, 0),   (255, 150, 0)),
        "planta":   ((50, 200, 50),   (0, 100, 0)),
        "gelo":     ((150, 255, 255), (0, 200, 200)),
        "lutador":  ((255, 140, 40),  (200, 90, 0)),
        "venenoso": ((180, 0, 180),   (100, 0, 100)),
        "terrestre":((200, 150, 50),  (100, 70, 0)),
        "voador":   ((150, 200, 255), (50, 100, 200)),
        "psiquico": ((255, 100, 255), (180, 0, 180)),
        "inseto":   ((150, 200, 50),  (80, 150, 0)),
        "pedra":    ((180, 150, 100), (100, 80, 50)),
        "fantasma": ((100, 50, 150),  (50, 0, 100)),
        "dragao":   ((60, 120, 130),  (0, 70, 80)),
        "sombrio":  ((60, 50, 40),    (20, 15, 10)),
        "metal":    ((180, 180, 200), (100, 100, 120)),
        "fada":     ((255, 180, 220), (230, 120, 170)),
        "sonoro":   ((210, 210, 210), (170, 170, 170)),
        "cosmico":  ((50, 50, 100),   (0, 0, 40)),
    }

    # -------- helpers --------
    def _diagonal_gradient(size, c0, c1):
        """Gradiente do canto inferior-esquerdo (c0) p/ superior-direito (c1)."""
        w, h = size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        x = np.linspace(0.0, 1.0, w, dtype=np.float32)
        y = np.linspace(0.0, 1.0, h, dtype=np.float32)
        X, Y = np.meshgrid(x, y)  # (h,w)
        t = np.clip((X + (1.0 - Y)) * 0.5, 0.0, 1.0)[..., None]  # (h,w,1)
        c0 = np.asarray(c0[:3], dtype=np.float32)
        c1 = np.asarray(c1[:3], dtype=np.float32)
        grad = (c0 * (1.0 - t) + c1 * t).astype(np.uint8)        # (h,w,3)
        arr3 = pygame.surfarray.pixels3d(surf)                   # (w,h,3)
        arr3[...] = grad.swapaxes(0, 1)                          # (h,w,3)->(w,h,3)
        alpha = pygame.surfarray.pixels_alpha(surf)              # (w,h)
        alpha[...] = 255
        del arr3, alpha
        return surf

    def _auto_text_color(rgb):
        r, g, b = rgb
        lumin = 0.2126*r + 0.7152*g + 0.0722*b
        return (0, 0, 0) if lumin > 160 else (255, 255, 255)

    def _get_font(sz_default):
        """Tenta fontes[sz]; se não existir, procura a menor disponível abaixo; se não achar, cai na primeira disponível."""
        try:
            return fontes[sz_default]
        except Exception:
            # procura menor
            for s in range(sz_default-1, -1, -1):
                try:
                    return fontes[s]
                except Exception:
                    continue
            # fallback: primeira fonte válida na lista
            for f in fontes:
                if f:
                    return f
            raise RuntimeError("Lista 'fontes' vazia ou inválida.")

    # -------- dimensões --------
    min_w = 190 if main else 160
    w, h = size
    if w < min_w:
        w = min_w
    radius  = h // 2
    padding = 6

    # -------- fundo --------
    tipo = str(novoataque.get("tipo", "normal")).lower()
    c0, c1 = TIPO_CORES.get(tipo, TIPO_CORES["normal"])
    grad = _diagonal_gradient((w, h), c0, c1)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.blit(grad, (0, 0))

    # cor do nome por contraste (amostra esquerda)
    sample_x = int(w * 0.25)
    sample_y = h // 2
    text_color = _auto_text_color(grad.get_at((sample_x, sample_y))[:3])

    # -------- dados básicos --------
    nome = str(novoataque.get("nome", ""))

    # -------- bloco direito (quando main=True) --------
    estilo = str(novoataque.get("estilo", "n")).lower()
    if   estilo == "n": icon = icones.get("CustoFisico")
    elif estilo == "s": icon = icones.get("CustoStatus")
    elif estilo == "e": icon = icones.get("CustoEspecial")
    else:               icon = icones.get("CustoFisico")

    try:
        custo_val = round(float(novoataque.get("custo", 0)))
    except Exception:
        custo_val = 0
    custo_txt   = str(custo_val)

    # Custo usa sempre 14 (ou fallback) — conforme pedido de 1 lista de fontes
    fonte_custo = _get_font(14)
    custo_surf  = fonte_custo.render(custo_txt, True, (230, 230, 230))

    # Ícone levemente menor e **gap um pouco menor que antes**
    icon_side = max(1, int(h * 0.65))   # ~65% da altura
    gap       = 1                       # antes 3 -> agora 2 (reduz "bem pouco")
    right_pad = max(3, padding - 2)

    if main:
        sub_w = padding + icon_side + gap + custo_surf.get_width() + right_pad
        sub_w = int(min(w * 0.5, sub_w))   # bloco mais enxuto (<= 50% da largura)
        sub_x = w - sub_w

        sub = pygame.Surface((sub_w, h), pygame.SRCALPHA)
        pygame.draw.rect(sub, (30, 30, 30, 140), sub.get_rect(), border_radius=radius)
        surf.blit(sub, (sub_x, 0))

        if icon is not None:
            ic = pygame.transform.smoothscale(icon, (icon_side, icon_side))
            ix = sub_x + padding
            iy = (h - icon_side) // 2
            surf.blit(ic, (ix, iy))
            cx = ix + icon_side + gap
        else:
            cx = sub_x + padding

        cy = (h - custo_surf.get_height()) // 2
        surf.blit(custo_surf, (cx, cy))
    else:
        sub_x = w  # sem bloco direito; nome ocupa até o fim

    # -------- escolher fonte do NOME (18 -> 16 -> 14) conforme espaço --------
    max_nome_w = max(0, sub_x - padding - padding)
    for sz in (18, 16, 14):
        fonte_nome_try = _get_font(sz)
        if fonte_nome_try.size(nome)[0] <= max_nome_w:
            fonte_nome = fonte_nome_try
            break
    else:
        fonte_nome = _get_font(14)  # se nenhum coube, fixa 14 e elipsa depois

    nome_surf = fonte_nome.render(nome, True, text_color)

    # -------- render do nome (com ellipsis se necessário) --------
    nome_x = padding
    nome_y = (h - nome_surf.get_height()) // 2
    if nome_surf.get_width() > max_nome_w:
        texto = nome
        while texto and fonte_nome.size(texto + "...")[0] > max_nome_w:
            texto = texto[:-1]
        nome_surf = fonte_nome.render((texto + "...") if texto else "...", True, text_color)

    surf.blit(nome_surf, (nome_x, nome_y))
    return surf
