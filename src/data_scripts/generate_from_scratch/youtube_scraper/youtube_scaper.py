
import os

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

youtube = build('youtube', 'v3', developerKey=api_key)
    
pl_request = youtube.playlists().list(
    part = 'contentDetails, snippet',
    channelId='UCHP9CdeguNUI-_nBv_UXBhw',
    maxResults=20
)

pl_repsonse = pl_request.execute()
playlist_id = None
playlist_name = "SpeedRun"
for item in pl_repsonse['items']:
    if item["snippet"]['title'] == playlist_name:
        playlist_id = item["id"]

if not playlist_id:
    raise ValueError("No playlist found")
else:
    print(f"{playlist_name} id found: {playlist_id}")

nextPageToken = None
count = 0 
videos = {}
while True:


    pl_items = youtube.playlistItems().list(
        part='contentDetails',
        playlistId = playlist_id,
        maxResults =50, #check this 
        pageToken=nextPageToken
    )

    pl_items_response = pl_items.execute()

    vid_ids = []
    for item in pl_items_response['items']:
        vid_ids.append(item['contentDetails']['videoId'])

    vid_request = youtube.videos().list(
        part="snippet, contentDetails",
        id = ','.join(vid_ids)
    )

    vid_response= vid_request.execute()

    for vid in vid_response['items']:
        # print(item)
        # print()
        snippet = vid["snippet"]
        content_details = vid["contentDetails"]
        videos[vid["id"]] = {}

        videos[vid["id"]]["video_id"] = vid["id"]
        videos[vid["id"]]["title"] = snippet["title"],
        videos[vid["id"]]["published_at"] = snippet["publishedAt"]
        videos[vid["id"]]["duration"] = content_details["duration"]
        videos[vid["id"]]["description"] = snippet["description"]
        count += 1

    nextPageToken = pl_items_response.get('nextPageToken')

    if not nextPageToken:
        break

    

print(count)
for key, value in videos.items():
    print(key)
    print(value)
    print()

