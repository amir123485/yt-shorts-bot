import json
import os
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_credentials():
    return Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=SCOPES,
    )

def get_publish_time():
    # Schedule 4 hours from now, on the hour
    now = datetime.now(timezone.utc)
    publish_at = (now + timedelta(hours=4)).replace(minute=0, second=0, microsecond=0)
    return publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")

def upload_video(script_path="script.json", video_path="short.mp4"):
    with open(script_path) as f:
        script = json.load(f)

    youtube = build("youtube", "v3", credentials=get_credentials())

    title = script["title"]
    if "#Shorts" not in title and "#shorts" not in title.lower():
        title = (title[:85] + " #Shorts").strip()

    description = script.get("description", "")
    if "#Shorts" not in description:
        description += "\n\n#Shorts #AItools #AI #ChatGPT"

    publish_at = get_publish_time()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": script.get("tags", []) + ["shorts", "youtubeshorts", "AI tools"],
            "categoryId": "28",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)

    print(f"[INFO] Uploading as PRIVATE + SCHEDULED")
    print(f"[INFO] Title: {title}")
    print(f"[INFO] Publish at: {publish_at}")

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[OK] https://youtube.com/shorts/{video_id}")
    print(f"[OK] Scheduled for: {publish_at}")
    return video_id

if __name__ == "__main__":
    upload_video()
