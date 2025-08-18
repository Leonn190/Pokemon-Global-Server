import pygame
import random
import math
import os
import pandas as pd

from Codigo.Prefabs.FunçõesPrefabs import Carregar_Frames, Carregar_Imagem
from Codigo.Prefabs.Terminal import adicionar_mensagem_terminal
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
    def __init__(self, Loc, string_dados, extra, Imagens, Animacoes, Parametros):
        """
        - Capturado e Fugiu: não são True/False; vêm como False ou número (1..30).
          -> número aciona o gatilho da animação (captura/fuga).
        - Movimento: ocorre automaticamente quando LocAlvo != Loc.
        """
        # ---- dados base / referências externas ----
        dados = desserializar_pokemon(string_dados)
        self.Dados = dados
        self.Parametros = Parametros

        # ---- posição em MUNDO ----
        self.Loc = list(Loc)
        self.LocAlvo = list(Loc)  # moverá quando for diferente de Loc

        # ---- flags vindas do 'extra' (mantidas como estão no seu fluxo) ----
        self.Irritado   = bool(extra.get("Irritado", False))
        self.Batalhando = bool(extra.get("Batalhando", False))
        self.Capturado  = extra.get("Capturado", False)  # False ou número (1..30)
        self.Fugiu      = extra.get("Fugiu", False)      # False ou número (1..30)

        # ---- estado interno controlado por máquina de estados ----
        # "vivo" | "capturando" | "fugindo" | "finalizado"
        self.estado = "vivo"
        self.Apagar = False           # quando True, seu gerenciador pode remover
        self.alpha = 255              # fade da fuga
        self.progress_irritado = 0.0  # 0..1 (cor de fundo)
        # captura
        self.captura_progress = 0.0   # 0..1..0
        self.captura_expandindo = True
        self.captura_cobriu = False   # quando True, para de desenhar o sprite

        # ---- animação base do sprite ----
        nome = self.Dados["Nome"].lower()
        self.animacoes = Animacoes
        self.animacao = self.animacoes.get(
            nome, CarregarAnimacaoPokemon(nome, self.animacoes)
        )
        self.indice_anim = 0
        self.tempo_anim  = 0.0
        self.quadro = self.animacao[0]

        # ---- extras (mantidos) ----
        self.TamanhoMirando   = float(extra.get("TamanhoMirando", 30))  # % do arco 0..100
        self.VelocidadeMirando= float(extra.get("VelocidadeMirando", 90.0))  # graus/seg (não por frame)
        self.Dificuldade      = extra.get("Dificuldade")
        self.Frutas           = extra.get("Frutas")
        self.MaxFrutas        = int(extra.get("MaxFrutas", 2))
        self.Tentativas       = int(extra.get("Tentativas", 0))
        self.DocesExtras      = int(extra.get("DocesExtras", 0))

        # ---- máscaras / bounds dependentes do quadro ----
        self._rebuild_bounds_from_frame(self.quadro)
        self._build_mirasurfaces()

        # ---- constantes de tempo ----
        self.VEL_ANIM    = 0.03   # s por frame da animação do sprite
        self.VEL_FADE    = 220.0  # alpha/seg (fuga)
        self.VEL_IRRITA  = 1.5    # 0..1 por segundo (cor irritado)
        self.VEL_CAPTURA = 2.5    # velocidade do ciclo do círculo de captura

        # ---- rotação do arco "Mirando" ----
        self.angulo_mirando = 0.0

        # ---- movimento suave (tiles/seg ou unidades do seu mundo/seg) ----
        self.VelocidadeMov = float(extra.get("VelocidadeMov", 2.0))

    # ============================================================
    # Construção de bounds/máscaras a partir do frame atual
    # ============================================================
    def _rebuild_bounds_from_frame(self, quadro):
        r = quadro.get_rect()
        # raio do disco de fundo com margem
        self.raio = max(r.width, r.height) // 2 + 8
        diam = self.raio * 2

        # máscara circular só da borda (anel)
        surf_mask = pygame.Surface((diam, diam), pygame.SRCALPHA)
        esp = 3
        centro = (self.raio, self.raio)
        pygame.draw.circle(surf_mask, (255,255,255,255), centro, self.raio)
        pygame.draw.circle(surf_mask, (0,0,0,0),      centro, self.raio - esp)
        self.Mask = pygame.mask.from_surface(surf_mask)

        # rect englobando (centrado na tela no uso)
        self.Rect = pygame.Rect(0, 0, diam, diam)

    def _build_mirasurfaces(self):
        # superfície base do arco de mira (antes de rotacionar)
        self.mask_mirando_raio = self.raio + 12
        d = self.mask_mirando_raio * 2
        self.surf_mirando_base = pygame.Surface((d, d), pygame.SRCALPHA)
        esp = 4
        rect_arc = pygame.Rect(esp, esp, d - 2*esp, d - 2*esp)
        arco_graus = max(0.0, min(360.0, 360.0 * (self.TamanhoMirando / 100.0)))
        pygame.draw.arc(self.surf_mirando_base, (0,255,0,180), rect_arc,
                        0, math.radians(arco_graus), esp)
        # máscara será reextraída da superfície rotacionada quando necessário
        self.MaskMirando = pygame.mask.from_surface(self.surf_mirando_base)

    # ============================================================
    # Máquina de estados: detecta transições por GATILHO numérico
    # ============================================================
    def _atualizar_transicoes(self):
        if self.estado in ("finalizado", "capturando", "fugindo"):
            return
        # prioridade: Captura > Fuga
        if self._flag_on(self.Capturado):  # False -> off; número != 0 -> on
            self.estado = "capturando"
            return
        if self._flag_on(self.Fugiu):      # False -> off; número != 0 -> on
            self.estado = "fugindo"

    @staticmethod
    def _flag_on(v):
        """Retorna True quando v é número != 0 ou qualquer valor truthy.
           Mantém False para False/None/0."""
        if v is False or v is None:
            return False
        if isinstance(v, (int, float)):
            return v != 0
        return True

    # ============================================================
    # Loop principal de atualização/desenho
    # ============================================================
    def Atualizar(self, tela, pos_tela, player, delta_time):
        """
        - pos_tela: posição (x,y) em PIXELS onde o Pokémon deve ser desenhado na TELA.
        - player.Mirando: se True, desenha arco giratório e atualiza MaskMirando.
        - Este método NÃO muda LocAlvo; ele apenas move quando Loc != LocAlvo.
        """
        if self.estado == "finalizado":
            return

        # 1) Transições para estados especiais
        self._atualizar_transicoes()

        # 2) Movimento físico no mundo (somente quando LocAlvo != Loc)
        self._mover_para_alvo(delta_time)

        # 3) Animação do sprite base (quadro)
        self.tempo_anim += delta_time
        if self.tempo_anim >= self.VEL_ANIM:
            self.indice_anim = (self.indice_anim + 1) % len(self.animacao)
            self.tempo_anim = 0.0
            self.quadro = self.animacao[self.indice_anim]
            # Se seus frames mudarem MUITO de tamanho, você pode reabrir bounds:
            # self._rebuild_bounds_from_frame(self.quadro)

        # 4) Rect centrado no local de desenho
        ret = self.quadro.get_rect(center=pos_tela)
        self.Rect.center = pos_tela

        # 5) Estados especiais primeiro (retornam após desenhar)
        if self.estado == "capturando":
            if not self.captura_cobriu:
                # antes de cobrir: ainda mostra fundo + sprite
                self._desenhar_fundo(tela, pos_tela)
                self._desenhar_sprite(tela, ret)
            # círculo da captura (expande e depois contrai)
            self._animacao_capturar(tela, pos_tela, delta_time)
            return

        if self.estado == "fugindo":
            # Fade out progressivo de tudo
            self.alpha = max(0, self.alpha - self.VEL_FADE * delta_time)
            if self.alpha <= 0:
                self.estado = "finalizado"
                self.Apagar = True
                return
            a = int(self.alpha)
            self._desenhar_fundo(tela, pos_tela, alpha=a)
            self._desenhar_mirar(tela, pos_tela, player, alpha=a, delta_time=delta_time)
            self._desenhar_sprite(tela, ret, alpha=a)
            return

        # 6) Estado normal (“vivo”): irritação, mira, sprite
        self._atualizar_irritado(delta_time)
        self._desenhar_fundo(tela, pos_tela)
        self._desenhar_mirar(tela, pos_tela, player, delta_time=delta_time)
        self._desenhar_sprite(tela, ret)

    # ============================================================
    # Desenho de cada camada
    # ============================================================
    def _desenhar_fundo(self, tela, pos, alpha=255):
        """Disco de fundo com cor interpolada Azul->Vermelho conforme 'Irritado'."""
        cor_azul = (173, 216, 230)
        cor_verm = (255, 160, 160)
        t = max(0.0, min(1.0, self.progress_irritado))
        cor_fundo = (
            int(cor_azul[0] + (cor_verm[0] - cor_azul[0]) * t),
            int(cor_azul[1] + (cor_verm[1] - cor_azul[1]) * t),
            int(cor_azul[2] + (cor_verm[2] - cor_azul[2]) * t),
        )
        cor_borda = (100, 149, 237)

        surf = pygame.Surface((self.raio*2 + 6, self.raio*2 + 6), pygame.SRCALPHA)
        c = (surf.get_width()//2, surf.get_height()//2)
        pygame.draw.circle(surf, cor_fundo, c, self.raio)
        pygame.draw.circle(surf, cor_borda, c, self.raio, 3)
        if alpha < 255:
            surf.set_alpha(alpha)
        tela.blit(surf, surf.get_rect(center=pos))

    def _desenhar_mirar(self, tela, pos, player, alpha=255, delta_time=0.0):
        """Arco verde giratório quando player.Mirando == True. Atualiza MaskMirando."""
        if not getattr(player, "Mirando", False):
            return
        # rotação suave (graus/seg)
        self.angulo_mirando = (self.angulo_mirando + self.VelocidadeMirando * delta_time) % 360.0
        surf_rot = pygame.transform.rotate(self.surf_mirando_base, self.angulo_mirando)
        if alpha < 255:
            surf_rot = surf_rot.copy()
            surf_rot.set_alpha(alpha)
        tela.blit(surf_rot, surf_rot.get_rect(center=pos))

        # Se você usa checagem de colisão com a mira, atualize a máscara rotacionada:
        self.MaskMirando = pygame.mask.from_surface(surf_rot)

    def _desenhar_sprite(self, tela, ret, alpha=255):
        """Sprite do pokémon (respeita alpha para fuga)."""
        if alpha < 255:
            quadro = self.quadro.copy()
            quadro.set_alpha(alpha)
        else:
            quadro = self.quadro
        tela.blit(quadro, ret)

    # ============================================================
    # Efeitos (irritado, captura)
    # ============================================================
    def _atualizar_irritado(self, dt):
        """Transição de 0..1 (azul->vermelho) enquanto Irritado for True."""
        v = self.VEL_IRRITA * dt
        if self.Irritado:
            self.progress_irritado = min(1.0, self.progress_irritado + v)
        else:
            self.progress_irritado = max(0.0, self.progress_irritado - v)

    def _animacao_capturar(self, tela, pos, dt):
        """
        Expande (0->1) cobrindo o sprite; marca captura_cobriu=True;
        contrai (1->0) e finaliza (estado='finalizado', Apagar=True).
        """
        if self.captura_expandindo:
            self.captura_progress += self.VEL_CAPTURA * dt
            if self.captura_progress >= 1.0:
                self.captura_progress = 1.0
                self.captura_expandindo = False
                self.captura_cobriu = True
        else:
            self.captura_progress -= self.VEL_CAPTURA * dt
            if self.captura_progress <= 0.0:
                # fim do efeito de captura
                self.estado = "finalizado"
                self.Apagar = True
                return

        # cor do círculo (pode ajustar para outro efeito/gradiente)
        cor_ini = (173, 216, 230)
        cor_fim = (255, 255, 255)
        p = self.captura_progress
        cor = (
            int(cor_ini[0] + (cor_fim[0] - cor_ini[0]) * p),
            int(cor_ini[1] + (cor_fim[1] - cor_ini[1]) * p),
            int(cor_ini[2] + (cor_fim[2] - cor_ini[2]) * p),
        )

        # raio proporcional (ligeiramente menor que o bound para aliviar fill)
        raio_max = int(max(self.Rect.width, self.Rect.height) * 0.75)
        raio = max(2, int(raio_max * max(0.05, p)))
        pygame.draw.circle(tela, cor, pos, raio)

    # ============================================================
    # Movimento suave automático (apenas se LocAlvo != Loc)
    # ============================================================
    def _mover_para_alvo(self, dt):
        pos  = pygame.math.Vector2(self.Loc)
        alvo = pygame.math.Vector2(self.LocAlvo)
        delta = alvo - pos
        dist = delta.length()
        if dist < 1e-3:
            # já está no alvo (evita jitter)
            self.Loc = [alvo.x, alvo.y]
            return
        # passo limitado por velocidade
        passo = min(self.VelocidadeMov * dt, dist)
        self.Loc = list(pos + delta.normalize() * passo)
    
    def Frutificar(self, dados, player):

        if len(self.Frutas) < self.MaxFrutas:
            if dados["nome"] not in self.Frutas:
                self.Frutas.append(dados["nome"])
            else:
                return
        else:
            return
        
        player.Particulas.adicionar_estouro(self.Rect.center,round(self.raio * 1.2), 80, [(255, 182, 193),(199, 21, 133)],duracao_ms=600)
        
        ConsumiveisDic[str(dados["nome"])](self, player, dados)

        self.Parametros["PokemonsAtualizar"].append(self.Todic())

    def Capturar(self, dados, player, crit):
        
        DocesIniciais = self.DocesExtras
        DadosIniciais = self.Dados

        self.Tentativas += 1
        dificuldade = self.Dificuldade - player.Maestria * 25
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
        
