# v1.1.0 test report

## Passed in the available environment
- `node --check` on the embedded frontend JavaScript.
- Python syntax compilation for the three shipped Python helpers.
- JSON parsing for `package.json`, `src-tauri/tauri.conf.json`, and `src-tauri/capabilities/default.json`.
- FFmpeg smoke test: a still image plus 2-second audio produced a valid MP4 background clip.
- FFmpeg smoke test: a short video plus audio encoded to H.264/AAC MP4 at the input dimensions.
- ZIP integrity test.

## Not run
- Rust/Tauri compilation: Cargo/Rust toolchain is not installed in this environment.
- Windows installer execution.
- End-to-end GUI automation for project switching, media relinking, audio/video synchronization, subtitle drag handles, AI API calls, and 1080p export quality.

Passing these checks is not equivalent to a complete Windows acceptance test.
