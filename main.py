import argparse
import json
from sqlite3 import DataError
from google.youtube_uploader import add_video_to_playlist, get_or_create_playlist, get_youtube_service, upload_video, DEFAULT_CATEGORY_ID
from utils.auto_mix_utils import make_mix_simple, make_mix_beats
from utils.make_video_utils import make_video_ffpy
from agents.agent_music import get_set_name

def main():
    result = get_set_name()
    title = result.get("title", "").strip()
    description = result.get("description","").strip()
    tags = result.get("hashtags","").strip()
    tags = [t.strip() for t in tags.split(",") if t.strip()]
    hashtagsforDescription = " ".join(f"#{tag}" for tag in tags)
    description = f"🔥{description}\n\n{hashtagsforDescription}"
    if not title:
        print("⚠️ No title - exit the function")
        return  

    numberOfSet = input("Enter Set number: ")
    title = f"Chillstep Set#{numberOfSet} - {title}"
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Hashtags: {tags}")

    parser = argparse.ArgumentParser(description="Auto DJ: simple or beat-aware mixing")
    parser.add_argument("folder", help="Папка с музыкой (mp3/wav/flac/m4a/aac)")
    parser.add_argument(
        "output", help="Имя выходного файла (например, output/mix.mp3 или mix.wav)"
    )
    parser.add_argument(
        "--mode",
        choices=["simple", "beats"],
        default="simple",
        help="Режим: 'simple' — кроссфейд по времени; 'beats' — по ударам",
    )
    parser.add_argument(
        "--crossfade-ms",
        type=int,
        default=8000,
        help="Длина кроссфейда в миллисекундах (для simple)",
    )
    parser.add_argument(
        "--xfade-beats",
        type=int,
        default=16,
        help="Длина кроссфейда в ударах (для beats)",
    )
    parser.add_argument(
        "--bitrate",
        default="320k",
        help="Битрейт MP3 для simple режима (по умолчанию 320k)",
    )
    parser.add_argument("--playlist", default="", help="Playlist title to add the video to (create if missing)")
    parser.add_argument("--playlist_desc", default="", help="Playlist description (used only if we create it)")
    args = parser.parse_args()

    if args.mode == "simple":
        make_mix_simple(
            args.folder,
            args.output,
            crossfade_ms=args.crossfade_ms,
            bitrate=args.bitrate,
        )
    else:
        make_mix_beats(args.folder, args.output, xfade_beats=args.xfade_beats)

    make_video_ffpy("images/1.png", "sets/mix.mp3", "videos/set.mp4")

    youtube = get_youtube_service()

    try:
        video_id = upload_video(
            youtube=youtube,
            file_path="videos/set.mp4",
            title=title,
            description=description,
            tags=tags,
            privacy_status="public", #"public" "private"-for tests
            category_id=DEFAULT_CATEGORY_ID,
            made_for_kids=False,
        )

        # if args.thumbnail:
        #     try:
        #         # set_thumbnail(youtube, video_id, args.thumbnail)
        #         print("Preview setted.")
        #     except HttpError as e:
        #         print(f"Failed to set preview: {e}")

        if args.playlist:
            pl_id = get_or_create_playlist(youtube, args.playlist, args.playlist_desc)
            add_video_to_playlist(youtube, pl_id, video_id)
            print(f"Video added to playlist: {args.playlist}")

        print(f"https://youtube.com/watch?v={video_id}")

    except DataError as e:
        print(f"HTTP Error: {e}")
        if e.resp and hasattr(e, 'content') and e.content:
            try:
                print(json.loads(e.content.decode("utf-8")))
            except Exception:
                pass


if __name__ == "__main__":
    main()
