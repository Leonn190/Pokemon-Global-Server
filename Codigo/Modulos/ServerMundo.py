import requests

def VerificaçãoSimplesServer(Parametros):
    try:
        url = Parametros["Link"].rstrip('/') + "/Verificar"  # monta a URL completa
        
        payload = {
            "Raio": Parametros.get("Raio", 10),   # define um valor padrão se quiser
            "X": Parametros["Loc"][0],
            "Y": Parametros["Loc"][1],
            "Code": Parametros["Code"]
        }
        
        resposta = requests.post(url, json=payload, timeout=5)
        resposta.raise_for_status()  # levanta exceção para status >=400
        
        dados = resposta.json()
        
        # Atualiza parâmetros com os dados recebidos
        Parametros["GridBiomas"] = dados.get("GridBiomas")
        Parametros["GridObjetos"] = dados.get("GridObjetos")
        Parametros["PlayersProximos"] = dados.get("players")
        Parametros["PokemonsProximos"] = dados.get("pokemons")
        
        return True  # sucesso
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar servidor: {e}")
        return False
    