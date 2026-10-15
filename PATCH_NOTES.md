# Insta Clip Studio — v1.0.4

## Cohere Transcribe failure diagnostics and stability

- The app now captures recent stdout/stderr from the Cohere Python process and returns the underlying failure details in the Transcribe status instead of only the generic exit-code hint.
- The status area can display multiline diagnostics and tracebacks.
- The Python runner prints stages (audio preparation, model loading, GPU/dtype/batch choice) so failed runs point to the actual stage.
- Batch size is reduced to 1 on systems with less than 8 GB VRAM, and to 1 on CPU-only systems; GPUs with more memory use a conservative batch of 4.
- CUDA dtype selection now prefers BF16 only when the installed PyTorch runtime reports support, otherwise FP16; CPU inference retains FP32.
- Batch failures clear the CUDA cache before retrying one chunk at a time.
- All previous v1.0.3 export, context-aware translation, and Islamic honorific changes are retained.

## Verification

- Python script syntax checked with `py_compile`; frontend JavaScript syntax checked with Node.
- JSON configuration parsed and ZIP integrity checked.
- No Windows Tauri compile or live Cohere model run was possible in this environment; build with GitHub Actions and retry a short clip to read the now-visible precise error.
