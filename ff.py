from pydub import AudioSegment

# Carrega o arquivo original
audio = AudioSegment.from_ogg("musica.ogg")

# Define o intervalo que você quer manter (em milissegundos)
# Aqui mantém de 15s até 1min05s
inicio = 15 * 1000     # 15 segundos
fim = 65 * 1000        # 65 segundos

# Faz o recorte
corte = audio[inicio:fim]

# Salva em um novo arquivo
corte.export("musica_cortada.ogg", format="ogg")

print("Recorte concluído! Arquivo salvo como musica_cortada.ogg")