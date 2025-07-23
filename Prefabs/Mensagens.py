import pygame

mensagens_passageiras = []

class MensagemPassageira:
    def __init__(self, mensagem, cor, fonte, posicao, duracao=240, deslocamento=110):
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

def adicionar_mensagem_passageira(mensagens, texto, cor, fonte, posicao, duracao=200, deslocamento=90):
    nova_mensagem = MensagemPassageira(texto, cor, fonte, posicao, duracao, deslocamento)
    mensagens_passageiras.append(nova_mensagem)