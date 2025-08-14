import os

# Caminho da pasta que você quer alterar
pasta = "Recursos/Visual/Skins/Bloqueadas"

# Lista todos os arquivos da pasta (ignora subpastas)
arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]

# Renomeia os arquivos numerando de 13 até o final
for i, arquivo in enumerate(arquivos, start=13):
    # Extensão original do arquivo
    extensao = os.path.splitext(arquivo)[1]

    # Novo nome: número + extensão
    novo_nome = f"{i}{extensao}"

    # Caminhos completos
    caminho_antigo = os.path.join(pasta, arquivo)
    caminho_novo = os.path.join(pasta, novo_nome)

    # Renomeia
    os.rename(caminho_antigo, caminho_novo)

print(f"Renomeados {len(arquivos)} arquivos de 13 até {12 + len(arquivos)}")