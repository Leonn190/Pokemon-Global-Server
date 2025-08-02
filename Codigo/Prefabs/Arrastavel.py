import pygame

class Arrastavel:
    def __init__(self, imagem, pos, dados=None, categoria=None, interno=False, funcao_execucao=None):
        self.imagem = imagem
        self.rect = self.imagem.get_rect(topleft=pos)
        self.pos_inicial = pos
        self.arrastando = False
        self.offset = (0, 0)
        self.dados = dados
        self.categoria = categoria
        self.interno = interno
        self.funcao_execucao = funcao_execucao

    def verificar_clique(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.arrastando = True
            mouse_x, mouse_y = mouse_pos
            self.offset = (self.rect.x - mouse_x, self.rect.y - mouse_y)

    def arrastar(self, mouse_pos):
        if self.arrastando:
            mouse_x, mouse_y = mouse_pos
            self.rect.x = mouse_x + self.offset[0]
            self.rect.y = mouse_y + self.offset[1]

    def soltar(self):
        if self.arrastando:
            self.arrastando = False
            if self.funcao_execucao:
                resultado = self.funcao_execucao(
                    self.rect.center,
                    self.dados,
                    self.categoria,
                    self.interno
                )
                if resultado is False:
                    self.rect.topleft = self.pos_inicial

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect.topleft)

    @property
    def esta_arrastando(self):
        return self.arrastando
