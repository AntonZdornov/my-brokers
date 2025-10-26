# from TTS.api import TTS
# import os
# os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)


# def record():
# # generate speech by cloning a voice using default settings
#     tts.tts_to_file(text="It took me quite a long time to develop a voice, and now that I have it I'm not going to be silent.",
#                     file_path="output.wav",
#                     speaker_wav="assets/voice_example/male_01.wav",
#                     language="en")