import json
import os

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

youtube = build('youtube', 'v3', developerKey=api_key)

pl_request = youtube.playlists().list(
    part='contentDetails, snippet',
    channelId='UCHP9CdeguNUI-_nBv_UXBhw',
    maxResults=20
)

pl_response = pl_request.execute()
playlist_id = None
playlist_name = "Top Theory Speedrun"
for item in pl_response['items']:
    # print(item["snippet"]['title'])
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
        playlistId=playlist_id,
        maxResults=50,
        pageToken=nextPageToken
    )

    pl_items_response = pl_items.execute()

    vid_ids = [item['contentDetails']['videoId'] for item in pl_items_response['items']]

    vid_request = youtube.videos().list(
        part="snippet, contentDetails",
        id=','.join(vid_ids)
    )

    vid_response = vid_request.execute()

    for vid in vid_response['items']:
        snippet = vid["snippet"]
        content_details = vid["contentDetails"]

        videos[vid["id"]] = {
            "video_id": vid["id"],
            "video_url": f"https://www.youtube.com/watch?v={vid['id']}",
            "title": snippet["title"],          
            "published_at": snippet["publishedAt"],
            "duration": content_details["duration"],
            "description": snippet["description"],
        }
        count += 1

    nextPageToken = pl_items_response.get('nextPageToken')

    if not nextPageToken:
        break

print(f"Total videos: {count}")

# Save as a list (easier to work with downstream than a dict keyed by video_id)
video_list = list(videos.values())

with open("youtube_videos.json", "w", encoding="utf-8") as f:
    json.dump(video_list, f, indent=2, ensure_ascii=False)

print("Saved to youtube_videos.json")