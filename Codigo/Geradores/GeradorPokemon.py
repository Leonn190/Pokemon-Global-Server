
CAMPOS_POKEMON = [
    "Nome",
    "Vida", "Atk", "Def", "SpA", "SpD", "Vel",
    "Mag", "Per", "Ene", "EnR", "CrD", "CrC",
    "Sinergia", "Habilidades", "Equipaveis", "Total",
    "Poder R1", "Poder R2", "Poder R3",
    "Tipo1", "%1", "Tipo2", "%2", "Tipo3", "%3",
    "Altura", "Peso", "Raridade", "Estagio", "FF", "Code",
    "Nivel",
    "IV",
    "IV_Vida", "IV_Atk", "IV_Def", "IV_SpA", "IV_SpD", "IV_Vel",
    "IV_Mag", "IV_Per", "IV_Ene", "IV_EnR", "IV_CrD", "IV_CrC"
]

def desserializar_pokemon(string):
    partes = string.split(",")
    info = {}
    for i, campo in enumerate(CAMPOS_POKEMON):
        if i < len(partes):
            valor = partes[i].replace(";", ",")  # reverter a substituição
            if campo in ["Vida", "Atk", "Def", "SpA", "SpD", "Vel",
                         "Mag", "Per", "Ene", "EnR", "CrD", "CrC",
                         "Sinergia", "Habilidades", "Equipaveis", "Total",
                         "Estagio", "Code", "Nivel"]:
                try:
                    valor = int(valor)
                except:
                    pass
            elif campo in ["Poder R1", "Poder R2", "Poder R3",
                           "%1", "%2", "%3", "Altura", "Peso",
                           "IV", "IV_Vida", "IV_Atk", "IV_Def", "IV_SpA", "IV_SpD", "IV_Vel",
                           "IV_Mag", "IV_Per", "IV_Ene", "IV_EnR", "IV_CrD", "IV_CrC"]:
                try:
                    valor = float(valor)
                except:
                    pass
            info[campo] = valor
    return info

class Pokemon:
    def __init__(self, Loc, string_dados, Imagens, Animaçoes):
        dados = desserializar_pokemon(string_dados)
        for campo, valor in dados.items():
            setattr(self, campo, valor)

        self.Loc = Loc
        self.imagem = Imagens.get(self.Nome.lower(), Imagens["pikachu"])
        self.animação = Animaçoes.get(self.Nome.lower(), Animaçoes["pikachu"])
        self.indice_anim = 0
        self.contador_anim = 0

    def Atualizar(self, tela, pos):
        # Controlar a velocidade da animação (ajuste esse valor como quiser)
        VELOCIDADE_ANIMACAO = 4

        # Atualiza índice com base no contador
        self.contador_anim += 1
        if self.contador_anim >= VELOCIDADE_ANIMACAO:
            self.indice_anim = (self.indice_anim + 1) % len(self.animação)
            self.contador_anim = 0

        # Pega o quadro atual da animação
        quadro = self.animação[self.indice_anim]
        ret = quadro.get_rect(center=pos)
        tela.blit(quadro, ret)

        

