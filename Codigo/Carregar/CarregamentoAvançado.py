import os
from Codigo.Prefabs.FunçõesPrefabs import Carregar_Imagem, Carregar_Frames

def CarregarPokemons():
    pasta = os.path.join("Recursos", "Visual", "Pokemons", "Imagens")
    imagens = {}

    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.lower().endswith(".png"):
            chave = os.path.splitext(nome_arquivo)[0]  # remove .png
            caminho_relativo = os.path.join("Pokemons", "Imagens", nome_arquivo)
            imagem = Carregar_Imagem(caminho_relativo)
            if imagem is not None:
                imagens[chave] = imagem

    return imagens

def CarregarAnimações():
    pasta = os.path.join("Recursos", "Visual", "Pokemons", "Animação")
    dic = {}

    for nome_arquivo in os.listdir(pasta):
            caminho_relativo = os.path.join("Pokemons", "Animação", nome_arquivo)
            frames = Carregar_Frames(caminho_relativo)
            if frames is not None:
                dic[nome_arquivo] = frames  # Mantém com extensão, conforme instruído

    return dic

def CarregarConsumiveis():
    pasta_base = os.path.join("Recursos", "Visual", "Itens", "Consumiveis")
    imagens = {}

    for subpasta in os.listdir(pasta_base):
        caminho_subpasta = os.path.join(pasta_base, subpasta)
        if os.path.isdir(caminho_subpasta):
            for nome_arquivo in os.listdir(caminho_subpasta):
                if nome_arquivo.lower().endswith(".png"):
                    chave = os.path.splitext(nome_arquivo)[0]
                    caminho_relativo = os.path.join("Itens", "Consumiveis", subpasta, nome_arquivo)
                    imagem = Carregar_Imagem(caminho_relativo)
                    if imagem is not None:
                        imagens[chave] = imagem

    return imagens

def CarregarEquipaveis():
    pasta = os.path.join("Recursos", "Visual", "Itens", "Equipaveis")
    imagens = {}

    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.lower().endswith(".png"):
            chave = os.path.splitext(nome_arquivo)[0]
            caminho_relativo = os.path.join("Itens", "Equipaveis", nome_arquivo)
            imagem = Carregar_Imagem(caminho_relativo)
            if imagem is not None:
                imagens[chave] = imagem

    return imagens

def CarregarEstruturasMundo():
    pasta = os.path.join("Recursos", "Visual", "Mapa")
    imagens = {}

    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.lower().endswith(".png"):
            chave = os.path.splitext(nome_arquivo)[0]
            caminho_relativo = os.path.join("Mapa", nome_arquivo)
            imagem = Carregar_Imagem(caminho_relativo)
            if imagem is not None:
                imagens[chave] = imagem

    return imagens

def CarregarOutrasSkins():
    pasta = os.path.join("Recursos", "Visual", "Skins", "Bloqueadas")
    imagens = []

    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.lower().endswith(".png"):
            caminho_relativo = os.path.join("Skins", "Bloqueadas", nome_arquivo)
            imagem = Carregar_Imagem(caminho_relativo)
            if imagem is not None:
                imagens.append(imagem)

    return imagens

def CarregamentoAvançado(info,Pré):

    Pokemons = CarregarPokemons()
    Consumiveis = CarregarConsumiveis()
    Equipaveis = CarregarEquipaveis()
    Estruturas = CarregarEstruturasMundo()

    if Pré:
        Animações = CarregarAnimações()
    else:
        Animações = {}

    Cores, Fontes, Texturas, Fundos, Outros = info["Conteudo"]

    Fundos.update({
        "FundoMundo": Carregar_Imagem("Fundos/FundoMundo.jpg"),
        "FundoSlots": Carregar_Imagem("Fundos/FundoSlots.jpg")
        })
    
    Texturas.update({
        "Madeira": Carregar_Imagem("Texturas/TexturaMadeira.jpg")
    })

    Outros.update({
        "Baus": {
            "Comum": Carregar_Frames("Outros/Bau Comum"),
            "Incomum": Carregar_Frames("Outros/Bau Incomum"),
            "Raro": Carregar_Frames("Outros/Bau Raro"),
            "Epico": Carregar_Frames("Outros/Bau Epico"),
            "Mitico": Carregar_Frames("Outros/Bau Mitico"),
            "Lendario": Carregar_Frames("Outros/Bau Lendario")
        }
    })

    Outros["SkinsTodas"] = Outros["Skins"] + CarregarOutrasSkins()

    info["Conteudo"] = Cores, Fontes, Texturas, Fundos, Outros, Pokemons, Consumiveis, Equipaveis, Estruturas, Animações
    info["Carregado"] = True
