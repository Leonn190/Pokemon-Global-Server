from PIL import Image
import os

def extrair_frames_gif(caminho_gif, pasta_saida="frames_extraidos"):
    # Cria a pasta de saída se não existir
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # Abre o GIF
    gif = Image.open(caminho_gif)
    nome_base = os.path.splitext(os.path.basename(caminho_gif))[0]

    # Extrai os frames
    frame_index = 0
    while True:
        gif.seek(frame_index)
        frame = gif.copy().convert("RGBA")  # Converte para RGBA para preservar transparência
        frame.save(os.path.join(pasta_saida, f"{nome_base}_frame{frame_index}.png"))
        frame_index += 1
        try:
            gif.seek(frame_index)
        except EOFError:
            break

    print(f"{frame_index} frames extraídos para a pasta '{pasta_saida}'.")

# Exemplo de uso:
# extrair_frames_gif("caminho/do/seu_arquivo.gif")

extrair_frames_gif("gif.gif")
