from PIL import Image
import os

def remover_pixels_mortos(pasta_origem, pasta_destino=None):
    if pasta_destino is None:
        pasta_destino = pasta_origem

    print("Tipo de limpeza:")
    print("1 - Parcial (remove apenas pixels 100% transparentes)")
    print("2 - Total (remove qualquer pixel com qualquer nível de transparência)")
    escolha = input("Digite 1 ou 2: ")

    if escolha not in ("1", "2"):
        print("Opção inválida.")
        return

    for nome_arquivo in os.listdir(pasta_origem):
        if nome_arquivo.lower().endswith(".png"):
            caminho = os.path.join(pasta_origem, nome_arquivo)
            imagem = Image.open(caminho).convert("RGBA")
            largura, altura = imagem.size

            esquerda = largura
            direita = 0
            topo = altura
            base = 0

            for y in range(altura):
                for x in range(largura):
                    r, g, b, a = imagem.getpixel((x, y))

                    if (escolha == "1" and a != 0) or (escolha == "2" and a == 255):
                        esquerda = min(esquerda, x)
                        direita = max(direita, x)
                        topo = min(topo, y)
                        base = max(base, y)

            if esquerda > direita or topo > base:
                continue

            nova_imagem = imagem.crop((esquerda, topo, direita + 1, base + 1))
            caminho_destino = os.path.join(pasta_destino, nome_arquivo)
            nova_imagem.save(caminho_destino)

    print("Limpeza concluída.")

# Exemplo de uso
remover_pixels_mortos("Frames")
