import requests

url = "https://pokemonunity.onrender.com/contas"

try:
    response = requests.get(url)
    response.raise_for_status()  # Lança exceção se não for status 200

    dados = response.json()  # Converte JSON em dicionário
    contas = dados.get("contas", [])

    print("Contas registradas no servidor:")
    for i, conta in enumerate(contas, 1):
        print(f"{i}. {conta}")

except requests.exceptions.RequestException as erro:
    print("Erro ao acessar a rota:", erro)
