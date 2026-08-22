# 🎬 Video → Guion

Pega un link de **YouTube, TikTok o Instagram** y obtén la transcripción del
vídeo (el guion) en texto. 100% gratis: descarga con `yt-dlp`, extrae el audio
con `ffmpeg` y transcribe localmente con **Whisper** (vía `faster-whisper`) —
sin APIs de pago, sin claves, sin límites de uso.

## Cómo funciona

1. `yt-dlp` descarga el audio del vídeo a partir del link.
2. `ffmpeg` lo convierte a mp3.
3. `faster-whisper` (Whisper corriendo en local) lo transcribe a texto.
4. Gradio muestra el resultado en una web sencilla, con botón de copiar.

## Probarlo en local

```bash
python -m venv .venv
.venv\Scripts\activate        # en Windows
pip install -r requirements.txt

# necesitas ffmpeg instalado y en el PATH
# Windows: winget install ffmpeg  (o choco install ffmpeg)

python app.py
```

Se abrirá en `http://localhost:7860`.

## Subirlo a GitHub

```bash
git init
git add .
git commit -m "Video → Guion: transcriptor gratuito con Whisper local"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/video-transcriptor.git
git push -u origin main
```

## Publicarlo gratis en la web (Hugging Face Spaces)

1. Crea una cuenta gratis en [huggingface.co](https://huggingface.co).
2. Ve a **New Space** → elige el SDK **Gradio** → nombre `video-transcriptor`.
3. Hugging Face te da un repo git propio para ese Space. Súbele el mismo
   código (puedes hacerlo desde la misma carpeta, con un segundo remoto):

   ```bash
   git remote add space https://huggingface.co/spaces/<tu-usuario>/video-transcriptor
   git push space main
   ```

4. El Space detecta `requirements.txt` y `packages.txt` (para instalar
   `ffmpeg`), construye el entorno solo, y en 1-2 minutos tendrás una URL
   pública tipo `https://huggingface.co/spaces/<tu-usuario>/video-transcriptor`
   para compartir con quien quieras.

No hace falta GPU ni ninguna tarjeta de crédito: el tier gratuito de Spaces
(CPU básico) es suficiente para los modelos `tiny`/`base`/`small` de Whisper.

## Notas

- Modelos más grandes (`small` vs `tiny`) = más precisión pero más tiempo de
  espera, sobre todo en CPU gratuita.
- Úsalo con vídeos públicos y respetando los términos de servicio de cada
  plataforma; pensado para sacar guiones propios o de referencia, no para
  scraping masivo.
- Instagram a veces bloquea descargas sin sesión iniciada; si falla con un
  link de IG, es lo más probable.
