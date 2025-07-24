import pygame
import os

def AdicionaServer(Nome, Link):
    os.makedirs("Servers", exist_ok=True)

    nome_arquivo = "".join(c if c.isalnum() else "_" for c in Nome)

    caminho = os.path.join("Servers", f"{nome_arquivo}.py")

    conteudo = f"server = {{'nome': {repr(Nome)}, 'link': {repr(Link)}}}\n"

    with open(caminho, "w", encoding="utf-8") as f:
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
