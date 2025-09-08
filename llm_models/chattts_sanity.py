# chattts_sanity.py
import os, sys, re, math, time, json
import numpy as np
import torch
import soundfile as sf
import ChatTTS

# ---------- жёсткие настройки окружения ----------
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"  # пусть даже не думает о MPS
os.environ["CHAT_TTS_DISABLE_MPS"] = "1"  # если переменная у модели читается
torch.set_default_dtype(torch.float32)

SR_IN = 24000
SR_OUT = 44100  # если нужно сразу 44.1 kHz

ALLOWED = r"[^a-zA-Z0-9\s\.\,\?\:\;\-\'\"\(\)]"


def sanitize(s: str) -> str:
    s = s.replace("!", ".")
    s = re.sub(ALLOWED, "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def save_wav(path, wav, sr=SR_IN):
    # numpy/torch -> float32 numpy mono
    import numpy as np

    if isinstance(wav, torch.Tensor):
        wav = wav.detach().to(torch.float32).cpu().numpy()
    else:
        wav = np.asarray(wav, dtype=np.float32)
    # [T] или [C,T]? приводим к [T]
    if wav.ndim == 2:
        if wav.shape[0] == 1:
            wav = wav[0]
        elif wav.shape[1] == 1:
            wav = wav[:, 0]
        else:
            wav = wav.mean(axis=0)  # safety
    # sanitize амплитуды
    wav = np.nan_to_num(wav, nan=0.0, posinf=0.0, neginf=0.0)
    wav = np.clip(wav, -1.0, 1.0)
    sf.write(path, wav, sr, subtype="PCM_16")


def resample44k(mono_24k: np.ndarray) -> np.ndarray:
    # простой и быстрый ресемплинг с помощью soundfile/libsndfile (прямой — нет)
    # тут сделаем линейный upsample (хватает для голоса)
    import numpy as np

    in_sr, out_sr = SR_IN, SR_OUT
    if in_sr == out_sr:
        return mono_24k
    ratio = out_sr / in_sr
    T_in = mono_24k.shape[0]
    T_out = int(math.floor(T_in * ratio))
    x = np.linspace(0, 1, T_in, endpoint=False)
    xi = np.linspace(0, 1, T_out, endpoint=False)
    return np.interp(xi, x, mono_24k).astype(np.float32)


def rms_db(wav) -> float:
    if isinstance(wav, torch.Tensor):
        wav = wav.detach().to(torch.float32).cpu().numpy()
    wav = wav.astype(np.float32)
    if wav.ndim == 2:
        wav = wav.mean(axis=0)
    e = float(np.sqrt(np.mean(np.square(wav)))) + 1e-12
    return 20.0 * math.log10(e)


def try_generate(chat, text: str, seed: int, temperature: float, refine_prompt: str):
    torch.manual_seed(seed)
    spk = chat.sample_random_speaker()
    code = ChatTTS.Chat.InferCodeParams(
        spk_emb=spk, temperature=temperature, top_P=0.55, top_K=20
    )
    # ref  = ChatTTS.Chat.RefineTextParams(prompt=refine_prompt)
    out = chat.infer(text, params_infer_code=code, params_refine_text=None)
    wav = out[0] if isinstance(out, (list, tuple)) else out
    return wav


def main():
    print(">>> Loading ChatTTS on CPU (compile=False)...")
    chat = ChatTTS.Chat()
    chat.load(compile=False, device="cpu")

    text = "Hello, my name is Anton. This is a clean sanity test of Chat T T S."
    text = sanitize(text)

    torch.manual_seed(7)
    spk = chat.sample_random_speaker()

    code = ChatTTS.Chat.InferCodeParams(
        spk_emb=spk, temperature=0.10, top_P=0.55, top_K=20
    )

    # вариант А: совсем без refine
    wavs = chat.infer(
        "Hello, my name is Anton.", params_infer_code=code, params_refine_text=None
    )

    # Перебор настроек до понятной речи
    # seeds = [7, 42, 1111, 2222, 3333]
    # temps = [0.10, 0.12, 0.15]
    # refine_prompts = ["", "[oral_2]"]  # сначала вообще без refine

    # wav_best = None
    # tried = 0
    # for rp in refine_prompts:
    #     for seed in seeds:
    #         for t in temps:
    #             tried += 1
    #             print(f" -> attempt {tried}: seed={seed}, temp={t}, refine='{rp or ''}'")
    #             try:
    #                 wav = try_generate(chat, text, seed, t, rp)
    #                 # nan/inf guard
    #                 if isinstance(wav, np.ndarray):
    #                     arr = wav
    #                 else:
    #                     arr = wav.detach().to(torch.float32).cpu().numpy()
    #                 arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    #                 # громкость
    #                 level = rms_db(arr)
    #                 print(f"    rms ~ {level:.1f} dBFS")
    #                 if level < -60.0:
    #                     print("    too quiet / likely wrong — trying next...")
    #                     continue
    #                 wav_best = arr
    #                 raise StopIteration
    #             except StopIteration:
    #                 break
    #             except Exception as e:
    #                 print("    exception:", e)
    #                 continue
    #         if wav_best is not None: break
    #     if wav_best is not None: break

    # if wav_best is None:
    #     print("!!! Still no valid speech. We need to re-check weights/cache.")
    #     sys.exit(2)

    # сохраняем 24k и 44.1k
    save_wav("chattts_24k.wav", wavs, SR_IN)
    # save_wav("chattts_44k.wav", resample44k(wavs), SR_OUT)
    print("✅ Saved: chattts_24k.wav, chattts_44k.wav")


if __name__ == "__main__":
    main()
