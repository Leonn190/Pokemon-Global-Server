import pygame
import random
import math
import pandas as pd

from Server.ServerMundo import RemoverPokemon

df = pd.read_csv("Dados/Pokemons.csv")

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
    "IV_Mag", "IV_Per", "IV_Ene", "IV_EnR", "IV_CrD", "IV_CrC", "ID"
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

def CompactarPokemon(info):
    valores = []
    for campo in CAMPOS_POKEMON:
        valor = info.get(campo, "")
        # Converter para string e substituir vírgulas internas se houver
        valor_str = str(valor).replace(",", ";")  # para não quebrar o csv
        valores.append(valor_str)
    return ",".join(valores)

def criar_pokemon_especifico(nome):
    pokemon = df[df["Nome"] == nome]  # <-- filtrando por nome

    if pokemon.empty:
        return False

    info_serializavel = pokemon.iloc[0].to_dict()

    if info_serializavel['Raridade'] == "-":
        return False

    info_serializavel["Nivel"] = int(random.betavariate(2, 5) * 50)

    info_serializavel["%1"] = max(0, info_serializavel["%1"] - int(random.betavariate(2, 4) * 70))
    info_serializavel["%2"] = max(0, info_serializavel["%2"] - int(random.betavariate(2, 4) * 70))
    info_serializavel["%3"] = max(0, info_serializavel["%3"] - int(random.betavariate(2, 4) * 70))

    P = {0: 1.2, 1: 1.05, 2: 0.9, 3: 0.7}.get(int(info_serializavel["Estagio"]), 1)

    def gerar_valor(base, fator_min, fator_max, P):
        vmin = int(base * fator_min)
        vmax = int(base * fator_max)
        vmax_real = int(vmax * P)
        valor = random.randint(vmin, vmax_real)
        valor = min(valor, int(base * fator_max))
        return valor, vmin, vmax

    atributos = ["Vida", "Atk", "Def", "SpA", "SpD", "Vel",
                 "Mag", "Per", "Ene", "EnR", "CrD", "CrC"]

    ivs = []
    for atributo in atributos:
        base = int(info_serializavel[atributo])
        valor, minimo, maximo = gerar_valor(base, 0.75, 1.25, P)
        iv = ((valor - minimo) / (maximo - minimo)) * 100
        iv = round(iv, 2)
        info_serializavel[atributo] = int(valor)
        info_serializavel[f"IV_{atributo}"] = iv
        ivs.append(iv)

    IV = round(sum(ivs) / len(ivs), 2)
    info_serializavel["IV"] = IV

    soma_atributos = sum([
        info_serializavel["Atk"],
        info_serializavel["Def"],
        info_serializavel["SpA"],
        info_serializavel["SpD"],
        info_serializavel["Vel"],
        info_serializavel["Mag"],
        info_serializavel["Per"],
        info_serializavel["Ene"],
        info_serializavel["EnR"],
        info_serializavel["CrD"],
        info_serializavel["CrC"]
    ])

    total = (
        soma_atributos * 2 +
        info_serializavel["Vida"] +
        info_serializavel.get("Sinergia", 0) * 10 +
        (info_serializavel.get("Habilidades", 0) + info_serializavel.get("Equipaveis", 0)) * 20
    )

    info_serializavel["Total"] = int(total)

    return CompactarPokemon(info_serializavel)

class Pokemon:
    def __init__(self, Loc, string_dados, Imagens, Animaçoes, Parametros):
        dados = desserializar_pokemon(string_dados)
        self.Dados = dados
        self.Loc = Loc
        self.Parametros = Parametros

        self.imagem = Imagens.get(self.Dados["Nome"].lower(), Imagens["pikachu"])
        self.animação = Animaçoes.get(self.Dados["Nome"].lower(), Animaçoes["pikachu"])
        self.indice_anim = 0
        self.contador_anim = 0

        self.TamanhoMirando = random.randint(10, 40)  # % da volta completa
        self.VelocidadeMirando = random.randint(2, 6)  # graus por frame
        self.Dificuldade = 0
        self.Frutas = 0

        # Criar máscara circular só da borda
        ret = self.imagem.get_rect()
        self.raio = max(ret.width, ret.height) // 2 + 8
        diametro = self.raio * 2

        surf_mask = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        cor_mascara = (255, 255, 255, 255)
        espessura_anel = 3
        pygame.draw.circle(surf_mask, cor_mascara, (self.raio, self.raio), self.raio)
        pygame.draw.circle(surf_mask, (0, 0, 0, 0), (self.raio, self.raio), self.raio - espessura_anel)
        self.Mask = pygame.mask.from_surface(surf_mask)

        # Criar superfície para o fluxo verde giratório
        self.mask_mirando_raio = self.raio + 12
        diam_mirando = self.mask_mirando_raio * 2
        self.surf_mirando = pygame.Surface((diam_mirando, diam_mirando), pygame.SRCALPHA)

        espessura = 4
        rect_arc = pygame.Rect(espessura, espessura, diam_mirando - 2 * espessura, diam_mirando - 2 * espessura)

        arco_graus = 360 * (self.TamanhoMirando / 100)
        arco_radianos = math.radians(arco_graus)
        pygame.draw.arc(self.surf_mirando, (0, 255, 0, 180), rect_arc, 0, arco_radianos, espessura)
        self.MaskMirando = pygame.mask.from_surface(self.surf_mirando)

        self.angulo_mirando = 0

        # --- Rect pré-verificação (quadrado que engloba as duas masks) ---
        maior_raio = max(self.mask_mirando_raio, self.raio)
        diam_max = maior_raio * 2
        self.Rect = pygame.Rect(0, 0, diam_max, diam_max)
        self.Rect.center = (int(self.Loc[0] * 70), int(self.Loc[1] * 70))

    def Atualizar(self, tela, pos, player):
        VELOCIDADE_ANIMACAO = 3

        self.Rect.center = pos

        # Atualiza índice com base no contador
        self.contador_anim += 1
        if self.contador_anim >= VELOCIDADE_ANIMACAO:
            self.indice_anim = (self.indice_anim + 1) % len(self.animação)
            self.contador_anim = 0

        # Pega o quadro atual da animação
        quadro = self.animação[self.indice_anim]
        ret = quadro.get_rect(center=pos)

        # Desenhar o círculo de fundo (atrás do Pokémon)
        cor_fundo = (173, 216, 230)  # azul claro
        cor_borda = (100, 149, 237)  # azul mais escuro (cornflower blue)

        pygame.draw.circle(tela, cor_fundo, pos, self.raio)
        pygame.draw.circle(tela, cor_borda, pos, self.raio, 3)

        # Se player.Mirando for True, desenhar fluxo giratório verde
        if getattr(player, "Mirando", False):
            self.angulo_mirando = (self.angulo_mirando + self.VelocidadeMirando) % 360

            surf_rotacionada = pygame.transform.rotate(self.surf_mirando, self.angulo_mirando)
            rot_rect = surf_rotacionada.get_rect(center=pos)
            tela.blit(surf_rotacionada, rot_rect)

            self.MaskMirando = pygame.mask.from_surface(surf_rotacionada)

        # Desenhar o Pokémon por cima
        tela.blit(quadro, ret)
    
    def Frutificar(self):
        pass

    def Capturar(self, player):
        for i, pokemon in enumerate(player.Pokemons):
            if pokemon == None:
                player.Pokemons[i] = self.Dados
                self.Parametros["PokemonsRemover"].append(self.Dados["ID"])
                break
        
