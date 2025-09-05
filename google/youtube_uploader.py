from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.auth.exceptions
import pickle


# === Настройки ===
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
CLIENT_SECRET_FILE = "client_secret.json"  # скачанный из Google Cloud
TOKEN_FILE = "token.pickle"

# Категория 10 = Music
DEFAULT_CATEGORY_ID = "10"


def get_youtube_service():
    creds = None
    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except google.auth.exceptions.RefreshError:
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video(
    youtube,
    file_path: str,
    title: str,
    description: str,
    tags: Optional[list[str]] = None,
    privacy_status: str = "public",
    category_id: str = DEFAULT_CATEGORY_ID,
    made_for_kids: bool = False,
):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id,
            **({"tags": tags} if tags else {}),
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(
        file_path,
        chunksize=1024 * 1024 * 8,  # 8MB чанки (резюмируемая загрузка)
        resumable=True,
        mimetype="/assets/video/mp4",  # желательно H.264 + AAC
    )

    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded: {int(status.progress() * 100)}%")
    video_id = response["id"]
    print(f"Done! video_id: {video_id}")
    return video_id


def set_thumbnail(youtube, video_id: str, thumbnail_path: str):
    media = MediaFileUpload(thumbnail_path, resumable=False)
    resp = youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    return resp


def get_or_create_playlist(youtube, title: str, description: str = "") -> str:
    # Ищем плейлист по названию
    resp = (
        youtube.playlists()
        .list(part="snippet,contentDetails", mine=True, maxResults=50)
        .execute()
    )
    for item in resp.get("items", []):
        if item["snippet"]["title"] == title:
            return item["id"]

    # Создаём, если нет
    body = {
        "snippet": {"title": title, "description": description},
        "status": {"privacyStatus": "public"},
    }
    created = youtube.playlists().insert(part="snippet,status", body=body).execute()
    return created["id"]


def add_video_to_playlist(youtube, playlist_id: str, video_id: str):
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {"kind": "youtube#video", "videoId": video_id},
        }
    }
    youtube.playlistItems().insert(part="snippet", body=body).execute()
