import requests
import json

def VerificaçãoSimplesServer(Parametros):
    try:
        url = Parametros["Link"].rstrip('/') + "/Verificar"

        payload = {
            "Raio": Parametros.get("Raio", 50),
            "X": Parametros["Player"].Loc[0],
            "Y": Parametros["Player"].Loc[1],
            "Code": Parametros["Code"],
            "Dados": Parametros["Player"].ToDicParcial()
        }

        payload_json = json.dumps(payload)

        resposta = requests.post(url, data=payload_json, headers={'Content-Type': 'application/json'}, timeout=5)
        resposta.raise_for_status()

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

def SalvarConta(Parametros):
    try:
        player = Parametros["Player"]
        url = f'{Parametros["Link"]}/salvar'

        dados_para_enviar = {
            "codigo": Parametros["Code"],
            "personagem": player.ToDicTotal()
        }

        resposta = requests.post(url, json=dados_para_enviar)
        if resposta.status_code in [200, 201]:
            print(f'[✔] Conta salva com sucesso: {resposta.json()["mensagem"]}')
        else:
            print(f'[⚠] Erro ao salvar conta: {resposta.status_code} - {resposta.text}')

    except Exception as e:
        print(f'[✘] Erro ao tentar salvar conta: {e}')

def SairConta(Parametros):
    try:
        url = f'{Parametros["Link"]}/sair'
        dados_para_enviar = {
            "codigo": Parametros["Code"]
        }

        resposta = requests.post(url, json=dados_para_enviar)
        if resposta.status_code == 200:
            print(f'[✔] Conta desconectada com sucesso: {resposta.json()["mensagem"]}')
        elif resposta.status_code == 202:
            print(f'[ℹ] Conta já não estava ativa: {resposta.json()["mensagem"]}')
        else:
            print(f'[⚠] Erro ao desconectar: {resposta.status_code} - {resposta.text}')

    except Exception as e:
        print(f'[✘] Erro ao tentar sair da conta: {e}')
