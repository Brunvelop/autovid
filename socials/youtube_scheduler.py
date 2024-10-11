import os
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()
class YouTubeScheduler:
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self):
        self.youtube = self._authenticate()

    def _authenticate(self) -> build:
        TOKENS_DIR = Path('./.tokens')
        YOUTUBE_TOKEN_PATH = TOKENS_DIR / 'youtube_token.json'
        creds = None
        
        TOKENS_DIR.mkdir(parents=True, exist_ok=True)
        if YOUTUBE_TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_PATH, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_json = json.loads(os.getenv('YOUTUBE_CLIENT_SECRET'))
                flow = InstalledAppFlow.from_client_config(credentials_json, self.SCOPES)
                creds = flow.run_local_server(port=0)
            YOUTUBE_TOKEN_PATH.write_text(creds.to_json())

        return build('youtube', 'v3', credentials=creds)


    def schedule_video(self, video_path: Path, title: str, description: str, 
                       tags: List[str], category: str = '22', 
                       privacy_status: str = 'private', 
                       publish_time: Optional[datetime] = None) -> str:       
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy_status,
                'publishAt': publish_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        }

        media = MediaFileUpload(video_path, resumable=True)

        try:
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            response = self._resumable_upload(request)
            return response['id']
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
            return None
    
    def check_quota_usage(self) -> dict:
        pass

    def _resumable_upload(self, request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print(f"Video id '{response['id']}' was successfully uploaded.")
                        return response
                    else:
                        raise ValueError(f"The upload failed with an unexpected response: {response}")
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise
            if error is not None:
                print(error)
                retry += 1
                if retry > 10:
                    raise ValueError("No longer attempting to retry.")


if __name__ == "__main__":
    scheduler = YouTubeScheduler()
    # c = scheduler.check_quota_usage()
    CATEGORY = 'MITOS_NORDICOS'
    VIDEO_N = 7
    VIDEO_PATH = Path(f'data/MITO_TV/SHORTS/{CATEGORY}/{VIDEO_N}')

    video_id = scheduler.schedule_video(
        video_path=VIDEO_PATH / f'{VIDEO_N}.mp4',
        title=json.load(open(VIDEO_PATH / 'text/storyboard.json'))[0].get('text', ''),
        description=open(VIDEO_PATH / 'text/text.txt', 'r', encoding='utf-8').read(),
        tags=[],
        privacy_status='private',
        publish_time = datetime(2024, 10, 12, 15, 0, 0, tzinfo=ZoneInfo("Europe/Madrid"))
    )
    
    if video_id:
        print(f"Video scheduled successfully. Video ID: {video_id}")
    else:
        print("Failed to schedule video.")