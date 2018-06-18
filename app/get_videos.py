import sys
from apiclient.discovery import build

#get API key for authentication from google developer console and provide here
api_key = sys.argv[1]

#building the service object
service = build('youtube', 'v3', developerKey=api_key)

#call to channels.list to retrieve uploads_id(list of all videos uploaded by channel) for given channel_id
response = service.channels().list(
  part='contentDetails',
  id='UCi7GJNg51C3jgmYTUwqoUXA',
  fields='items/contentDetails/relatedPlaylists/uploads'
).execute()
uploads_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

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
      print(video['snippet']['title'])
  request = service.playlistItems().list_next(request, video_list)
