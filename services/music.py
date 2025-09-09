# flake8: noqa
import argparse
import json
from sqlite3 import DataError
from google.youtube_uploader import (
    add_video_to_playlist,
    get_or_create_playlist,
    get_youtube_service,
    upload_video,
    DEFAULT_CATEGORY_ID,
)
from utils.auto_mix_utils import make_mix_simple, make_mix_beats
from utils.make_video_utils import make_video_ffpy
from agents.agent_music import get_set_name


def createSet():
    print("Style:")
    print("1) Drum And Bass")
    print("2) ChillStep")
    print("3) Lofi")

    style = input("Style number: ").strip()
    if style == "1":
        style = "Drum&Bass"
    elif style == "2":
        style = "ChillStep"
    elif style == "3":
        style = "Lofi"
    else:
        print("Error")

    result = get_set_name(style)

    title = result.get("title", "").strip()
    description = result.get("description", "").strip()
    tags = result.get("hashtags", "").strip()

    tags = [t.strip() for t in tags.split(",") if t.strip()]
    hashtagsforDescription = " ".join(f"#{tag}" for tag in tags)
    description = f"🔥{description}\n\n{hashtagsforDescription}"

    if not title:
        print("⚠️ No title")
        return

    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Hashtags: {tags}")
    numberOfSet = input("Enter Set number: ")
    title = f"{style} Set#{numberOfSet} - {title}"
    print(f"Title: {title}")

    print("Mode:")
    print("1) simple")
    print("2) beats")
    mode = input("Mode number: ")
    if mode == "1":
        mode = "simple"
    elif mode == "2":
        mode = "beats"
    else:
        print("Error")
        return
    print("Selected mode:", mode)

    print("Playlists:")
    print("1) Lofi")
    print("2) ChillStep")
    print("3) DrumAndBass")

    playlist = input("Playlist number: ")
    if playlist == "1":
        playlist = "simple"
    elif playlist == "2":
        playlist = "beats"
    else:
        print("Error")
        return

    print("Selected Playlist:", mode)

    if mode == "simple":
        print("make_mix_simple")
        make_mix_simple("assets/tracks/", "assets/sets/mix.mp3")
    else:
        print("make_mix_beats")
        make_mix_beats("assets/tracks/", "assets/sets/mix.mp3")

    make_video_ffpy(
        "assets/images/1.png", "assets/sets/mix.mp3", "assets/videos/set.mp4"
    )

    youtube = get_youtube_service()

    try:
        video_id = upload_video(
            youtube=youtube,
            file_path="assets/videos/set.mp4",
            title=title,
            description=description,
            tags=tags,
            privacy_status="public",  # "public" "private"-for tests
            category_id=DEFAULT_CATEGORY_ID,
            made_for_kids=False,
        )

        # if args.thumbnail:
        #     try:
        #         # set_thumbnail(youtube, video_id, args.thumbnail)
        #         print("Preview setted.")
        #     except HttpError as e:
        #         print(f"Failed to set preview: {e}")

        if playlist:
            pl_id = get_or_create_playlist(youtube, playlist, "")
            add_video_to_playlist(youtube, pl_id, video_id)
            print(f"Video added to playlist: {playlist}")

        print(f"https://youtube.com/watch?v={video_id}")

    except DataError as e:
        print(f"HTTP Error: {e}")
        if e.resp and hasattr(e, "content") and e.content:
            try:
                print(json.loads(e.content.decode("utf-8")))
            except Exception:
                pass
