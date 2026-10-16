# Insta Clip Studio v1.0.8 — Export progress

- Added a visible export progress bar and live status text to the Export panel.
- Reports progress during browser-side frame rendering and updates the progress bar from FFmpeg's `-progress pipe:1` output during final MP4 encoding.
- Shows stages for preparation, rendering, audio preparation, FFmpeg encoding, thumbnail generation, completion, and failure.
- Adds accessible progress-bar attributes for assistive technology.
- Preserves the v1.0.7 project and independently movable subtitle controls.

Validation: inline JavaScript syntax checked with Node.js. A Windows/Tauri build and end-to-end export test still need to be run on Windows.
