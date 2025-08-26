from pydub import AudioSegment, effects
import os

SUPPORTED = (".mp3", ".wav", ".flac", ".m4a", ".aac")


def load_tracks(folder: str):
    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(SUPPORTED)
    ]
    files.sort(
        key=lambda x: os.path.basename(x).lower()
    )  # можно заменить на случайный порядок: random.shuffle(files)
    return files


def normalize(track: AudioSegment) -> AudioSegment:
    """Выравнивает громкость трека"""
    return effects.normalize(track)
