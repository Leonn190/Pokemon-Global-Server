import os, re, tempfile, subprocess
from imageio_ffmpeg import get_ffmpeg_exe  # vem junto com moviepy/imageio_ffmpeg

def juntar_videos_ffmpeg(pasta, saida="PhRuimNaVida.mp4"):
    if not os.path.isdir(pasta):
        raise FileNotFoundError(os.path.abspath(pasta))

    vids = [f for f in os.listdir(pasta) if f.lower().endswith(".mp4")]
    if not vids:
        return
    vids.sort(key=lambda s: [int(t) if t.isdigit() else t.lower()
                             for t in re.split(r'(\d+)', s)])

    abspaths = [os.path.join(pasta, v) for v in vids]
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as f:
        lista_txt = f.name
        for p in abspaths:
            f.write(f"file '{p}'\n")

    ffmpeg = get_ffmpeg_exe()

    cmd = [ffmpeg, "-f", "concat", "-safe", "0", "-i", lista_txt, "-c", "copy", saida]
    try:
        subprocess.run(cmd, check=True)
    finally:
        try: os.remove(lista_txt)
        except Exception: pass

juntar_videos_ffmpeg(r"C:\Users\Leon\Documents\GitHub\Pokemon-Global-Server\uva", "final.mp4")