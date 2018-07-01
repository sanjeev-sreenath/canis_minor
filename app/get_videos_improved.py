import sys
import pymongo
#import dateutil.parser
from dateutil import parser
from apiclient.discovery import build

cli = pymongo.MongoClient()
db = cli.interview_details

celebrity_list = list(db.celebrity_collection.find({}, {'_id': 0, 'name': 1}))

def get_celeb_name_from_title(title, uploads_id, next_page_token, prev_page_token=None):
    celebrities_present = []
    for celebrity in celebrity_list:
        if celebrity['name'] in title:
            celebrities_present.append(celebrity['name'])
    if len(celebrities_present) == 0:
        return None
    elif len(celebrities_present) == 1:
        return celebrities_present[0]
    else:
        celebrity_count = {}
        for name in celebrities_present:
            celebrity_count[name] = 1

        api_key = sys.argv[1]
        service = build('youtube', 'v3', developerKey=api_key)

        response = service.playlistItems().list(
          part='snippet',
          maxResults=50,
          pageToken=next_page_token,
          playlistId=uploads_id,
          fields='items(snippet(publishedAt,resourceId/videoId,title)),nextPageToken,prevPageToken'
        ).execute()
        for video in response['items']:
            for celebrity in celebrity_count:
                if celebrity in video['snippet']['title']:
                    celebrity_count[celebrity] += 1

        response = service.playlistItems().list(
          part='snippet',
          maxResults=50,
          pageToken=response['prevPageToken'],
          playlistId=uploads_id,
          fields='items(snippet(publishedAt,resourceId/videoId,title)),nextPageToken,prevPageToken'
        ).execute()
        for video in response['items']:
            for celebrity in celebrity_count:
                if celebrity in video['snippet']['title']:
                    celebrity_count[celebrity] += 1

        if prev_page_token:
            response = service.playlistItems().list(
              part='snippet',
              maxResults=50,
              pageToken=prev_page_token,
              playlistId=uploads_id,
              fields='items(snippet(publishedAt,resourceId/videoId,title)),nextPageToken,prevPageToken'
            ).execute()
            for video in response['items']:
                for celebrity in celebrity_count:
                    if celebrity in video['snippet']['title']:
                        celebrity_count[celebrity] += 1

        return max(celebrity_count, key=celebrity_count.get)

def fetch_videos_for_channel(channel_id, host_name):
    #get API key for authentication from google developer console and provide here
    api_key = sys.argv[1]

    #other params: youtube_channel_id, time-range to get delta of videos

    #building the service object
    service = build('youtube', 'v3', developerKey=api_key)

    #call to channels.list to retrieve uploads_id(list of all videos uploaded by channel) for given channel_id
    response = service.channels().list(
      part='contentDetails',
      id = channel_id,
      #id='UCi7GJNg51C3jgmYTUwqoUXA',
      fields='items/contentDetails/relatedPlaylists/uploads'
    ).execute()

    print(response)
    uploads_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    #construct request object to retreive list of videos from uploads_id
    request = service.playlistItems().list(
      part='snippet',
      maxResults=50,
      playlistId=uploads_id,
      fields='items(snippet(publishedAt,resourceId/videoId,title)),nextPageToken,prevPageToken'
    )

    #implementing pagination with func().list_next
    while request is not None:
      video_list = request.execute()
      for video in video_list['items']:
          if 'prevPageToken' in video_list:
              celeb_name = get_celeb_name_from_title(video['snippet']['title'], uploads_id, video_list['nextPageToken'], video_list['prevPageToken'])
          else:
              celeb_name = get_celeb_name_from_title(video['snippet']['title'], uploads_id, video_list['nextPageToken'])
          if  celeb_name == None:
              continue
          db.video_collection.insert_one({
            "host_name": host_name,
            "celebrity_name": celeb_name,
            "youtube_video_id": video['snippet']['resourceId']['videoId'],
            "youtube_title": video['snippet']['title'],
            "youtube_published_on": video['snippet']['publishedAt']
          })
          print("inserting {} ---, title: {}".format(celeb_name, video['snippet']['title']))
      request = service.playlistItems().list_next(request, video_list)

def fetch_channel_from_mongo():
    host_cursor = db.host_collection.find()
    for host in host_cursor:
        for channel in host['youtube_channel_ids']:
            fetch_videos_for_channel(channel,host['name'])

if __name__ == "__main__":
    fetch_channel_from_mongo()

# ------------------------------------------------------------------
# To pretty print hosts collection limited to 10 videos per channel
# db.hosts.find({}, {"channels.videos": {$slice: [0, 10]} }).pretty()

## TODO:
# populate more celebrities from imdb
# delta logic for video grabbing
