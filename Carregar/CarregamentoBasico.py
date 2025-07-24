from Prefabs.FunçõesPrefabs import Carregar_Imagem, Carregar_Frames

def CarregarTexturas():
    return {
        "AzulRoxa": Carregar_Imagem("Texturas/TexturaAzulRoxa.jpg")
    }

def CarregarFundos():
    return {
        "FundoInicio": Carregar_Frames("Fundos/FundoInicio")
    }

def CarregarOutros():
    return {
        "Logo": Carregar_Imagem("Outros/Logo.png",(700,700))
    }