import requests
import json

def main():
    print("Digite:")
    print("1 - Ver MAPAS")
    print("2 - Ver CONTAS")
    print("3 - Ver ROTAS DISPONÍVEIS")
    escolha = input("Escolha: ").strip()

    if escolha == "1":
        url = "https://pokemonunity.onrender.com/mapaa"
    elif escolha == "2":
        url = "https://pokemonunity.onrender.com/contas"
    elif escolha == "3":
        url = "https://pokemonunity.onrender.com/rotas"
    else:
        print("Opção inválida. Encerrando.")
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        dados = response.json()

        if escolha == "1":
            print("Dados do mapa recebidos:")
            print(json.dumps(dados, indent=2, ensure_ascii=False))

        elif escolha == "2":
            contas = dados.get("contas", [])
            print("Contas registradas no servidor:")
            for i, conta in enumerate(contas, 1):
                print(f"{i}. {conta}")

        elif escolha == "3":
            rotas = dados.get("rotas", [])
            print("Rotas disponíveis no servidor:")
            for rota in rotas:
                print(rota)

    except requests.exceptions.RequestException as erro:
        print("Erro ao acessar a rota:", erro)

if __name__ == "__main__":
    main()
