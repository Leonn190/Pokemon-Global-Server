import requests
import json
import math
import numpy as np

def sanitizar_dados(d):
    if isinstance(d, dict):
        return {k: sanitizar_dados(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [sanitizar_dados(item) for item in d]
    elif isinstance(d, float):
        if math.isnan(d) or math.isinf(d):
            return str(d)  # transforma NaN, inf, -inf em string
        return d
    elif isinstance(d, (int, str)):
        return d
    elif d is None:
        return "None"
    else:
        return str(d)

def VerificaçãoSimplesServer(Parametros):
    try:
        url = Parametros["Link"].rstrip('/') + "/Verificar"

        payload = {
            "Raio": Parametros.get("Raio", 18) + 4,
            "X": Parametros["Player"].Loc[0],
            "Y": Parametros["Player"].Loc[1],
            "Code": Parametros["Code"],
            "Dados": Parametros["Player"].ToDicParcial()
        }

        payload_json = json.dumps(payload)

        resposta = requests.post(
            url,
            data=payload_json,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )

        # Se servidor respondeu 204 No Content → para execução
        if resposta.status_code == 204:
            Parametros["Running"] = False
            return

        resposta.raise_for_status()

        dados = resposta.json()

        Parametros["PlayersProximos"] = dados.get("players", [])
        Parametros["PokemonsProximos"] = dados.get("pokemons", [])
        Parametros["BausProximos"] = dados.get("baus", [])

        if not Parametros["BausProximos"]:
            Parametros["BausProximos"].append({
                "ID": 111,
                "X": 510,
                "Y": 520,
                "Raridade": 1
            })

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")

def VerificaMapa(Parametros):
    try:
        url = Parametros["Link"].rstrip('/') + "/Mapa"

        # Faz a requisição GET passando os dados como query params
        resposta = requests.get(url, timeout=30)
        resposta.raise_for_status()

        dados = resposta.json()

        # Converte direto para numpy arrays compactos
        Parametros["GridBiomas"]  = np.array(dados.get("biomas", []),  dtype=np.uint8)
        Parametros["GridObjetos"] = np.array(dados.get("objetos", []), dtype=np.uint8)
        Parametros["GridBlocos"]  = np.array(dados.get("blocos", []),  dtype=np.uint8)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar servidor (Mapa): {e}")

def SalvarConta(Parametros):
    try:
        player = Parametros["Player"]
        url = f'{Parametros["Link"]}/salvar'

        envio = player.ToDicTotal()
        sanitizar_dados(envio)
        print(envio["Inventario"])

        dados_para_enviar = {
            "codigo": Parametros["Code"],
            "personagem": envio
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
            print(f'[✔] Conta desconectada com sucesso: {resposta.json()["ativos"]}')
        elif resposta.status_code == 202:
            print(f'[ℹ] Conta já não estava ativa: {resposta.json()["mensagem"]}')
        else:
            print(f'[⚠] Erro ao desconectar: {resposta.status_code} - {resposta.text}')

    except Exception as e:
        print(f'[✘] Erro ao tentar sair da conta: {e}')

def RemoverBau(Parametros, bau_id):
    try:
        url = f'{Parametros["Link"]}/remover-bau'
        dados_para_enviar = {
            "id": bau_id
        }

        resposta = requests.post(url, json=dados_para_enviar)
        if resposta.status_code == 200:
            print(f'[✔] Baú removido com sucesso: {resposta.json()["mensagem"]}')
        elif resposta.status_code == 404:
            print(f'[⚠] Baú não encontrado: {resposta.json()["erro"]}')
        else:
            print(f'[⚠] Erro ao remover baú: {resposta.status_code} - {resposta.text}')

    except Exception as e:
        print(f'[✘] Erro ao tentar remover baú: {e}')

def RemoverPokemon(Parametros, pokemon_id):
    try:
        url = f'{Parametros["Link"]}/remover-pokemon'
        print (pokemon_id)
        dados_para_enviar = {
            "id": pokemon_id
        }

        resposta = requests.post(url, json=dados_para_enviar)
        if resposta.status_code == 200:
            print(f'[✔] Pokémon removido com sucesso: {resposta.json()["mensagem"]}')
        elif resposta.status_code == 404:
            print(f'[⚠] Pokémon não encontrado: {resposta.json()["erro"]}')
        else:
            print(f'[⚠] Erro ao remover Pokémon: {resposta.status_code} - {resposta.text}')

    except Exception as e:
        print(f'[✘] Erro ao tentar remover Pokémon: {e}')

def AtualizarPokemon(Parametros, pokemon_dados):
    """
    pokemon_dados é um dicionário com pelo menos as chaves:
        - "id" (int ou str)
        - "Dados" (string compactada)
        - "extra" (dicionário com os extras a atualizar)
    """

    try:
        url = f'{Parametros["Link"]}/atualizar-pokemon'
        resposta = requests.post(url, json=pokemon_dados)

        if resposta.status_code == 200:
            print(f'[✔] Pokémon atualizado com sucesso: {resposta.json().get("mensagem","")}')
        elif resposta.status_code == 404:
            print(f'[⚠] Pokémon não encontrado: {resposta.json().get("erro","")}')
        else:
            print(f'[⚠] Erro ao atualizar Pokémon: {resposta.status_code} - {resposta.text}')

    except Exception as e:
        print(f'[✘] Erro ao tentar atualizar Pokémon: {e}')
