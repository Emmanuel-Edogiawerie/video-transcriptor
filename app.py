import datetime as dt
import glob
import os
import shutil
import tempfile

import requests
import streamlit as st
import yt_dlp
from faster_whisper import WhisperModel

st.set_page_config(page_title="Video → Guion", page_icon="🎬")


@st.cache_resource(show_spinner=False)
def get_model(model_size: str) -> WhisperModel:
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def download_audio(url: str, tmp_dir: str) -> tuple[str, dict]:
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
        info = ydl.extract_info(url, download=True)

    matches = glob.glob(os.path.join(tmp_dir, "audio.*"))
    if not matches:
        raise RuntimeError("No se pudo extraer el audio del vídeo.")
    return matches[0], info


def format_timestamp(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"[{minutes:02d}:{secs:02d}]"


def transcribe(url: str, model_size: str, language: str | None, vocabulary: str):
    tmp_dir = tempfile.mkdtemp(prefix="transcriptor_")
    try:
        with st.status("Descargando audio del vídeo...") as status:
            audio_path, info = download_audio(url, tmp_dir)

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
            lines = [
                f"{format_timestamp(segment.start)} {segment.text.strip()}"
                for segment in segments
                if segment.text.strip()
            ]
            text = "\n".join(lines)

            status.update(label="Guion listo", state="complete")
        return text, info
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def build_markdown(text: str, info: dict) -> str:
    title = info.get("title", "Sin título")
    source_url = info.get("webpage_url", "")
    plataforma = info.get("extractor_key", "")
    fecha = dt.date.today().isoformat()
    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        f"url: {source_url}\n"
        f"plataforma: {plataforma}\n"
        f"fecha_transcripcion: {fecha}\n"
        "---\n\n"
    )
    return frontmatter + text


def analizar_hook(texto: str, api_key: str) -> str:
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un analista de contenido short-form (TikTok/Reels/Shorts) "
                        "experto en hooks y estructura narrativa. Respondes en español, "
                        "directo y sin relleno."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Analiza este guion de vídeo. Responde en 3 bloques:\n"
                        "1. **Hook**: cuál es (las primeras 1-2 líneas) y si es fuerte "
                        "o débil, y por qué.\n"
                        "2. **Estructura**: los beats del vídeo en 3-5 puntos.\n"
                        "3. **Mejora**: una sugerencia concreta y accionable.\n\n"
                        f"Guion:\n{texto}"
                    ),
                },
            ],
            "temperature": 0.4,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


st.title("🎬 Video → Guion")
st.write(
    "Pega un link de **YouTube, TikTok o Instagram** y saca la transcripción "
    "del vídeo (el guion) en texto, con timestamps y analíticas. 100% gratis, "
    "corre con Whisper local."
)

url = st.text_input(
    "Link del vídeo", placeholder="https://www.tiktok.com/@usuario/video/..."
)
MODEL_SIZE = "small"

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
            text, info = transcribe(
                url.strip(), MODEL_SIZE, IDIOMAS[idioma_label], vocabulario
            )
            if not text:
                st.warning(
                    "No se detectó voz en el vídeo (o el idioma no se pudo reconocer)."
                )
                st.session_state.pop("guion", None)
            else:
                st.session_state["guion"] = text
                st.session_state["info"] = info
                st.session_state["markdown"] = build_markdown(text, info)
        except yt_dlp.utils.DownloadError:
            st.error(
                "No se pudo descargar ese vídeo. Puede ser privado, haber sido "
                "borrado, o la plataforma está bloqueando la descarga en este momento."
            )
        except Exception as exc:  # noqa: BLE001 - mostramos el error al usuario en la UI
            st.error(f"Ha ocurrido un error: {exc}")

if "guion" in st.session_state:
    info = st.session_state["info"]

    stats = {
        "👁️ Vistas": info.get("view_count"),
        "❤️ Likes": info.get("like_count"),
        "💬 Comentarios": info.get("comment_count"),
        "⏱️ Duración": (
            f"{int(info.get('duration', 0) // 60)}:{int(info.get('duration', 0) % 60):02d}"
            if info.get("duration")
            else None
        ),
    }
    disponibles = {k: v for k, v in stats.items() if v is not None}
    if disponibles:
        cols = st.columns(len(disponibles))
        for col, (label, value) in zip(cols, disponibles.items()):
            col.metric(label, f"{value:,}" if isinstance(value, int) else value)
    else:
        st.caption(
            "Esta plataforma no expuso analíticas públicas para este vídeo "
            "(frecuente en Instagram sin sesión iniciada)."
        )

    st.text_area("Guion", st.session_state["guion"], height=400)
    st.download_button(
        "Descargar .md (formato Obsidian)",
        st.session_state["markdown"],
        file_name="guion.md",
        mime="text/markdown",
    )

    with st.expander("🪝 Analizar hook y estructura (requiere API key gratis de Groq)"):
        st.caption(
            "Consigue una key gratis en https://console.groq.com/keys (sin tarjeta)."
        )
        groq_key = st.text_input("Groq API key", type="password")
        if st.button("Analizar"):
            if not groq_key.strip():
                st.warning("Pega tu API key de Groq primero.")
            else:
                try:
                    with st.spinner("Analizando..."):
                        analisis = analizar_hook(
                            st.session_state["guion"], groq_key.strip()
                        )
                    st.markdown(analisis)
                except requests.HTTPError as exc:
                    st.error(f"Groq rechazó la petición: {exc}")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Ha ocurrido un error: {exc}")

st.caption(
    "⚠️ Úsalo solo con vídeos públicos y respeta los términos de servicio de cada "
    "plataforma. Pensado para sacar guiones propios o de referencia, no para "
    "scraping masivo."
)
