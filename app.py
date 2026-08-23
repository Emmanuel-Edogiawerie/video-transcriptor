import glob
import os
import shutil
import tempfile

import streamlit as st
import yt_dlp
from faster_whisper import WhisperModel

st.set_page_config(page_title="Video → Guion", page_icon="🎬")


@st.cache_resource(show_spinner=False)
def get_model(model_size: str) -> WhisperModel:
    return WhisperModel(model_size, device="cpu", compute_type="int8")


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


def transcribe(url: str, model_size: str, language: str | None, vocabulary: str) -> str:
    tmp_dir = tempfile.mkdtemp(prefix="transcriptor_")
    try:
        with st.status("Descargando audio del vídeo...") as status:
            audio_path = download_audio(url, tmp_dir)

            status.update(label=f"Transcribiendo con Whisper ({model_size})...")
            model = get_model(model_size)
            segments, _info = model.transcribe(
                audio_path,
                language=language,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                condition_on_previous_text=False,
                initial_prompt=vocabulary.strip() or None,
            )
            lines = [segment.text.strip() for segment in segments if segment.text.strip()]
            text = "\n".join(lines)

            status.update(label="Guion listo", state="complete")
        return text
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


st.title("🎬 Video → Guion")
st.write(
    "Pega un link de **YouTube, TikTok o Instagram** y saca la transcripción "
    "del vídeo (el guion) en texto. 100% gratis, corre con Whisper local."
)

url = st.text_input(
    "Link del vídeo", placeholder="https://www.tiktok.com/@usuario/video/..."
)
col1, col2 = st.columns(2)
with col1:
    model_size = st.selectbox(
        "Modelo",
        ["tiny", "base", "small"],
        index=2,
        help="Más grande = más preciso pero más lento. 'small' alucina mucho menos que 'tiny'/'base'.",
    )
with col2:
    idioma_label = st.selectbox(
        "Idioma del vídeo",
        ["Auto-detectar", "Español", "English"],
        index=1,
        help="Forzar el idioma reduce errores de reconocimiento en clips cortos.",
    )
IDIOMAS = {"Auto-detectar": None, "Español": "es", "English": "en"}

vocabulario = st.text_input(
    "Vocabulario / nombres propios (opcional)",
    placeholder="Ej: OSA, EMMScode, Kotlin, backend, DAM",
    help="Palabras, nombres o anglicismos que suelen salir mal. Ayuda a Whisper a reconocerlos.",
)

if st.button("Transcribir", type="primary"):
    if not url.strip():
        st.warning("Pega primero un link de YouTube, TikTok o Instagram.")
    else:
        try:
            text = transcribe(
                url.strip(), model_size, IDIOMAS[idioma_label], vocabulario
            )
            if not text:
                st.warning(
                    "No se detectó voz en el vídeo (o el idioma no se pudo reconocer)."
                )
            else:
                st.text_area("Guion", text, height=400)
                st.download_button("Descargar .txt", text, file_name="guion.txt")
        except yt_dlp.utils.DownloadError:
            st.error(
                "No se pudo descargar ese vídeo. Puede ser privado, haber sido "
                "borrado, o la plataforma está bloqueando la descarga en este momento."
            )
        except Exception as exc:  # noqa: BLE001 - mostramos el error al usuario en la UI
            st.error(f"Ha ocurrido un error: {exc}")

st.caption(
    "⚠️ Úsalo solo con vídeos públicos y respeta los términos de servicio de cada "
    "plataforma. Pensado para sacar guiones propios o de referencia, no para "
    "scraping masivo."
)
