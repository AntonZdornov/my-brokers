import argparse
from auto_dj import make_mix_simple, make_mix_beats

def main():
    parser = argparse.ArgumentParser(description="Auto DJ: simple or beat-aware mixing")
    parser.add_argument("folder", help="Папка с музыкой (mp3/wav/flac/m4a/aac)")
    parser.add_argument("output", help="Имя выходного файла (например, output/mix.mp3 или mix.wav)")
    parser.add_argument("--mode", choices=["simple", "beats"], default="simple",
                        help="Режим: 'simple' — кроссфейд по времени; 'beats' — по ударам")
    parser.add_argument("--crossfade-ms", type=int, default=8000,
                        help="Длина кроссфейда в миллисекундах (для simple)")
    parser.add_argument("--xfade-beats", type=int, default=16,
                        help="Длина кроссфейда в ударах (для beats)")
    parser.add_argument("--bitrate", default="320k",
                        help="Битрейт MP3 для simple режима (по умолчанию 320k)")
    args = parser.parse_args()

    if args.mode == "simple":
        make_mix_simple(args.folder, args.output, crossfade_ms=args.crossfade_ms, bitrate=args.bitrate)
    else:
        make_mix_beats(args.folder, args.output, xfade_beats=args.xfade_beats)

if __name__ == "__main__":
    main()
