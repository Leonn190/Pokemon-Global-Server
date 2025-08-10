import requests
import os
from Codigo.Prefabs.Mensagens import adicionar_mensagem_passageira
from Codigo.Geradores.GeradorPokemon import criar_pokemon_especifico, desserializar_pokemon

import math

def limpar_nans(obj):
    if isinstance(obj, dict):
        return {k: limpar_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [limpar_nans(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0  # ou outro valor padrão
        return obj
    else:
        return obj

def AdicionaServer(Nome, Link, Limite=7):
    os.makedirs("Servers", exist_ok=True)

    nome_arquivo = "".join(c if c.isalnum() else "_" for c in Nome)
    caminho = os.path.join("Servers", f"{nome_arquivo}.py")

    servidores_existentes = []
    for arquivo in os.listdir("Servers"):
        if arquivo.endswith(".py"):
            try:
                caminho_arquivo = os.path.join("Servers", arquivo)
                with open(caminho_arquivo, "r", encoding="utf-8") as f:
                    contexto = {}
                    exec(f.read(), contexto)
                    server = contexto.get("server", {})
                    if "nome" in server and "link" in server:
                        servidores_existentes.append(server)
            except Exception as e:
                print(f"Erro ao carregar {arquivo}: {e}")

    if len(servidores_existentes) >= Limite:
        adicionar_mensagem_passageira("Limite máximo de servidores atingido",cor=(210,0,0))
        return

    if any(s["nome"] == Nome for s in servidores_existentes):
        adicionar_mensagem_passageira("Já existe um servidor com esse nome",cor=(210,0,0))
        return

    if any(s["link"] == Link for s in servidores_existentes):
        adicionar_mensagem_passageira("Já existe um servidor com esse link",cor=(210,0,0))
        return

    conteudo = f"server = {{'nome': {repr(Nome)}, 'link': {repr(Link)}}}\n"

    with open(caminho, "w", encoding="utf-8") as f:
        adicionar_mensagem_passageira("Server Adicionado com Sucesso")
        f.write(conteudo)

def CarregarServers(Parametros):
    Parametros["Servers"] = []  # Resetando a lista de servidores
    pasta = "Servers"
    if not os.path.exists(pasta):
        return

    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.endswith(".py"):
            caminho = os.path.join(pasta, nome_arquivo)
            try:
                contexto = {}
                with open(caminho, "r", encoding="utf-8") as f:
                    exec(f.read(), {}, contexto)

                if "server" in contexto and isinstance(contexto["server"], dict):
                    Parametros["Servers"].append(contexto["server"])
            except:
                pass  # Erros são ignorados silenciosamente

def ApagarServer(Nome):
    nome_arquivo = "".join(c if c.isalnum() else "_" for c in Nome)
    caminho = os.path.join("Servers", f"{nome_arquivo}.py")

    if os.path.exists(caminho):
        try:
            os.remove(caminho)
        except Exception:
            pass  # Silenciosamente ignora qualquer erro

def RenomearServer(NomeNovo, Link):
    pasta = "Servers"
    if not os.path.exists(pasta):
        return

    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.endswith(".py"):
            caminho = os.path.join(pasta, nome_arquivo)
            try:
                contexto = {}
                with open(caminho, "r", encoding="utf-8") as f:
                    exec(f.read(), {}, contexto)

                if "server" in contexto and isinstance(contexto["server"], dict):
                    server = contexto["server"]
                    if server.get("link") == Link:
                        # Apagar o arquivo antigo
                        try:
                            os.remove(caminho)
                        except Exception:
                            return
                        
                        # Criar um novo com o novo nome
                        AdicionaServer(NomeNovo, Link)
                        return
            except Exception:
                pass

def EntrarServer(Code, Parametros):
    try:
        url = f"{Parametros['ServerSelecionado']['link']}/acessar"
        response = requests.post(url, json={'codigo': Code}, timeout=5)
        rjson = response.json() if response.content else {}

        if response.status_code == 201:
            Parametros["EstadoServidor"] = {
                "status": 201,
                "mensagem": "Conta acessada com sucesso!",
                "dados": rjson
            }
        elif response.status_code == 200:
            Parametros["EstadoServidor"] = {
                "status": 200,
                "mensagem": "Conta já estava ativa.",
                "dados": rjson
            }
        elif response.status_code == 202:
            Parametros["EstadoServidor"] = {
                "status": 202,
                "mensagem": "Conta ainda não registrada.",
                "dados": rjson
            }
        elif response.status_code == 503:
            Parametros["EstadoServidor"] = {
                "status": 503,
                "mensagem": "Servidor não está ativado.",
                "dados": rjson
            }
        elif response.status_code == 504:
            Parametros["EstadoServidor"] = {
                "status": 504,
                "mensagem": "Servidor está desligado.",
                "dados": rjson
            }
        else:
            Parametros["EstadoServidor"] = {
                "status": 600,
                "mensagem": f"Erro inesperado: {response.status_code}",
                "dados": rjson
            }
    except requests.exceptions.RequestException as e:
        Parametros["EstadoServidor"] = {
            "status": None,
            "mensagem": f"Erro de conexão: {e}",
            "dados": None
        }

def RegistrarNoServer(Code, Personagem, Parametros):
    try:
        url = f"{Parametros['ServerSelecionado']['link']}/salvar"
        # Monta o JSON com os dados que quer salvar — aqui estou incluindo 'codigo' e 'personagem'

        Personagem["Skin"] = round(Personagem["Skin"])
        Personagem["Pokemons"][0] = limpar_nans(desserializar_pokemon(criar_pokemon_especifico(Personagem["Inicial"])))
        del Personagem["Inicial"]

        payload = {
            'codigo': Code,
            'personagem': Personagem  # ajuste conforme o que sua API espera receber
        }
        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 201:
            print("Conta registrada com sucesso!")
            return response.json()
        elif response.status_code == 200:
            print("Conta atualizada com sucesso!")
            return response.json()
        else:
            print(f"Erro inesperado: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")
        return None

def VerificaOperador(codigo_operador, Parametros):
    url = f"{Parametros['ServerSelecionado']['link']}/verificar-operador"
    try:
        # Envia o código como JSON no corpo da requisição
        response = requests.post(url, json={"codigo": codigo_operador}, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            Parametros["Operador"] = data.get("operador", False)
        else:
            Parametros["Operador"] = False
            adicionar_mensagem_passageira("Senha Invalida",cor=(200,0,0))
    except requests.RequestException:
        Parametros["Operador"] = False

def AtivarServidor(Parametros):
    url = f"{Parametros['ServerSelecionado']['link']}/ativar-servidor"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Servidor ativado ou já ativo
            return True
        else:
            return False
    except requests.RequestException:
        return False

def LigarDesligarServidor(Parametros, ligar):
    url = f"{Parametros['ServerSelecionado']['link']}/ligar-desligar"
    try:
        response = requests.post(url, json={"ligar": ligar}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Confirmar se o estado é o esperado
            return data.get("ligado", None) == ligar
        else:
            return False
    except requests.RequestException:
        return False

def ObterEstadoServidor(Parametros):
    url = f"{Parametros['ServerSelecionado']['link']}/estado-server"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            ligado = data.get("ligado", False)
            ativo = data.get("ativo", False)
            # Atualiza os índices de controle do servidor em Parametros
            Parametros["ServerOperadoLigado"] = ligado
            Parametros["ServerOperadoAtivado"] = ativo
            print (ligado, ativo)
            return True  # sucesso
        else:
            # Falha na requisição
            Parametros["ServerOperadoLigado"] = False
            Parametros["ServerOperadoAtivado"] = False
            print("deu ruim")
            return False
    except requests.RequestException:
        # Exceção na conexão com o servidor
        Parametros["ServerOperadoLigado"] = False
        Parametros["ServerOperadoAtivado"] = False
        print("deu ruim 2")
        return False

def ResetarServidor(Parametros):
    url = f"{Parametros['ServerSelecionado']['link']}/resetar-servidor"
    try:
        response = requests.post(url, timeout=5)
        if response.status_code == 200:
            Parametros["ServerOperadoAtivado"] = False
            Parametros["ServerOperadoLigado"] = False
        else:
            adicionar_mensagem_passageira("Erro Inesperado 1",cor=(200,0,0))
    except requests.RequestException as e:
        adicionar_mensagem_passageira("Erro Inesperado 2",cor=(200,0,0))
    