# import torch
# import ChatTTS
# import torchaudio
# import numpy as np
# import os
# from datetime import datetime

# # ---------- жёсткие настройки окружения ----------
# os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"  # пусть даже не думает о MPS
# os.environ["CHAT_TTS_DISABLE_MPS"] = "1"  # если переменная у модели читается
# os.environ["CUDA_VISIBLE_DEVICES"] = ""
# torch.set_default_dtype(torch.float32)

# def split_text_by_words(text, chunk_size=30):
#     words = text.split()
#     chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
#     return chunks

# def to_44k(wav, orig_sr=24000, new_sr=44100):
#     if isinstance(wav, np.ndarray):
#         wav = torch.from_numpy(wav)
#     if wav.dim() == 1:
#         wav = wav.unsqueeze(0)  # [channels, time]
#     resampler = torchaudio.transforms.Resample(orig_freq=orig_sr, new_freq=new_sr)
#     return resampler(wav)


# def record():
#     chat = ChatTTS.Chat()
#     chat.load(
#         compile=False, device="cpu"
#     )  # если True, будет оптимизация, но дольше загрузка

#     code_max_new_token = 10000
#     text_max_new_token = 5000
#     manual_seed = 41
#     temperature = 0.2
#     top_P = 0.5
#     top_K = 50

#     # best
#     # code_max_new_token = 10000
#     # text_max_new_token = 5000
#     # manual_seed = 41 #42
#     # temperature = 0.2
#     # top_P = 0.6
#     # top_K = 30

#     # spk_emb = chat.sample_random_speaker()
#     # torch.save(spk_emb, "assets/voice_example/my_voice.pt")
#     spk_emb = torch.load("assets/voice_example/female_best.pt")

#     # Стабильно и чётко (озвучка текста):
#     # temperature=0.3–0.5, top_P=0.85–0.95, top_K=20–50, manual_seed=0

#     # Поживее/эмоциональнее:
#     # temperature=0.6–0.8, top_P=0.9–1.0, top_K=0/None, manual_seed=42

#     # Макс-детерминизм (тесты/сравнения):
#     # temperature=0.2–0.3, top_P=0.7–0.85, top_K=10–20, manual_seed=0

#     # Настройки голоса
#     params_infer_code = ChatTTS.Chat.InferCodeParams(
#         spk_emb=spk_emb,
#         manual_seed=manual_seed,
#         temperature=temperature,
#         top_P=top_P,
#         top_K=top_K,
#         stream_batch=28,
#         stream_speed=8000,
#         max_new_token=code_max_new_token,
#     )

#     # # Настройки стиля речи (эмоции/паузы)
#     params_refine_text = ChatTTS.Chat.RefineTextParams(
#         prompt="[break_3][oral_3]",  # [speed_2][oral_2][laugh_0][s_2]"
#         max_new_token=text_max_new_token,
#     )

#     filename = "assets/story_input/story.txt"

#     # Проверяем размер файла перед чтением
#     if os.path.getsize(filename) == 0:
#         raise ValueError("Файл пустой!")

#     with open(filename, "r", encoding="utf-8") as file:
#         text = file.read()

#         if not text.strip():  # вдруг там только пробелы или переносы строк
#             raise ValueError("empty file")

#     print(text)
#     text = split_text_by_words(text)
#     print(f"Text parts: {len(text)}")
#     # Генерация
#     wavs = chat.infer(
#         text,
#         params_infer_code=params_infer_code,
#         params_refine_text=params_refine_text,
#     )

#     audio = wavs[0] if isinstance(wavs, (list, tuple)) else wavs
    
#     print(f"wavs: {len(wavs)}")

#     audio_44k = to_44k(audio)

#     current_datetime = datetime.now()
#     hours = current_datetime.hour
#     minutes = current_datetime.minute

#     wavFileName = f"{hours}:{minutes}_code-token={code_max_new_token}_text-token={text_max_new_token}_manual_seed={manual_seed}_temperature={temperature}_top-P={top_P}_top-K={top_K}.wav"

#     # Сохраняем в файл
#     torchaudio.save(
#         f"assets/voice_output/{wavFileName}",
#         audio_44k,
#         44100,
#     )
#     print(f"Done: {wavFileName}")
