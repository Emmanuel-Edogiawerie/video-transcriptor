# 🎬 Video → Guion

Pega un link de **YouTube, TikTok o Instagram** y obtén la transcripción del
vídeo (el guion) en texto. 100% gratis: descarga con `yt-dlp`, extrae el audio
con `ffmpeg` y transcribe localmente con **Whisper** (vía `faster-whisper`) —
sin APIs de pago, sin claves, sin límites de uso.

🔗 App en vivo: https://video-transcriptor.streamlit.app *(una vez desplegada, ver abajo)*

## Cómo funciona

1. `yt-dlp` descarga el audio del vídeo a partir del link.
2. `ffmpeg` lo convierte a mp3.
3. `faster-whisper` (Whisper corriendo en local) lo transcribe a texto.
4. Streamlit muestra el resultado en una web sencilla, con botón de descarga.

## Probarlo en local

```bash
python -m venv .venv
.venv\Scripts\activate        # en Windows
pip install -r requirements.txt

# necesitas ffmpeg instalado y en el PATH
# Windows: winget install ffmpeg  (o choco install ffmpeg)

streamlit run app.py
```

Se abrirá en `http://localhost:8501`.

## Publicarlo gratis en la web (Streamlit Community Cloud)

> Nota: Hugging Face Spaces dejó de ser gratis para apps con backend Python
> (Gradio/Docker) — ahora piden suscripción PRO en el tier gratuito. Por eso
> esta app usa **Streamlit Community Cloud**, que sigue siendo 100% gratis
> para repos públicos de GitHub, sin tarjeta de crédito.

1. Entra en [share.streamlit.io](https://share.streamlit.io) e inicia sesión
   con tu cuenta de GitHub (la misma donde está este repo:
   `Emmanuel-Edogiawerie/video-transcriptor`).
2. Clic en **Create app** → **Deploy a public app from GitHub**.
3. Selecciona el repo `video-transcriptor`, rama `master`, archivo `app.py`.
4. Clic en **Deploy**. Streamlit Cloud detecta `requirements.txt` (paquetes
   Python) y `packages.txt` (paquetes de sistema, aquí `ffmpeg`) y construye
   el entorno solo.
5. En 1-2 minutos tendrás una URL pública tipo
   `https://video-transcriptor.streamlit.app` para compartir con quien
   quieras. Cada `git push` a `master` la redespliega automáticamente.

No hace falta GPU ni tarjeta: el tier gratuito de Streamlit Cloud (CPU
básica) es suficiente para los modelos `tiny`/`base`/`small` de Whisper.

## Notas

- Modelos más grandes (`small` vs `tiny`) = más precisión pero más tiempo de
  espera, sobre todo en CPU gratuita.
- Úsalo con vídeos públicos y respetando los términos de servicio de cada
  plataforma; pensado para sacar guiones propios o de referencia, no para
  scraping masivo.
- Instagram a veces bloquea descargas sin sesión iniciada; si falla con un
  link de IG, es lo más probable.
