import pygame
import pyperclip
import os
import math
import re
import sys
import time
import numpy as np

_tooltip_fades = {}

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

def Barra(tela, posicao, tamanho, valor_atual, valor_maximo, cor, estado_barra, chave,
          vertical=False, variacao=0):
    x, y = posicao
    largura, altura = tamanho

    # estado suave do valor mostrado
    vis_key = f"{chave}__vis"
    if vis_key not in estado_barra:
        estado_barra[vis_key] = float(valor_atual)

    visivel = estado_barra[vis_key]
    visivel += (valor_atual - visivel) * 0.15
    visivel = max(0.0, min(visivel, float(valor_maximo) if valor_maximo else 0.0))
    estado_barra[vis_key] = visivel

    # frações básicas
    frac_cor = (visivel / valor_maximo) if valor_maximo else 0.0
    frac_branco = 0.0
    frac_vazio = 1.0 - frac_cor

    # cálculo do overlay de "barreira" (variacao >= 0)
    if variacao is not None and variacao >= 0:
        total = visivel + variacao
        if valor_maximo > 0:
            if total <= valor_maximo:
                # Cor + Branco + Vazio
                frac_branco = variacao / valor_maximo
                frac_vazio  = 1.0 - (frac_cor + frac_branco)
            else:
                # comprime para caber mantendo proporção cor:branco
                denom = (visivel + variacao) or 1.0
                frac_cor    = (visivel  / denom)
                frac_branco = (variacao / denom)
                # ocupa 100% (sem vazio)
                frac_vazio  = 0.0

    # clamp seguro
    def _clamp01(v): return max(0.0, min(1.0, v))
    frac_cor    = _clamp01(frac_cor)
    frac_branco = _clamp01(frac_branco)
    frac_vazio  = _clamp01(1.0 - (frac_cor + frac_branco))

    # desenhar barra de fundo
    fundo = (50, 50, 50)
    borda = (0, 0, 0)
    pygame.draw.rect(tela, fundo, (x, y, largura, altura))
    pygame.draw.rect(tela, borda, (x, y, largura, altura), 2)

    # helpers p/ desenhar segmentos em ordem: cor -> branco
    def draw_segments_h():
        w_cor    = int(largura * frac_cor)
        w_branco = int(largura * frac_branco)
        if w_cor > 0:
            pygame.draw.rect(tela, cor, (x, y, w_cor, altura))
        if w_branco > 0:
            pygame.draw.rect(tela, (255, 255, 255), (x + w_cor, y, w_branco, altura))

    def draw_segments_v():
        h_cor    = int(altura * frac_cor)
        h_branco = int(altura * frac_branco)
        # desenha de baixo pra cima
        if h_cor > 0:
            pygame.draw.rect(tela, cor, (x, y + altura - h_cor, largura, h_cor))
        if h_branco > 0:
            pygame.draw.rect(tela, (255, 255, 255), (x, y + altura - (h_cor + h_branco), largura, h_branco))

    if not vertical:
        draw_segments_h()
    else:
        draw_segments_v()

    # --- Pisca do desgaste (variacao < 0) ---
    if variacao is not None and variacao < 0 and valor_maximo > 0:
        var_abs = abs(float(variacao))
        frac_pisca_total = var_abs / valor_maximo
        # limitamos o pisca ao preenchido de cor (parte útil)
        if frac_pisca_total > 0:
            # cor do pisca: branco; se o "dano" excederia o que temos (visivel-var_abs < 0), pisca vermelho
            excede = (visivel - var_abs) < 0
            cor_pisca_base = (255, 80, 80) if excede else (255, 255, 255)

            # alpha pulsante (lento)
            t = pygame.time.get_ticks() / 1000.0
            alpha = int(128 + 100 * (0.5 + 0.5 * math.sin(2 * math.pi * 0.8 * t)))  # ~0.8 Hz

            if not vertical:
                w_total    = int(largura * frac_pisca_total)
                w_dispon   = int(largura * frac_cor)  # só pisca na parte preenchida
                w_pisca    = max(0, min(w_total, w_dispon))
                if w_pisca > 0:
                    # pisca encostado na "ponta" direita do preenchido
                    px = x + int(largura * frac_cor) - w_pisca
                    s = pygame.Surface((w_pisca, altura), pygame.SRCALPHA)
                    s.fill((*cor_pisca_base, alpha))
                    tela.blit(s, (px, y))
            else:
                h_total   = int(altura * frac_pisca_total)
                h_dispon  = int(altura * frac_cor)
                h_pisca   = max(0, min(h_total, h_dispon))
                if h_pisca > 0:
                    # pisca encostado no topo do preenchido (parte superior)
                    py = y + (altura - int(altura * frac_cor))
                    s = pygame.Surface((largura, h_pisca), pygame.SRCALPHA)
                    s.fill((*cor_pisca_base, alpha))
                    tela.blit(s, (x, py))
                    
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

def Fluxo(tela, x1, y1, x2, y2,
          Pontos=40, pontos_por_100px=None,
          frequencia=4, velocidade=3,
          cor_base=(0, 255, 0), raio=5, forma="bola",
          translucido=False):

    dx = x2 - x1
    dy = y2 - y1
    dist_total = math.hypot(dx, dy)
    if dist_total == 0:
        return

    # direção normalizada e normal perpendicular
    dir_x = dx / dist_total
    dir_y = dy / dist_total
    nx, ny = -dir_y, dir_x

    # escolhe quantidade de pontos
    if isinstance(pontos_por_100px, (int, float)) and pontos_por_100px > 0:
        num_pontos = max(2, int(pontos_por_100px * (dist_total / 100.0)))
    else:
        num_pontos = max(2, int(Pontos))

    t = pygame.time.get_ticks() / 1000.0

    # helper: rotaciona um vetor (ux,uy) por ângulo (rad)
    def rot(ux, uy, ang):
        ca, sa = math.cos(ang), math.sin(ang)
        return (ux*ca - uy*sa, ux*sa + uy*ca)

    for i in range(num_pontos):
        fator = i / num_pontos
        px = x1 + dir_x * fator * dist_total
        py = y1 + dir_y * fator * dist_total

        # calcula alpha
        if translucido is not False:
            alpha = int(max(0, min(255, translucido)))
        else:
            onda = 0.5 + 0.5 * math.sin(2 * math.pi * frequencia * fator - velocidade * t)
            alpha = int(max(0, min(255, onda * 255)))

        cor = (*cor_base, alpha)

        if forma == "seta":
            # seta sólida com "entalhe" central (como a imagem)
            L = max(10, int(raio * 3.5))   # comprimento ao longo do fluxo
            W = max(6,  int(raio * 3.2))   # espessura total
            entalhe = 0.2                 # quão fundo o recorte entra (0..0.5) do L

            # vetores direção e normal já calculados: (dir_x, dir_y) e (nx, ny)
            # pontos base
            tipx  = px + dir_x * (L/2)
            tipy  = py + dir_y * (L/2)

            backx = px - dir_x * (L/2)
            backy = py - dir_y * (L/2)

            topx  = backx + nx * (W/2)
            topy  = backy + ny * (W/2)

            botx  = backx - nx * (W/2)
            boty  = backy - ny * (W/2)

            # ponto do entalhe (no meio da altura, recuado para dentro)
            notchx = px - dir_x * (L * entalhe)
            notchy = py - dir_y * (L * entalhe)

            # ordem dos vértices: topo-esquerda -> entalhe -> base-inferior -> ponta
            pts = [(topx, topy), (notchx, notchy), (botx, boty), (tipx, tipy)]

            # desenha em surface local com alpha
            minx = int(min(p[0] for p in pts)) - 2
            miny = int(min(p[1] for p in pts)) - 2
            maxx = int(max(p[0] for p in pts)) + 2
            maxy = int(max(p[1] for p in pts)) + 2
            w, h = maxx - minx, maxy - miny

            s = pygame.Surface((w, h), pygame.SRCALPHA)
            pts_local = [(x - minx, y - miny) for (x, y) in pts]
            pygame.draw.polygon(s, cor, pts_local)
            tela.blit(s, (minx, miny))

        else:  # "bola"
            r = int(raio)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, cor, (r, r), r)
            tela.blit(s, (int(px) - r, int(py) - r))   

def Pulso(tela, pos, cor=(0, 255, 0), raio_base=40,
          variacao=0.3, velocidade=2.0, alpha_base=80):
    """
    Desenha um círculo pulsante (expande/contrai) em torno de 'pos'.

    - pos: (x, y) centro do círculo
    - cor: cor base (R,G,B)
    - raio_base: raio médio do pulso
    - variacao: fração do raio que oscila (ex: 0.3 → ±30%)
    - velocidade: velocidade da oscilação (Hz aprox)
    - alpha_base: transparência máxima (0..255)
    """
    t = pygame.time.get_ticks() / 1000.0

    # seno oscilando entre -1..1
    osc = math.sin(2 * math.pi * velocidade * t)

    # raio varia em torno do base
    raio = int(raio_base * (1 + variacao * osc * 0.5))

    # alpha também oscila suavemente (0.5..1.0 do base)
    alpha = int(alpha_base * (0.5 + 0.5 * (osc + 1) / 2))

    # surface auxiliar com canal alpha
    s = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*cor, alpha), (raio, raio), raio)

    tela.blit(s, (pos[0] - raio, pos[1] - raio))

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

def caixa_de_texto(
    tela,
    texto,
    fonte,
    espaco,              # (x, y, largura, altura)
    cor_caixa=(40, 40, 40),
    cor_borda_caixa=(255, 255, 255),
    esp_borda_caixa=2,
    cor_texto=(255, 255, 255),
    cor_borda_texto=(0, 0, 0),
    esp_borda_texto=2,
    raio=0               # arredondamento da caixa (padrão agora é 0)
):
    # garante que espaco seja um rect
    if not isinstance(espaco, pygame.Rect):
        espaco = pygame.Rect(espaco)

    x, y, w, h = espaco

    # desenha em uma surface com alpha (fica bonitinho se quiser transparência)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # fundo e borda da caixa
    pygame.draw.rect(surf, cor_caixa, (0, 0, w, h), border_radius=raio)
    if esp_borda_caixa and cor_borda_caixa is not None:
        pygame.draw.rect(surf, cor_borda_caixa, (0, 0, w, h), esp_borda_caixa, border_radius=raio)

    # centraliza o texto dentro da caixa
    tw, th = fonte.size(str(texto))
    tx = (w - tw) // 2
    ty = (h - th) // 2

    # usa sua função para texto com borda
    texto_com_borda(surf, str(texto), fonte, (tx, ty), cor_texto, cor_borda_texto, esp_borda_texto)

    # manda pra tela
    tela.blit(surf, (x, y))

def Tooltip(
    tela, rect_ctt, rect_hud,
    surface=None,
    texto=None, fonte=None, cor_texto=(255,255,255),
    titulo=None, fonte_titulo=None, cor_titulo=(255,255,0)
):
    global _tooltip_fades

    mouse_pos = pygame.mouse.get_pos()
    hovering = rect_ctt.collidepoint(mouse_pos)

    # chave estável pelo retângulo (id(rect) muda por frame)
    key = (rect_ctt.left, rect_ctt.top, rect_ctt.width, rect_ctt.height)
    if key not in _tooltip_fades:
        _tooltip_fades[key] = {"alpha": 0, "last_hover": False}
    fade = _tooltip_fades[key]

    # alpha sempre translúcido (tooltip)
    MAX_A = 220
    if hovering:
        fade["alpha"] = min(MAX_A, fade["alpha"] + 20)
    else:
        fade["alpha"] = max(0, fade["alpha"] - 30)
    fade["last_hover"] = hovering

    if fade["alpha"] <= 0:
        return

    # converter rect_hud se vier tupla (fallback)
    if isinstance(rect_hud, tuple):
        rect_hud = pygame.Rect(rect_hud[0], rect_hud[1], 200, 80)

    # pré-render do texto e cálculo do box enxuto
    lines = []
    if texto and fonte:
        # quebra natural por "[" (múltiplas linhas)
        for part in str(texto).split("["):
            part = part.strip()
            if part:
                surf = fonte.render(part, True, cor_texto)
                lines.append(surf)

    pad_x, pad_y = 6, 4
    content_w = max((ln.get_width() for ln in lines), default=0)
    content_h = sum((ln.get_height() for ln in lines)) + (len(lines) - 1) * 2  # 2px entre linhas
    box_w = max(rect_hud.width, content_w + 2 * pad_x) if not surface else rect_hud.width
    box_h = max(rect_hud.height, content_h + 2 * pad_y) if not surface else rect_hud.height

    # usamos um "hud_rect" local com largura/altura ajustadas (mantendo topleft)
    hud_rect = pygame.Rect(rect_hud.left, rect_hud.top, box_w, box_h)

    # Surface de fundo
    if not surface:
        surface = pygame.Surface((hud_rect.width, hud_rect.height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, fade["alpha"]))

    # Desenha fundo
    tela.blit(surface, hud_rect.topleft)

    # Desenha título (mantido genérico, mas não vamos usá-lo para atributos)
    y = hud_rect.top + pad_y
    if titulo and fonte_titulo:
        surf_titulo = fonte_titulo.render(titulo, True, cor_titulo)
        x = hud_rect.centerx - surf_titulo.get_width() // 2
        tela.blit(surf_titulo, (x, y))
        y += surf_titulo.get_height() + 2

    # Desenha linhas do texto
    if lines:
        for ln in lines:
            tela.blit(ln, (hud_rect.left + pad_x, y))
            y += ln.get_height() + 2
