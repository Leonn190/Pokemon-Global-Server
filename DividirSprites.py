from PIL import Image
import os

def dividir_em_frames(caminho_imagem, largura_frame, altura_frame, pasta_saida="Frames"):
    # Carrega a imagem
    imagem = Image.open(caminho_imagem)
    largura_total, altura_total = imagem.size

    # Cria a pasta de saída, se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    contador = 0
    for y in range(0, altura_total, altura_frame):
        for x in range(0, largura_total, largura_frame):
            box = (x, y, x + largura_frame, y + altura_frame)
            frame = imagem.crop(box)
            frame.save(os.path.join(pasta_saida, f"frame_{contador}.png"))
            contador += 1

    print(f"{contador} frames salvos na pasta '{pasta_saida}'.")

# Exemplo de uso
dividir_em_frames("on.png", 47, 47)
