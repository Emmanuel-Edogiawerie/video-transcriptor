# 🎬 Video → Guion

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
[![Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://video-transcriptor.streamlit.app)

Pega el link de un vídeo de **YouTube, TikTok o Instagram** y obtén su
transcripción completa — el guion — en unos segundos. Sin APIs de pago, sin
cuentas, sin límites de uso: todo corre con modelos **Whisper en local**.

**🔗 Pruébalo:** https://video-transcriptor.streamlit.app

**Incluye:**
- 📝 Guion con **timestamp por línea** (`[mm:ss]`)
- 📊 **Analíticas del vídeo** (vistas, likes, comentarios, duración) sacadas de los metadatos públicos de la plataforma
- 📄 Export en **`.md` con frontmatter**, listo para pegar en Obsidian
- 🪝 **Análisis de hook y estructura** opcional, vía Groq (LLM gratuito, cada usuario usa su propia API key)

## Por qué existe

Lo hice para dejar de perder tiempo transcribiendo a mano mis propios vídeos
(y los de referencia) cada vez que quería reutilizar o adaptar contenido.
Todas las herramientas "gratis" que encontré tenían límite de minutos o
pedían suscripción tarde o temprano, así que monté el pipeline completo con
piezas open source que corren sin coste ni claves de API.

## Cómo funciona

```mermaid
flowchart LR
    A["🔗 Link del vídeo"] --> B["yt-dlp<br/>descarga audio + metadatos"]
    B --> C["ffmpeg<br/>convierte a mp3"]
    C --> D["faster-whisper<br/>transcribe en local"]
    D --> E["📝 Guion con timestamps"]
    B --> F["📊 Vistas / likes / comentarios"]
    E -.opcional.-> G["🪝 Groq LLM<br/>hook + estructura"]
```

1. **yt-dlp** descarga el audio del vídeo a partir del link, y de paso trae
   metadatos públicos (vistas, likes, comentarios, duración).
2. **ffmpeg** convierte el audio a mp3.
3. **faster-whisper** (Whisper corriendo en local, sin API) lo transcribe a
   texto con timestamp por línea.
4. **Streamlit** muestra guion + analíticas, y permite descargar el guion en
   `.md` con frontmatter (listo para Obsidian).
5. *(Opcional)* con una API key gratuita de Groq, un LLM analiza el hook y la
   estructura del guion.

## Stack

| Pieza | Uso |
|---|---|
| [Streamlit](https://streamlit.io) | interfaz web |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | descarga de vídeo/audio + metadatos/analíticas |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | transcripción (Whisper + CTranslate2) |
| [ffmpeg](https://ffmpeg.org) | procesado de audio |
| [Groq](https://console.groq.com) (opcional) | LLM gratuito para el análisis de hook/estructura |

## Uso rápido en local

```bash
git clone https://github.com/Emmanuel-Edogiawerie/video-transcriptor.git
cd video-transcriptor

python -m venv .venv
.venv\Scripts\activate        # Windows — usa "source .venv/bin/activate" en macOS/Linux
pip install -r requirements.txt

# necesitas ffmpeg instalado y en el PATH
# Windows: winget install ffmpeg   |   macOS: brew install ffmpeg   |   Linux: apt install ffmpeg

streamlit run app.py
```

Se abre en `http://localhost:8501`.

## Despliegue gratis (Streamlit Community Cloud)

> Hugging Face Spaces dejó de ser gratis para apps con backend Python
> (Gradio/Docker): ahora exige suscripción PRO en el tier gratuito. Por eso
> este proyecto usa **Streamlit Community Cloud**, que sigue siendo 100%
> gratis para repos públicos de GitHub, sin tarjeta.

1. Entra en [share.streamlit.io](https://share.streamlit.io) e inicia sesión con GitHub.
2. **Create app** → **Deploy a public app from GitHub**.
3. Repo: `Emmanuel-Edogiawerie/video-transcriptor` · Branch: `master` · Main file: `app.py`.
4. **Deploy**. Streamlit Cloud instala `requirements.txt` (paquetes Python) y
   `packages.txt` (paquetes de sistema, aquí `ffmpeg`) automáticamente.
5. Cada `git push` a `master` redespliega la app sola.

## Estructura del proyecto

```
video-transcriptor/
├── app.py             # app Streamlit (UI + orquestación del pipeline)
├── requirements.txt   # dependencias Python
├── packages.txt       # dependencias de sistema (ffmpeg) para Streamlit Cloud
└── README.md
```

## Limitaciones conocidas

- En el tier gratuito (CPU, sin GPU) los modelos `tiny`/`base` son rápidos;
  `small` es más preciso pero tarda más en vídeos largos.
- Instagram a veces bloquea descargas sin sesión iniciada — puede fallar en
  contenido privado o restringido.
- Pensado para sacar guiones propios o de referencia sobre vídeo **público**,
  no para scraping masivo. Respeta los términos de servicio de cada
  plataforma.

## Roadmap

- [x] Timestamps por segmento
- [x] Selección manual de idioma
- [x] Analíticas del vídeo (vistas/likes/comentarios)
- [x] Análisis de hook y estructura (Groq)
- [x] Export a `.md` con frontmatter
- [ ] Exportar directamente a `.srt`

## Licencia

[MIT](LICENSE) — úsalo, modifícalo, compártelo.

---

Hecho por [Emmanuel Osa](https://github.com/Emmanuel-Edogiawerie).
