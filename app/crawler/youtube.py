__author__ = 'ffuuugor'

from googleapiclient.discovery import build
from config import DEVELOPER_KEY, YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION
import isodate


class Video:

    def __init__(self, title, thumb, id, duration):
        self.title = title.encode("utf-8")
        self.thumb = thumb
        self.id = id
        self.duration = duration

    def _make_url(self):
        return "http://www.youtube.com/watch?v={}".format(self.id)

    def _make_embed(self):
        return "<a href={url} target=_blank><img src={thumb}></a> {title}".format(url=self._make_url(),
                                                                                  thumb=self.thumb,
                                                                                  title=self.title)

    def to_json(self):
        return {"title": self.title,
                "thumb": self.thumb,
                "id": self.id,
                "duration": self.duration,
                "url": self._make_url(),
                "embed": self._make_embed()}


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
    print youtube_search("cabview")