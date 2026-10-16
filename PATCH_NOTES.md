# Insta Clip Studio v1.1.0 — Stabilization Release

This release consolidates fixes against the v1.0.9 source project.

## Included
- Keeps the Assets workflow for image, video, and audio/MP3 imports.
- Restores saved project source media and external audio paths when available, rehydrates overlay media, and reloads the selected image background.
- A new project now clears prior media, overlays, audio, subtitle data, and editing state rather than leaving stale media behind.
- Project autosave now refreshes source-media metadata as well as editor state and asset references.
- Project JSON import attempts to restore its source video, assets, and active external audio.
- Dual subtitle source and translation have separate X/Y controls and independent preview drag targeting. The controls are saved with project state.
- Export progress updates are mirrored to a render cover so the preview does not visibly play during export; project switching is blocked during export to avoid corrupting the live render state.
- Version numbers are synchronized to 1.1.0.

## Important limitation
The export compositor still uses the existing canvas/MediaRecorder capture to preserve the app's custom effects and subtitle styles, then uses FFmpeg for final audio processing and MP4 encoding. This release does **not** yet replace that capture pipeline with a fully detached FFmpeg-only renderer, and it does not permit switching projects during an active export. The render cover hides preview playback, but it is not a substitute for an isolated background-rendering architecture.

## Validation performed
- Inline JavaScript syntax check with Node.js.
- Python syntax checks for the transcription and environment scripts.
- JSON parsing for package, Tauri configuration, and capabilities.
- ZIP integrity check.

## Not yet verified
A Windows/Tauri build and full end-to-end tests for video playback, asset relinking, subtitle dragging, transcription, and final export must run on Windows. Cargo was unavailable in the patching environment, so this is a validated source package, not a verified Windows installer.
- Removed the redundant legacy transcription handlers so one engine-routed transcription path controls the Generate subtitles button.
- Sentence-grouping is applied once to generated subtitle segments, while preserving word timings where possible.
- Renamed the obsolete hidden translator status node so progress updates target the active Translate tab.
