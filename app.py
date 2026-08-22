import os
import glob
import shutil
import tempfile

import gradio as gr
import yt_dlp
from faster_whisper import WhisperModel

MODEL_CACHE = {}


def get_model(model_size: str) -> WhisperModel:
    if model_size not in MODEL_CACHE:
        MODEL_CACHE[model_size] = WhisperModel(
            model_size, device="cpu", compute_type="int8"
        )
    return MODEL_CACHE[model_size]


def download_audio(url: str, tmp_dir: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tmp_dir, "audio.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    matches = glob.glob(os.path.join(tmp_dir, "audio.*"))
    if not matches:
        raise RuntimeError("No se pudo extraer el audio del vídeo.")
    return matches[0]


def transcribe_video(url: str, model_size: str, progress=gr.Progress()):
    if not url or not url.strip():
        return "Pega primero un link de YouTube, TikTok o Instagram."

    tmp_dir = tempfile.mkdtemp(prefix="transcriptor_")
    try:
        progress(0.1, desc="Descargando audio del vídeo...")
        audio_path = download_audio(url.strip(), tmp_dir)

        progress(0.4, desc=f"Transcribiendo con Whisper ({model_size})...")
        model = get_model(model_size)
        segments, _info = model.transcribe(audio_path, language=None)

        progress(0.9, desc="Montando el guion...")
        text = " ".join(segment.text.strip() for segment in segments).strip()

        if not text:
            return "No se detectó voz en el vídeo (o el idioma no se pudo reconocer)."

        return text

    except yt_dlp.utils.DownloadError:
        return (
            "No se pudo descargar ese vídeo. Puede ser privado, haber sido "
            "borrado, o la plataforma está bloqueando la descarga en este momento."
        )
    except Exception as exc:  # noqa: BLE001 - mostramos el error al usuario en la UI
        return f"Ha ocurrido un error: {exc}"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


with gr.Blocks(title="Video → Guion") as demo:
    gr.Markdown(
        "# 🎬 Video → Guion\n"
        "Pega un link de **YouTube, TikTok o Instagram** y saca la transcripción "
        "del vídeo (el guion) en texto. 100% gratis, corre con modelos Whisper locales."
    )

    with gr.Row():
        url_input = gr.Textbox(
            label="Link del vídeo",
            placeholder="https://www.tiktok.com/@usuario/video/...",
            scale=3,
        )
        model_choice = gr.Dropdown(
            choices=["tiny", "base", "small"],
            value="base",
            label="Modelo",
            info="Más grande = más preciso pero más lento",
            scale=1,
        )

    transcribe_btn = gr.Button("Transcribir", variant="primary")
    output = gr.Textbox(label="Guion", lines=18, show_copy_button=True)

    transcribe_btn.click(
        fn=transcribe_video,
        inputs=[url_input, model_choice],
        outputs=output,
    )

    gr.Markdown(
        "---\n"
        "⚠️ Úsalo solo con vídeos públicos y respeta los términos de servicio "
        "de cada plataforma. Pensado para uso personal (sacar guiones propios "
        "o de referencia), no para scraping masivo."
    )

if __name__ == "__main__":
    demo.queue().launch()
