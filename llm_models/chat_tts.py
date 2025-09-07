import torch
import ChatTTS
import torchaudio
import numpy as np

torch.set_default_dtype(torch.float32)

def to_44k(wav, orig_sr=24000, new_sr=44100):
    if isinstance(wav, np.ndarray):
        wav = torch.from_numpy(wav)
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)  # [channels, time]
    resampler = torchaudio.transforms.Resample(orig_freq=orig_sr, new_freq=new_sr)
    return resampler(wav)

def record():
    chat = ChatTTS.Chat()
    chat.load(compile=False,device="cpu")  # если True, будет оптимизация, но дольше загрузка

    # Фиксируем сид, чтобы голос был стабильным
    # torch.manual_seed(512)
    rand_spk = chat.sample_random_speaker()

    # Настройки голоса
    params_infer_code = ChatTTS.Chat.InferCodeParams(
        spk_emb=rand_spk,manual_seed=2500, temperature=0.3, top_P=0.4, top_K=20
    )

    # # Настройки стиля речи (эмоции/паузы)
    params_refine_text = ChatTTS.Chat.RefineTextParams(
        prompt="[oral_2][laugh_0][break_4][s_2]"
    )

    # Генерация
    wavs = chat.infer(
        "[s_2]There were dough smudges on the ceiling and a cloud of flour dusting his spectacles.[break_4] He was trying to perfect his",
        params_infer_code=params_infer_code,
        params_refine_text=params_refine_text,
    )
    
    audio = wavs[0] if isinstance(wavs, (list, tuple)) else wavs
    audio_44k = to_44k(audio)

    # Сохраняем в файл
    torchaudio.save("story.wav", audio_44k, 44100)
    print("Done: story.wav")