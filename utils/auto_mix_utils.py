import os
import tempfile
import numpy as np
from utils.utils import load_tracks
from pydub import AudioSegment
import librosa
import soundfile as sf


# ====== Простой режим: фиксированный кроссфейд по времени (pydub) ======
# Требует: pip install pydub  и установленный ffmpeg
def make_mix_simple(
    folder: str, output: str, crossfade_ms: int = 8000, bitrate: str = "320k"
):
    from pydub import AudioSegment, effects

    files = load_tracks(folder)
    if not files:
        raise RuntimeError("Нет треков в папке.")

    files.sort(key=lambda x: os.path.basename(x).lower())

    print(f"🔹 Simple: найдено {len(files)} треков, crossfade={crossfade_ms} мс")

    mix = None
    for i, path in enumerate(files, 1):
        track = AudioSegment.from_file(path)
        track = effects.normalize(track)
        mix = track if mix is None else mix.append(track, crossfade=crossfade_ms)
        print(f"[{i}/{len(files)}] {os.path.basename(path)}")

    # формат выбираем по расширению выходного файла
    ext = os.path.splitext(output)[1].lstrip(".").lower() or "mp3"
    export_args = {"format": ext}
    if ext == "mp3":
        export_args["bitrate"] = bitrate
    mix.export(output, **export_args)
    print(f"✅ Готово: {output}")


# ====== Режим по битам: кроссфейд по ударам (librosa) ======
# Требует: pip install librosa soundfile numpy
def make_mix_beats(
    folder: str, output: str, xfade_beats: int = 16, mp3_bitrate: str = "320k"
):
    files = load_tracks(folder)
    if not files:
        raise RuntimeError("Нет треков в папке.")

    files.sort(key=lambda x: os.path.basename(x).lower())

    print(f"🔹 Beat-aware: {len(files)} треков, xfade_beats={xfade_beats}")

    mix = None  # shape: (channels, samples)
    sr_global = None

    for i, path in enumerate(files, 1):
        # СТЕРЕО загрузка: y shape -> (samples,) или (channels, samples)
        y, sr = librosa.load(path, sr=None, mono=False)
        if y.ndim == 1:
            y = y[np.newaxis, :]  # -> (1, N)
        if sr_global is None:
            sr_global = sr

        # Для анализа темпа делаем моно-микс (НЕ для звука)
        y_mono = librosa.to_mono(y)  # (N,)
        tempo, beats = librosa.beat.beat_track(y=y_mono, sr=sr, units="time")
        tempo_num = float(np.atleast_1d(tempo)[0])
        beats = np.asarray(beats, dtype=float).ravel()
        print(f"[{i}/{len(files)}] {os.path.basename(path)} — ~{tempo_num:.1f} BPM")

        if mix is None:
            mix = y.astype(np.float32)
            continue

        # длина кроссфейда: N-й удар или fallback 8 сек
        if beats.size > xfade_beats:
            idx = min(xfade_beats, beats.size - 1)
            xfade = int(sr * float(beats[idx]))
        else:
            xfade = int(sr * 8.0)

        # Подгоняем каналы (вдруг разные числа каналов)
        ch_mix, ch_y = mix.shape[0], y.shape[0]
        if ch_mix != ch_y:
            # простой даунмикс/апмикс
            if ch_mix == 1 and ch_y == 2:
                mix = np.vstack([mix, mix])  # mono -> pseudo-stereo
            elif ch_mix == 2 and ch_y == 1:
                y = np.vstack([y, y])  # mono -> pseudo-stereo

        # Выделяем куски для кроссфейда по последней оси (samples)
        a = mix[:, -xfade:] if mix.shape[1] >= xfade else mix
        b = y[:, :xfade] if y.shape[1] >= xfade else y

        n = min(a.shape[1], b.shape[1])
        if n == 0:
            mix = np.concatenate([mix, y], axis=1)
            continue

        # Синусная кривая — плавный fade
        t = np.linspace(0.0, np.pi, n, dtype=np.float32)
        fade = (1.0 - np.cos(t)) / 2.0  # 0..1
        fade = fade[np.newaxis, :]  # -> (1, n) для broadcast

        a = a[:, -n:] * (1.0 - fade)
        b = b[:, :n] * fade

        mixed_tail = a + b
        mix = np.concatenate([mix[:, :-(n)], mixed_tail, y[:, n:]], axis=1)

    # Нормализация (бережная)
    peak = float(np.max(np.abs(mix))) or 1.0
    mix = (mix / peak * 0.98).astype(np.float32)

    # Экспорт
    ext = os.path.splitext(output)[1].lower()
    if ext == ".mp3":
        # Через временный WAV -> pydub -> MP3 (битрейт настраиваемый)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_wav = tmp.name
        try:
            # soundfile ждёт (samples, channels), поэтому транспонируем
            sf.write(tmp_wav, mix.T, sr_global, subtype="PCM_16")
            seg = AudioSegment.from_wav(tmp_wav)
            seg.export(output, format="mp3", bitrate=mp3_bitrate)
        finally:
            try:
                os.remove(tmp_wav)
            except Exception as e:
                print(f"Exception: {e}")
                pass
        print(f"✅ MP3 сохранён: {output} @ {mp3_bitrate}")
    else:
        # WAV/FLAC напрямую
        data = mix.T  # (samples, channels)
        if ext not in (".wav", ".flac"):
            print("ℹ️ Лучше указать .mp3/.wav/.flac. Сохраняю .wav.")
            output = os.path.splitext(output)[0] + ".wav"
        sf.write(output, data, sr_global)
        print(f"✅ Сохранено: {output}")
