__author__ = 'ffuuugor'

from googleapiclient.discovery import build
from geo import CityExtractor
import isodate

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class Video:

    def __init__(self, title, thumb, id, duration):
        self.title = title;
        self.thumb = thumb;
        self.id = id;
        self.duration = duration;

        self.from_city = None;
        self.to_city = None;

#def _parse_duration(duration_str):

def youtube_search(query, pages=1):

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)

    next_page_token=None

    ret = []
    for i in range(1,pages+1):
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=50,
            type="video",
            videoDuration="long",
            pageToken=next_page_token
        ).execute()

        videos = [x["id"]["videoId"] for x in search_response.get("items")]

        videos_response = youtube.videos().list(
            part="id,snippet,contentDetails",
            id=",".join(videos)
        ).execute()

        for video_info in videos_response.get("items"):
            title = video_info["snippet"]["title"]
            thumb = video_info["snippet"]["thumbnails"]["default"]["url"]
            id = video_info["id"]
            duration = isodate.parse_duration(video_info["contentDetails"]["duration"]).seconds

            video = Video(title=title, thumb=thumb, id=id, duration=duration)
            ret.append(video)

        next_page_token = search_response.get("nextPageToken")
        if next_page_token is None:
            break

    return ret

if __name__ == "__main__":
    youtube_search("cabview")