import torch
import ChatTTS
import torchaudio
import numpy as np
import os

# ---------- жёсткие настройки окружения ----------
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"  # пусть даже не думает о MPS
os.environ["CHAT_TTS_DISABLE_MPS"] = "1"  # если переменная у модели читается
os.environ["CUDA_VISIBLE_DEVICES"] = ""
torch.set_default_dtype(torch.float32)

def load_wav_1d(path: str, target_sr: int = 24000, device: str = "cpu") -> torch.Tensor:
    wav, sr = torchaudio.load(path)           # [C, T]
    if wav.size(0) > 1:                       # стерео -> моно
        wav = wav.mean(dim=0, keepdim=False)  # [T]
    else:
        wav = wav.squeeze(0)                  # [T]
    if sr != target_sr:
        wav = torchaudio.functional.resample(wav.unsqueeze(0), sr, target_sr).squeeze(0)  # [T]
    return wav.to(device).to(torch.float32) 

def to_44k(wav, orig_sr=24000, new_sr=44100):
    if isinstance(wav, np.ndarray):
        wav = torch.from_numpy(wav)
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)  # [channels, time]
    resampler = torchaudio.transforms.Resample(orig_freq=orig_sr, new_freq=new_sr)
    return resampler(wav)


def record():
    chat = ChatTTS.Chat()
    chat.load(
        compile=False, device="cpu"
    )  # если True, будет оптимизация, но дольше загрузка

    wav_1d = load_wav_1d("assets/voice_example/male_01.wav", target_sr=24000, device="cpu")
    # Фиксируем сид, чтобы голос был стабильным
    rand_spk = chat.sample_audio_speaker(wav_1d)

    # Настройки голоса
    params_infer_code = ChatTTS.Chat.InferCodeParams(
        spk_emb=rand_spk, manual_seed=2500, temperature=0.3, top_P=0.7, top_K=20
    )

    # # Настройки стиля речи (эмоции/паузы)
    params_refine_text = ChatTTS.Chat.RefineTextParams(
        prompt="[oral_2][laugh_0][break_4][s_2]"
    )

    filename = "assets/story_input/story.txt"

    # Проверяем размер файла перед чтением
    if os.path.getsize(filename) == 0:
        raise ValueError("Файл пустой!")

    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()

        if not text.strip():  # вдруг там только пробелы или переносы строк
            raise ValueError("empty file")

    print(text)
    # Генерация
    wavs = chat.infer(
        [text],
        params_infer_code=params_infer_code,
        params_refine_text=params_refine_text,
    )

    audio = wavs[0] if isinstance(wavs, (list, tuple)) else wavs
    audio_44k = to_44k(audio)

    # Сохраняем в файл
    torchaudio.save("story.wav", audio_44k, 44100)
    print("Done: story.wav")
