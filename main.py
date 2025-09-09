from services.music import createSet
from llm_models.chat_tts import record


def main():
    model = input("Music-1,Stories-2: ").strip()

    if model == "1":
        createSet()
    elif model == "2":
        record()


if __name__ == "__main__":
    main()
