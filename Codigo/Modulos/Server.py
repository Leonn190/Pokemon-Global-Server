import pygame
import requests
import os
from Prefabs.Mensagens import adicionar_mensagem_passageira

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
        url = f"{Parametros["ServerSelecionado"]['link']}/acessar"
        response = requests.post(url, json={'codigo': Code}, timeout=5)

        if response.status_code == 201:
            print("Conta acessada com sucesso!")
            return response.json()
        elif response.status_code == 200:
            print("Conta já estava ativa.")
            return response.json()
        elif response.status_code == 202:
            print("Conta ainda não registrada.")
            return response.json()
        else:
            print(f"Erro inesperado: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")
    