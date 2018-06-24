import sys
import pymongo
from apiclient.discovery import build

cli = pymongo.MongoClient()
db = cli.interview_details

def fetch_videos_for_channel(channel_id):
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

    db.hosts.update_one(
        {"channels.youtube_channel_id": channel_id},
        {'$set': {"channels.$.youtube_uploads_id": uploads_id} }
    )

    #construct request object to retreive list of videos from uploads_id
    request = service.playlistItems().list(
      part='snippet',
      maxResults=50,
      playlistId=uploads_id,
      fields='items(snippet(publishedAt,resourceId/videoId,title)),nextPageToken'
    )

    #implementing pagination with func().list_next
    while request is not None:
      video_list = request.execute()
      for video in video_list['items']:
          db.hosts.update_one(
            {"channels.youtube_channel_id": channel_id},
            {'$push': {"channels.$.videos": {
                "youtube_video_id": video['snippet']['resourceId']['videoId'],
                "youtube_title": video['snippet']['title'],
                "youtube_published_on": video['snippet']['publishedAt']
            }}}
          )

          print(video['snippet']['title'])
      request = service.playlistItems().list_next(request, video_list)

def fetch_channel_from_mongo():
    host_curs = db.hosts.find()
    for host in host_curs:
        for channel in host['channels']:
            fetch_videos_for_channel(channel['youtube_channel_id'])
    # for host in list(db.hosts.find()):
    #     for channel in host.channels:
    #         fetch_videos_for_channel(channel)

if __name__ == "__main__":
    fetch_channel_from_mongo()
