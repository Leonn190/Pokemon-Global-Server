import pygame

class Arrastavel:
    def __init__(self, imagem, pos, dados=None, interno=None, funcao_execucao=None):
        self.imagem = imagem
        self.rect = self.imagem.get_rect(topleft=pos)

        self.dados = dados
        self.interno = interno
        self.funcao_execucao = funcao_execucao

        self.esta_arrastando = False
        self.offset_x = 0
        self.offset_y = 0

        self.posicao_original = self.rect.topleft  # nova linha

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect.topleft)

    def arrastar(self, mouse_pos):
        if self.esta_arrastando:
            self.rect.topleft = (mouse_pos[0] + self.offset_x, mouse_pos[1] + self.offset_y)

    def atualizar(self, eventos):
        mouse_pos = pygame.mouse.get_pos()

        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.rect.collidepoint(mouse_pos):
                    self.esta_arrastando = True
                    self.offset_x = self.rect.x - mouse_pos[0]
                    self.offset_y = self.rect.y - mouse_pos[1]
                    self.posicao_original = self.rect.topleft  # salva antes de arrastar

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if self.esta_arrastando:
                    self.esta_arrastando = False
                    sucesso = True
                    if self.funcao_execucao:
                        sucesso = self.funcao_execucao(mouse_pos, self.dados, self.interno)

                    # Se não deu certo, volta pra posição original
                    if sucesso is False:
                        self.rect.topleft = self.posicao_original
