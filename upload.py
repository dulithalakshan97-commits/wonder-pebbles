#!/usr/bin/env python3
"""Upload out/video.mp4 to YouTube using the metadata made by make_video.py.

Needs env vars YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (GitHub secrets).
PRIVACY = private (default) | unlisted | public
"""
import json
import os
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"


def main():
    creds = Credentials(
        None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    meta = json.load(open(os.path.join(OUT, "metadata.json")))
    privacy = os.environ.get("PRIVACY", "private") or "private"
    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"][:30],
            "categoryId": "27",  # Education
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": True,
            "embeddable": True,
            "license": "youtube",
        },
    }
    media = MediaFileUpload(os.path.join(OUT, "video.mp4"), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  uploaded {int(status.progress() * 100)}%")
    vid = resp["id"]
    url = f"https://youtu.be/{vid}"
    print(f"Uploaded: {url} (privacy={resp['status']['privacyStatus']})")
    thumb = os.path.join(OUT, "thumbnail.jpg")
    if os.path.exists(thumb):
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb, mimetype="image/jpeg")).execute()
            print("  custom thumbnail set")
        except HttpError as e:
            print(f"  thumbnail not set (verify your channel by phone to enable custom thumbnails): {e.reason}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write(f"### Uploaded episode {meta['episode']}\n\n**{meta['title']}**\n\n{url}  (privacy: {resp['status']['privacyStatus']})\n\n"
                     f"Review it in [YouTube Studio](https://studio.youtube.com/video/{vid}/edit) and set it to Public when happy.\n")
    with open(os.path.join(OUT, "video_id.txt"), "w") as fh:
        fh.write(vid)


if __name__ == "__main__":
    main()
