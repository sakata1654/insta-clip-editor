# Cohere Transcribe (English / Arabic) with VAD-based timestamp reconstruction.
# Uses the model's optimized transcribe() path when available, while retaining
# VAD segment start/end times for the editor's subtitle workflow.
import sys, json, os, traceback, time
import numpy as np


def log(message):
    print(message, flush=True)


def vad_segments(audio, sr):
    try:
        from faster_whisper.vad import get_speech_timestamps, VadOptions
        ts = get_speech_timestamps(
            audio,
            VadOptions(min_silence_duration_ms=400, speech_pad_ms=200, max_speech_duration_s=20),
        )
        segs = [(t['start'] / sr, t['end'] / sr) for t in ts]
    except Exception as e:
        log(f"VAD unavailable ({type(e).__name__}: {e}); using fixed windows")
        n = len(audio) / sr
        segs = [(float(i), float(min(n, i + 15.0))) for i in np.arange(0, n, 15.0)]
    out = []
    for s, e in segs:
        if out and (s - out[-1][1] < 0.35 and e - out[-1][0] < 12.0):
            out[-1] = (out[-1][0], e)
        elif out and (e - s < 0.8 and e - out[-1][0] < 12.0):
            out[-1] = (out[-1][0], e)
        else:
            out.append((s, e))
    return out


def clean_text(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ('text', 'transcription', 'generated_text'):
            if isinstance(value.get(key), str):
                return value[key].strip()
    return str(value).strip() if value is not None else ''


def main():
    started = time.perf_counter()
    log('Reading extracted audio…')
    with open(sys.argv[1], encoding='utf-8') as f:
        a = json.load(f)
    import soundfile as sf
    audio, sr = sf.read(a['audio'], dtype='float32')
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != 16000:
        # Rust currently extracts at 16 kHz; this guard also protects future callers.
        try:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000).astype(np.float32, copy=False)
        except Exception as e:
            raise RuntimeError(f'Audio must be resampled from {sr} Hz to 16000 Hz, but librosa resampling failed: {e}')
        log(f'Resampled audio from {sr} Hz to 16000 Hz')
        sr = 16000

    vad_started = time.perf_counter()
    segs = vad_segments(audio, sr)
    log(f"Audio duration: {len(audio) / sr:.1f}s; {len(segs)} speech segments; VAD {time.perf_counter()-vad_started:.1f}s")
    if not segs:
        with open(a['out'], 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)
        log('DONE')
        return

    import torch
    from transformers import AutoProcessor, CohereAsrForConditionalGeneration
    mid = a['model_id']
    tok = os.environ.get('HF_TOKEN') or None
    if torch.cuda.is_available():
        try:
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        except Exception:
            vram_gb = 0.0
        try:
            bf16_ok = bool(torch.cuda.is_bf16_supported())
        except Exception:
            bf16_ok = False
        model_dtype = torch.bfloat16 if bf16_ok else torch.float16
        # Keep activation memory conservative on 4 GB GPUs. Larger VRAM can batch.
        batch_size = 1 if vram_gb < 6.0 else (2 if vram_gb < 10.0 else 4)
        log(f'CUDA available; VRAM {vram_gb:.1f} GB; dtype {model_dtype}; inference batch {batch_size}')
    else:
        model_dtype = torch.float32
        batch_size = 1
        log('CUDA unavailable; using CPU float32. Transcription will be substantially slower.')

    load_started = time.perf_counter()
    log(f'Loading model {mid}…')
    processor = AutoProcessor.from_pretrained(mid, token=tok)
    try:
        model = CohereAsrForConditionalGeneration.from_pretrained(
            mid, device_map='auto', token=tok, dtype=model_dtype
        )
    except TypeError:
        model = CohereAsrForConditionalGeneration.from_pretrained(mid, device_map='auto', token=tok)
    model.eval()
    log(f"MODEL {mid.split('/')[-1]} on {model.device}; load {time.perf_counter()-load_started:.1f}s")

    lang = a['lang']
    out = []
    # Process a few timestamped VAD regions per call. The model's native transcribe
    # implementation handles its own efficient inference/batching; the VAD boundaries
    # remain the timestamps used by the subtitle editor.
    group_size = max(batch_size, batch_size * 4)
    inference_started = time.perf_counter()
    inference_seconds = 0.0
    optimized = callable(getattr(model, 'transcribe', None))
    for i in range(0, len(segs), group_size):
        part = segs[i:i + group_size]
        chunks = [audio[max(0, int(s * sr)):min(len(audio), int(e * sr))] for s, e in part]
        t0 = time.perf_counter()
        texts = None
        if optimized:
            try:
                # Native implementation avoids our old per-segment generate loop.
                texts = model.transcribe(
                    processor=processor,
                    audio_arrays=chunks,
                    sample_rates=[sr] * len(chunks),
                    language=lang,
                    batch_size=batch_size,
                )
                if not isinstance(texts, (list, tuple)) or len(texts) != len(chunks):
                    texts = None
            except (TypeError, AttributeError, NotImplementedError) as e:
                log(f'Native transcribe API unavailable ({type(e).__name__}); using compatible generation path')
                optimized = False
            except Exception as e:
                # Fall back only for this group; do not rerun previously completed groups.
                log(f'Native transcribe group failed ({type(e).__name__}: {e}); retrying this group with generate()')
                texts = None
        if texts is None:
            texts = []
            for c in chunks:
                inputs = processor(c, sampling_rate=sr, return_tensors='pt', language=lang)
                inputs.to(model.device, dtype=model.dtype)
                with torch.inference_mode():
                    res = model.generate(**inputs, max_new_tokens=256)
                texts.append(processor.decode(res, skip_special_tokens=True, language=lang))
        inference_seconds += time.perf_counter() - t0
        for (s, e), text in zip(part, texts):
            text = clean_text(text)
            if text:
                out.append({'s': s, 'e': e, 't': text})
        pct = min(99, int((i + len(part)) / len(segs) * 100))
        elapsed = time.perf_counter() - inference_started
        completed = i + len(part)
        log(f'progress = {pct}%')
        log(f"COHERE_METRICS completed_segments={completed}/{len(segs)} group_seconds={time.perf_counter()-t0:.1f} inference_elapsed={elapsed:.1f}s")

    with open(a['out'], 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)
    log(f"COHERE_TIMING total={time.perf_counter()-started:.1f}s inference={inference_seconds:.1f}s segments={len(segs)} output={len(out)}")
    log('DONE')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        log(f'COHERE_ERROR: {type(exc).__name__}: {exc}')
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)
