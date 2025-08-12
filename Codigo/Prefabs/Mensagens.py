import pygame

mensagens_passageiras = []
fonte_padrao = pygame.font.Font(None, 35)

class MensagemPassageira:
    def __init__(self, mensagem, cor, fonte, posicao, duracao, deslocamento):
        self.mensagem = mensagem
        self.cor = cor
        self.fonte = fonte
        self.posicao_inicial = posicao
        self.duracao = duracao
        self.deslocamento = deslocamento
        self.frame_atual = 0
        self.ativa = True

    def atualizar(self):
        self.frame_atual += 1
        if self.frame_atual >= self.duracao:
            self.ativa = False

    def desenhar(self, tela):
        if not self.ativa:
            return

        alpha = max(0, 255 - int((self.frame_atual / self.duracao) * 255))
        y_offset = int((self.frame_atual / self.duracao) * self.deslocamento)

        # Texto sempre branco
        texto_surface = self.fonte.render(self.mensagem, True, (255, 255, 255))
        texto_surface = texto_surface.convert_alpha()
        texto_surface.set_alpha(alpha)

        largura = texto_surface.get_width() + 20
        altura = texto_surface.get_height() + 10

        # Cria superfície com canal alpha para o fundo + borda
        fundo = pygame.Surface((largura, altura), pygame.SRCALPHA)

        # Borda preta com alpha
        cor_borda = (0, 0, 0, min(255, alpha))
        pygame.draw.rect(fundo, cor_borda, fundo.get_rect(), border_radius=10)

        # Fundo colorido com alpha, um pouco menor para deixar a borda visível
        padding = 2  # espessura da borda
        inner_rect = pygame.Rect(padding, padding, largura - 2 * padding, altura - 2 * padding)
        cor_fundo = (*self.cor, min(200, alpha))
        pygame.draw.rect(fundo, cor_fundo, inner_rect, border_radius=8)

        # Centraliza a caixa na posição inicial
        x, y = self.posicao_inicial
        x_caixa = x - largura // 2
        y_caixa = y - altura // 2 - y_offset

        # Desenha fundo e texto centralizado dentro da caixa
        tela.blit(fundo, (x_caixa, y_caixa))
        tela.blit(texto_surface, (x_caixa + 10, y_caixa + 5))

def adicionar_mensagem_passageira(texto, cor=(0,0,0), fonte=fonte_padrao, posicao=(960,100), duracao=300, deslocamento=90):
    nova_mensagem = MensagemPassageira(texto, cor, fonte, posicao, duracao, deslocamento)
    mensagens_passageiras.append(nova_mensagem)

mensagens_itens = []

class MensagemItemGanho:
    LARGURA = 300
    ALTURA = 60
    PADDING = 10
    DURAÇÃO = 300  # frames
    ESPAÇO_ENTRE_MENSAGENS = 5
    ANIM_FRAMES = 30  # frames da animação de entrada

    def __init__(self, nome_item, imagem_item):
        self.nome = nome_item
        self.imagem = imagem_item
        self.frame_atual = 0
        self.ativa = True

        self.imagem = pygame.transform.scale(self.imagem, (45, 45))
        self.fonte = pygame.font.Font(None, 28)

    def atualizar(self):
        self.frame_atual += 1
        if self.frame_atual >= self.DURAÇÃO:
            self.ativa = False

    def desenhar(self, tela, indice):
        alpha = max(0, 255 - int((self.frame_atual / self.DURAÇÃO) * 255))

        largura = self.LARGURA
        altura = self.ALTURA
        padding = self.PADDING

        y_base = tela.get_height() - altura - 20
        y = y_base - (indice * (altura + self.ESPAÇO_ENTRE_MENSAGENS))

        # posição X fixa final
        x_final = tela.get_width() - largura - 20

        # animação de entrada: deslizando da direita para x_final
        if self.frame_atual < self.ANIM_FRAMES:
            # começa fora da tela à direita (largura da tela)
            x_inicial = tela.get_width()
            # interpola linearmente a posição X do início ao fim durante os frames da animação
            progresso = self.frame_atual / self.ANIM_FRAMES
            x = x_inicial + (x_final - x_inicial) * progresso
        else:
            x = x_final

        # fundo com borda arredondada
        fundo = pygame.Surface((largura, altura), pygame.SRCALPHA)
        cor_borda = (0, 0, 0, alpha)
        cor_fundo = (50, 50, 50, min(200, alpha))
        pygame.draw.rect(fundo, cor_borda, fundo.get_rect(), border_radius=10)
        inner_rect = pygame.Rect(padding, padding, largura - 2 * padding, altura - 2 * padding)
        pygame.draw.rect(fundo, cor_fundo, inner_rect, border_radius=8)

        # texto
        texto = f"x1 {self.nome}"
        texto_surface = self.fonte.render(texto, True, (255, 255, 255))
        texto_surface.set_alpha(alpha)

        # imagem com alpha
        imagem_alpha = self.imagem.copy()
        imagem_alpha.set_alpha(alpha)

        # desenhar na tela
        tela.blit(fundo, (int(x), y))
        tela.blit(imagem_alpha, (int(x) + padding, y + (altura - self.imagem.get_height()) // 2))
        tela.blit(texto_surface, (int(x) + padding + 50, y + (altura - texto_surface.get_height()) // 2))

def adicionar_mensagem_item(nome_item, imagens_dict):
    if nome_item not in imagens_dict:
        print(f"[!] Imagem não encontrada para o item '{nome_item}'")
        return

    imagem = imagens_dict[nome_item]
    nova_mensagem = MensagemItemGanho(nome_item, imagem)
    mensagens_itens.append(nova_mensagem)

def atualizar_e_desenhar_mensagens_itens(tela):
    # remove mensagens inativas
    for msg in mensagens_itens:
        msg.atualizar()
    mensagens_ativas = [msg for msg in mensagens_itens if msg.ativa]

    # redesenha as mensagens empilhadas
    for i, msg in enumerate(reversed(mensagens_ativas)):
        msg.desenhar(tela, i)

    # atualiza a lista principal
    mensagens_itens[:] = mensagens_ativas
