import pygame
import random
import math
import os
import pandas as pd

from Codigo.Prefabs.FunçõesPrefabs import Carregar_Frames, Carregar_Imagem
from Codigo.Prefabs.Terminal import adicionar_mensagem_terminal
from Codigo.Prefabs.Particulas import adicionar_estouro
from Codigo.Funções.FunçõesConsumiveis import ConsumiveisDic

df = pd.read_csv("Dados/Pokemons.csv")
dfa = pd.read_csv("Dados/Ataques.csv")

berries = [
    "Caxi Berry",
    "Frambo Berry",
    "Simp Berry",
    "Lum Berry",
    "Tomper Berry",
    "Abbajuur Berry",
    "Jujuca Berry",
    "Jungle Berry",
    "Desert Berry",
    "Frozen Berry",
    "Field Berry",
    "Water Berry",
    "Lava Berry",
    "Magic Berry"
]

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

def CarregarPokemon(nome_pokemon, dic):
    """Carrega a imagem de um Pokémon específico, salva no dicionário e retorna a superfície."""
    caminho_relativo = os.path.join("Pokemons", "Imagens", f"{nome_pokemon}.png")
    imagem = Carregar_Imagem(caminho_relativo)
    dic[nome_pokemon] = imagem  # Armazena no dicionário
    return imagem  # Pode retornar None se não encontrar

def CarregarAnimacaoPokemon(nome_pokemon, dic):
    """Carrega a lista de frames de um Pokémon específico, salva no dicionário e retorna."""
    caminho_relativo = os.path.join("Pokemons", "Animação", nome_pokemon)
    frames = Carregar_Frames(caminho_relativo)
    dic[nome_pokemon] = frames  # Armazena no dicionário
    return frames  # Pode retornar None se não encontrar
    
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

def _mult_iv(pokemon, campo):
    """Multiplicador de IV no intervalo [0.8, 1.2]. Usa IV_específico ou IV global (ou 0)."""
    iv_campo = f"IV_{campo}"
    iv_valor = pokemon.get(iv_campo, pokemon.get("IV", 0))
    return 0.8 + (iv_valor / 100.0) * 0.4

def _recalcular_total(pokemon):
    """Mesmo cálculo já usado por você (mantido)."""
    soma_atributos = (
        pokemon.get("Atk", 0) +
        pokemon.get("Def", 0) +
        pokemon.get("SpA", 0) +
        pokemon.get("SpD", 0) +
        pokemon.get("Vel", 0) +
        pokemon.get("Mag", 0) +
        pokemon.get("Per", 0) +
        pokemon.get("Ene", 0) +
        pokemon.get("EnR", 0) * 2 +
        pokemon.get("CrD", 0) * 1.5 +
        pokemon.get("CrC", 0) * 1.5
    )
    total = (
        soma_atributos * 2 +
        pokemon.get("Vida", 0) +
        pokemon.get("Sinergia", 0) * 10 +
        (pokemon.get("Habilidades", 0) + pokemon.get("Equipaveis", 0)) * 20
    )
    pokemon["Total"] = total

def MaterializarPokemon(Dados):
    pokemon = Dados.copy()

    # 1) Congelar bases e aplicar IV no nível 0
    for campo in ["Vida", "Atk", "Def", "SpA", "SpD", "Vel", "Mag", "Per", "Ene", "EnR", "CrD", "CrC"]:
        pokemon[f"{campo}_Base"] = float(pokemon[campo])
        pokemon[campo] = pokemon[f"{campo}_Base"] * _mult_iv(pokemon, campo)

    # 2) Subir até o nível informado (a partir do nível 0)
    nivel_alvo = int(pokemon.get("Nivel", 0))
    pokemon["Nivel"] = 0
    # garante chaves esperadas
    pokemon["XP"] = int(pokemon.get("XP", 0))
    pokemon["Amizade"] = int(pokemon.get("Amizade", 0))

    pokemon["MoveList"] = [None] * 4
    pokemon["Memoria"] = [None] * 8

    pokemon["Build"] = [None] * pokemon["Equipaveis"]

    for _ in range(nivel_alvo):
        SubirNivel(pokemon)

    # 3) Ajustes iniciais que você já fazia
    #    (mantidos; apenas cap de amizade para não passar de 100)
    if "Amizade" in pokemon:
        pokemon["Amizade"] += max(0, random.randint(0, 30) - random.randint(0, pokemon["Nivel"]))
    else:
        pokemon["Amizade"] = max(0, random.randint(0, 30) - random.randint(0, pokemon["Nivel"]))
    pokemon["Amizade"] = min(100, pokemon["Amizade"])

    pokemon["Fruta Favorita"] = random.choice(berries)

    nivel = pokemon.get("Nivel", 0)
    if nivel > 0:
        pokemon["XP"] = random.randint(0, nivel * 10 - 1)
    else:
        pokemon["XP"] = 0
    
    while None in pokemon["MoveList"]:
        dfa["Code"] = pd.to_numeric(dfa["Code"], errors="coerce")
        r = dfa[dfa["Code"].between(1, 451)].sample(1).iloc[0]

        novoataque = {
            "nome": r["Ataque"],
            "tipo": r["Tipo"],
            "custo": r["Custo"],
            "dano": r["Dano"],
            "estilo": r["Estilo"],
            "assertividade": r["Assertividade"],
            "alvo": r["Alvo"],
            "descrição": r["Descrição"],
        }

        for i, mov in enumerate(pokemon["MoveList"]):
            if mov is None:
                pokemon["MoveList"][i] = novoataque
                break  # sai do for e volta pro while, garantindo preencher 1 de cada vez

    # 4) Recalcular Total ao final da materialização
    _recalcular_total(pokemon)
    return pokemon

def SubirNivel(pokemon):
    """Sobe 1 nível:
       - soma 10% da base (com IV) em 2 atributos (par do ciclo)
       - zera XP
       - +1 Amizade em níveis múltiplos de 5 (máx 100)
       - recalcula Total
       Observação: no 100, cada atributo terá recebido 20 * 10% = +200% da base(IV), totalizando 3x.
    """

    PARES_LEVEL_UP = [
        ("Vida", "Mag"),
        ("Atk",  "SpA"),
        ("Def",  "SpD"),
        ("Per",  "Vel"),
        ("EnR",  "Ene"),
    ]
    INCR_PCT = 0.10  # 10% da base (com IV) em cada up
    NIVEL_MAX = 100  # nível máximo

    # trava no nível máx (não muda nada caso já esteja nele)
    if pokemon.get("Nivel", 0) >= NIVEL_MAX:
        return pokemon

    # próximo nível
    nivel_atual = pokemon.get("Nivel", 0) + 1
    pokemon["Nivel"] = nivel_atual

    # quais dois atributos deste nível
    par = PARES_LEVEL_UP[(nivel_atual - 1) % len(PARES_LEVEL_UP)]

    for atributo in par:
        base = pokemon.get(f"{atributo}_Base", 0.0)
        mult = _mult_iv(pokemon, atributo)
        base_iv = base * mult                  # valor base já com IV aplicado
        incremento = base_iv * INCR_PCT        # +10% da base(IV) — incremento linear (não composto)
        pokemon[atributo] = pokemon.get(atributo, 0.0) + incremento

    # XP zera ao subir
    pokemon["XP"] = 0

    # Amizade +1 em níveis múltiplos de 5 (cap 100)
    if nivel_atual % 5 == 0:
        pokemon["Amizade"] = min(100, int(pokemon.get("Amizade", 0)) + 1)

    if random.randint(0, 100) > 75:
        dfa["Code"] = pd.to_numeric(dfa["Code"], errors="coerce")
        r = dfa[dfa["Code"].between(1, 451)].sample(1).iloc[0]

        novoataque = {
            "nome": r["Ataque"],
            "tipo": r["Tipo"],
            "custo": r["Custo"],
            "dano": r["Dano"],
            "estilo": r["Estilo"],
            "assertividade": r["Assertividade"],
            "alvo": r["Alvo"],
            "descrição": r["Descrição"],
        }

        if None in pokemon["MoveList"]:
            for i, mov in enumerate(pokemon["MoveList"]):
                if mov is None:
                    pokemon["MoveList"][i] = novoataque
                    break  # garante que só preenche o primeiro None encontrado
        elif None in pokemon["Memoria"]:
            for i, mov in enumerate(pokemon["Memoria"]):
                if mov is None:
                    pokemon["Memoria"][i] = novoataque
                    break

    # Recalcula o Total após o up
    _recalcular_total(pokemon)
    return pokemon

class Pokemon:
    def __init__(self, Loc, string_dados, extra, Imagens, Animaçoes, Parametros):
        dados = desserializar_pokemon(string_dados)
        self.Dados = dados
        self.Loc = Loc
        self.LocAlvo = Loc
        self.Parametros = Parametros
        self.Apagar = False

        self.animação = Animaçoes.get(self.Dados["Nome"].lower(), CarregarAnimacaoPokemon(self.Dados["Nome"].lower(), Animaçoes))
        self.imagem = self.animação[0]
        self.indice_anim = 0
        self.contador_anim = 0

        self.TamanhoMirando = extra["TamanhoMirando"]
        self.VelocidadeMirando = extra["VelocidadeMirando"] * 100 # graus por frame
        self.Dificuldade = extra["Dificuldade"]
        self.Frutas = extra["Frutas"]
        self.MaxFrutas = extra.get("MaxFrutas", 2)
        self.Tentativas = extra.get("Tentativas", 0)
        self.DocesExtras = extra.get("DocesExtras", 0)
        self.Irritado = extra.get("Irritado", False)
        self.Batalhando = extra.get("Batalhando", False)
        self.Capturado = extra.get("Capturado", False)
        self.Fugiu = extra.get("Fugiu", False)

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

        self.iniciou_fuga = False
        self.alpha = 255
        self.progress_irritado = 0.0
        self.captura_cobriu = False
        self.sumiu_de_vez = False
        self.FimCaptura = False

        self.tempo_anim = 0

    def Atualizar(self, tela, pos, player, delta_time):
        VELOCIDADE_ANIMACAO = 0.03  # tempo em segundos para trocar de frame
        VELOCIDADE_FADE = 220       # alpha/seg para fugir
        VELOCIDADE_COR = 1.5        # velocidade da transição da cor

        if self.sumiu_de_vez or self.FimCaptura:
            return

        if self.LocAlvo != self.Loc:
            self.mover_para_alvo(delta_time)

        # ===== estado base / posição =====
        self.Rect.center = pos

        # ===== animação do sprite =====
        self.tempo_anim += delta_time
        if self.tempo_anim >= VELOCIDADE_ANIMACAO:
            self.indice_anim = (self.indice_anim + 1) % len(self.animação)
            self.tempo_anim = 0

        quadro = self.animação[self.indice_anim]
        ret = quadro.get_rect(center=pos)

        # ===== estados derivados =====
        capturado_ativo = (self.Capturado != False)

        # Fugiu: inicia fade só quando muda de False -> diferente de False
        if not self.iniciou_fuga and self.Fugiu != False:
            self.iniciou_fuga = True

        # Fade em andamento
        if self.iniciou_fuga and not self.sumiu_de_vez:
            self.alpha -= VELOCIDADE_FADE * delta_time
            if self.alpha <= 0:
                self.alpha = 0
                self.sumiu_de_vez = True

        # ===== cor por irritação (interpolação azul -> vermelho) =====
        if self.Irritado:
            self.progress_irritado += VELOCIDADE_COR * delta_time
            if self.progress_irritado > 1.0:
                self.progress_irritado = 1.0
        else:
            self.progress_irritado -= VELOCIDADE_COR * delta_time
            if self.progress_irritado < 0.0:
                self.progress_irritado = 0.0

        cor_azul = (173, 216, 230)
        cor_vermelho = (255, 160, 160)
        t = self.progress_irritado
        cor_fundo = (
            int(cor_azul[0] + (cor_vermelho[0] - cor_azul[0]) * t),
            int(cor_azul[1] + (cor_vermelho[1] - cor_azul[1]) * t),
            int(cor_azul[2] + (cor_vermelho[2] - cor_azul[2]) * t),
        )
        cor_borda = (100, 149, 237)

        # ===== fundo (respeita alpha e captura_cobriu) =====
        if not (capturado_ativo and self.captura_cobriu):
            surf_circ = pygame.Surface((self.raio * 2 + 6, self.raio * 2 + 6), pygame.SRCALPHA)
            centro_local = (surf_circ.get_width() // 2, surf_circ.get_height() // 2)

            pygame.draw.circle(surf_circ, cor_fundo, centro_local, self.raio)
            pygame.draw.circle(surf_circ, cor_borda, centro_local, self.raio, 3)

            if self.alpha < 255:
                surf_circ.set_alpha(int(self.alpha))

            rect_circ = surf_circ.get_rect(center=pos)
            tela.blit(surf_circ, rect_circ)

        # ===== mirando (respeita alpha) =====
        if player.Mirando:
            self.angulo_mirando = (self.angulo_mirando + self.VelocidadeMirando * delta_time) % 360
            surf_rotacionada = pygame.transform.rotate(self.surf_mirando, self.angulo_mirando)
            if self.alpha < 255:
                surf_rotacionada = surf_rotacionada.copy()
                surf_rotacionada.set_alpha(int(self.alpha))
            rot_rect = surf_rotacionada.get_rect(center=pos)
            tela.blit(surf_rotacionada, rot_rect)
            self.MaskMirando = pygame.mask.from_surface(surf_rotacionada)

        # ===== sprite do pokémon (respeita captura_cobriu e alpha) =====
        if not (capturado_ativo and self.captura_cobriu):
            if self.alpha < 255:
                quadro_to_blit = quadro.copy()
                quadro_to_blit.set_alpha(int(self.alpha))
            else:
                quadro_to_blit = quadro
            tela.blit(quadro_to_blit, ret)

        # ===== animação de captura por cima =====
        if capturado_ativo:
            self.AnimacaoCapturar(tela, pos, delta_time)

    def AnimacaoCapturar(self, tela, pos, delta_time):
        cor_inicio = (173, 216, 230)
        cor_fim = (255, 255, 255)

        if not hasattr(self, "captura_progress"):
            self.captura_progress = 0.0
            self.captura_expandindo = True
            self.captura_cobriu = False

        velocidade = 2.5
        if self.captura_expandindo:
            self.captura_progress += velocidade * delta_time
            if self.captura_progress >= 1.0:
                self.captura_progress = 1.0
                self.captura_expandindo = False
                self.captura_cobriu = True
        else:
            self.captura_progress -= velocidade * delta_time
            if self.captura_progress <= 0.0:
                # Fim da animação
                self.captura_progress = 0.0
                self.FimCaptura = True
                return

        cor = (
            int(cor_inicio[0] + (cor_fim[0] - cor_inicio[0]) * self.captura_progress),
            int(cor_inicio[1] + (cor_fim[1] - cor_inicio[1]) * self.captura_progress),
            int(cor_inicio[2] + (cor_fim[2] - cor_inicio[2]) * self.captura_progress),
        )

        raio_max = max(self.Rect.width, self.Rect.height) * 1.2
        raio = max(1, int(raio_max * self.captura_progress))

        pygame.draw.circle(tela, cor, pos, raio)
    
    def mover_para_alvo(self, delta_time):
        # Velocidade máxima de movimento por segundo (exemplo)
        velocidade_mov = getattr(self, "VelocidadeMov", 2.0)  # casas por segundo, ajuste como quiser

        pos_atual = pygame.math.Vector2(self.Loc)
        pos_alvo = pygame.math.Vector2(self.LocAlvo)

        delta = pos_alvo - pos_atual
        distancia = delta.length()

        if distancia < 0.01:
            # Posição próxima o suficiente: encaixa no alvo
            self.Loc = [pos_alvo.x, pos_alvo.y]
        else:
            # Movimento suave em direção ao alvo
            direcao = delta.normalize()
            passo = min(velocidade_mov * delta_time, distancia)
            nova_pos = pos_atual + direcao * passo
            self.Loc = [nova_pos.x, nova_pos.y]
    
    def Frutificar(self, dados, player):

        # if len(self.Frutas) < self.MaxFrutas:
        #     if dados["nome"] not in self.Frutas:
        #         self.Frutas.append(dados["nome"])
        #     else:
        #         return
        # else:
        #     return
        
        adicionar_estouro(self.Loc, 40, 30, [(255, 182, 193),(199, 21, 133)])
        
        ConsumiveisDic[str(dados["nome"])](self, player, dados)

        self.Parametros["PokemonsAtualizar"].append(self.Todic())

    def Capturar(self, dados, player, crit):
        
        DocesIniciais = self.DocesExtras
        DadosIniciais = self.Dados

        self.Tentativas += 1
        dificuldade = self.Dificuldade - player.Maestria * 10
        self.Dificuldade += 5

        chance_inicial = max(0.001, 1 - dificuldade / 200)

        if self.Irritado:
            chance_inicial = 0.001
        if chance_inicial == 0.001:
            self.Irritado = True
        
        Multiplicador = ConsumiveisDic[str(dados["nome"])](self, player, dados, crit)

        chance_final = chance_inicial * Multiplicador

        Capturou = random.random() < chance_final

        if Capturou:
            self.Capturado = 1
            for i, pokemon in enumerate(player.Pokemons):
                if pokemon == None:
                    player.Pokemons[i] = MaterializarPokemon(self.Dados)
                    self.Parametros["PokemonsAtualizar"].append(self.Todic())
                    adicionar_mensagem_terminal(f"Capturou o pokemon com dificuldade de {round(dificuldade)} e chance de {round(chance_final * 100)}%", (0,200,0))
                    player.PokemonsCapturados += 1
                    break
        else:
            self.Dados = DadosIniciais
            self.DocesExtras = DocesIniciais
            self.Parametros["PokemonsAtualizar"].append(self.Todic())
            adicionar_mensagem_terminal(f"Falhou em capturar o pokemon com dificuldade de {round(dificuldade)} e chance de {round(chance_final * 100)}%", (200,0,0))
            
    def Todic(self):
        return {
    "id": self.Dados["ID"],
    "Dados": CompactarPokemon(self.Dados),
    "extra": {
        "TamanhoMirando": self.TamanhoMirando,
        "VelocidadeMirando": self.VelocidadeMirando,
        "Dificuldade": self.Dificuldade,
        "Frutas": self.Frutas,
        "Tentativas": self.Tentativas,
        "MaxFrutas": self.MaxFrutas,
        "DocesExtras": self.DocesExtras,
        "Irritado": self.Irritado,
        "Batalhando": self.Batalhando,
        "Capturado": self.Capturado
    }}
        
