# Insta Clip Studio
Download (yt-dlp) -> Edit (studio card / simple crop, themes, camera, banner) -> Subtitles (faster-whisper, AI translate) -> Export (FFmpeg).

## Get the .exe (pick one)
**A. GitHub builds it for you**
1. Create a GitHub repo and upload this whole folder (keep the `.github` folder).
2. **Actions** tab -> "Build Windows installer" -> **Run workflow**.
3. Download **Insta-Clip-Studio-Setup** from the finished run, unzip, run the .exe.

**B. Build on your own PC:** double-click `Build-Windows.bat`.

## First launch = automatic setup
The installer is small. On first launch the **Setup** tab scans your PC and uses what you already have:
Python, faster-whisper (+ your cached large-v3 / distil-large-v3 / medium models), Demucs, yt-dlp, FFmpeg
(it even finds the FFmpeg that moviepy ships). Only what is missing is downloaded/installed
(yt-dlp, FFmpeg and whisper.cpp go to `%LOCALAPPDATA%\InstaClipStudio\tools`).
Custom locations can be set in the Setup tab.

Exports are saved to `Documents\Insta Clip Studio\Projects\Project_<date>`.
To update: re-upload changed files to the repo (same names overwrite) and run the workflow again.

## Models by language
- **Urdu**: Whisper large-v3 (faster-whisper). Cohere Transcribe has no Urdu.
- **Arabic**: Cohere Transcribe Arabic (July 2026) if set up, else Whisper.
- **English**: Cohere Transcribe if set up, else Whisper.
Cohere models are gated: add a free Hugging Face token in Setup and accept the terms on both model pages.
Cohere models give no timestamps, so subtitle timing comes from voice-activity detection.

## Translate tab
Gemini (or OpenAI / Claude / Groq / OpenRouter / Ollama). Lines are sent with their on-screen duration; results are cached.


## Cohere Transcribe troubleshooting

If Cohere fails, the Transcribe status now shows Python's recent diagnostic output instead of only a generic exit-code message. For gated-model errors, log in to Hugging Face, accept the conditions on the model page for the selected language, create a Read token from that same account, save it in Setup, and retry. For low-VRAM errors, close GPU-heavy applications and retry; the runner uses smaller batches on GPUs with less than 8 GB VRAM.
