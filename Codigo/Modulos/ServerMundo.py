import requests
import json

def VerificaçãoSimplesServer(Parametros):
    try:
        url = Parametros["Link"].rstrip('/') + "/Verificar"

        payload = {
            "Raio": Parametros.get("Raio", 50),
            "X": Parametros["Loc"][0],
            "Y": Parametros["Loc"][1],
            "Code": Parametros["Code"]
        }

        payload_json = json.dumps(payload)

        resposta = requests.post(url, data=payload_json, headers={'Content-Type': 'application/json'}, timeout=5)
        resposta.raise_for_status()

        # Calcular o tamanho do JSON recebido (em KB)
        tamanho_recebido_kb = len(resposta.content) / 1024
        print(f"Tamanho do JSON recebido: {tamanho_recebido_kb:.2f} KB")

        dados = resposta.json()

        Parametros["PlayersProximos"] = dados.get("players")
        Parametros["PokemonsProximos"] = dados.get("pokemons")

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")

def VerificaMapa(Parametros):
    try:
        url = Parametros["Link"].rstrip('/') + "/Mapa"

        # Faz a requisição GET passando os dados como query params
        resposta = requests.get(url, timeout=5)
        resposta.raise_for_status()

        dados = resposta.json()

        Parametros["GridBiomas"] = dados.get("biomas")
        Parametros["GridObjetos"] = dados.get("objetos")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar servidor (Mapa): {e}")
