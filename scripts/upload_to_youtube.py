"""
upload_to_youtube.py
Uploads short.mp4 as a scheduled private Short.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_credentials():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    return creds

def get_best_publish_time():
    """
    Schedule for a good Shorts time (around 18:00 UTC next available slot).
    You can later change this logic.
    """
    now = datetime.now(timezone.utc)
    # Schedule 3 hours from now (safe default)
    publish_at = now + timedelta(hours=3)
    # Round to next full hour
    publish_at = publish_at.replace(minute=0, second=0, microsecond=0)
    return publish_at.isoformat().replace("+00:00", "Z")

def upload_video(script_path="script.json", video_path="short.mp4"):
    with open(script_path) as f:
        script = json.load(f)

    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    title = script["title"]
    if "#Shorts" not in title and "#shorts" not in title:
        title = title[:90] + " #Shorts"

    description = script.get("description", "")
    if "#Shorts" not in description:
        description += "\n\n#Shorts #AItools #AI"

    publish_at = get_best_publish_time()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": script.get("tags", []) + ["shorts", "youtubeshorts", "AI tools"],
            "categoryId": "28",  # Science & Technology
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)

    print(f"[INFO] Uploading (scheduled): {title}")
    print(f"[INFO] Will publish at: {publish_at}")

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  Upload {pct}%")

    video_id = response["id"]
    print(f"[OK] Uploaded as private + scheduled!")
    print(f"     https://youtube.com/shorts/{video_id}")
    print(f"     Publish time: {publish_at}")
    return video_id

if __name__ == "__main__":
    upload_video()
