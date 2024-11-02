import sys, os
if os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from data_types import VideoData

load_dotenv()
class YouTubeScheduler:
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self):
        self.youtube = self._authenticate()

    def _authenticate(self) -> build:
        TOKENS_DIR = Path('.tokens')
        YOUTUBE_TOKEN_PATH = TOKENS_DIR / 'youtube_token.json'
        creds = None
        
        TOKENS_DIR.mkdir(parents=True, exist_ok=True)
        if YOUTUBE_TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN_PATH, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    # If refresh fails, delete the token file and start fresh
                    YOUTUBE_TOKEN_PATH.unlink(missing_ok=True)
                    creds = None
            
            if not creds:
                credentials_json = json.loads(os.getenv('YOUTUBE_CLIENT_SECRET'))
                flow = InstalledAppFlow.from_client_config(credentials_json, self.SCOPES)
                creds = flow.run_local_server(port=0)
            YOUTUBE_TOKEN_PATH.write_text(creds.to_json())

        return build('youtube', 'v3', credentials=creds)

    def schedule_video(self, video_data: VideoData, category: str = '22',
                      privacy_status: str = 'private',
                      publish_time: Optional[datetime] = None) -> str:
        """Schedule a video upload using VideoData structure"""
        if not video_data.video_path or not video_data.video_path.exists():
            raise ValueError("Video path not found")
            
        if not video_data.youtube_details:
            raise ValueError("YouTube details not provided")

        body = {
            'snippet': {
                'title': video_data.youtube_details.title or '',
                'description': video_data.youtube_details.description or '',
                'tags': video_data.youtube_details.tags or [],
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy_status,
            }
        }

        if publish_time:
            body['status']['publishAt'] = publish_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        media = MediaFileUpload(str(video_data.video_path), resumable=True)

        try:
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            response = self._resumable_upload(request)
            
            # Update VideoData with upload information
            if response and 'id' in response:
                video_data.youtube_details.uploaded = True
                video_data.youtube_details.url = f"https://youtu.be/{response['id']}"
                if publish_time:
                    video_data.youtube_details.realse_date = publish_time.isoformat()
                video_data.save()
                
            return response['id'] if response else None
            
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
    # Example usage with new VideoData structure
    video_number = "5"
    base_path = Path(r"C:\Users\bruno\Desktop\autovid\data\MITO_TV\historias_de_titanes_de_la_mitología_griega_2")
    json_path = base_path / video_number / "video_data.json"
    
    video_data = VideoData.get(json_path)
    video_data.video_path = json_path.parent / f"{video_number}.mp4"

    
    scheduler = YouTubeScheduler()
    video_id = scheduler.schedule_video(
        video_data=video_data,
        privacy_status='private',
        publish_time=datetime(2024, 11, 7, 15, 0, 0, tzinfo=ZoneInfo("Europe/Madrid"))
    )
    
    if video_id:
        print(f"Video scheduled successfully. Video ID: {video_id}")
    else:
        print("Failed to schedule video.")
