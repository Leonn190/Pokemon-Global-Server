from Prefabs.FunçõesPrefabs import Carregar_Imagem, Carregar_Frames

def CarregarTexturas():
    return {
        "AzulRoxa": Carregar_Imagem("Texturas/TexturaAzulRoxa.jpg"),
        "azul": Carregar_Imagem("Texturas/FundoAzul.jpg"),
        "vermelho": Carregar_Imagem("Texturas/FundoVermelho.jpg"),
        "roxo": Carregar_Imagem("Texturas/FundoRoxo.jpg"),
        "amarelo": Carregar_Imagem("Texturas/FundoAmarelo.jpg"),
        "verde": Carregar_Imagem("Texturas/FundoVerde.jpg"),
        "Cosmico": Carregar_Frames("Texturas/TexturaCosmica")
    }

def CarregarFundos():
    return {
        "FundoInicio": Carregar_Imagem("Fundos/FundoInicio.png")
        
    }

def CarregarOutros():
    return {
        "Logo": Carregar_Imagem("Outros/Logo.png",(750,750))
    }