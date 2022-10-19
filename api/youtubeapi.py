from googleapiclient.discovery import build
from datetime import datetime




def YoutubeInit(key):
  """
    To initialize the Youtube API
      Usage:
        youtube = YoutubeInti(key)
      Parameters:
        key : api key from your authorized google developers account 
  """
  return build('youtube','v3',developerKey=key)



def write_csv(file_location, file_name, header_row, data):
  """
    Function to write data in a csv file format
      
      Usage:
        write_csv(file_name, header_row, data)

      Parameters:
        file_name : Name of the file to save the gathered data
        header_row : Custom Title/Header for your CSV data file
        data : Data to write into the CSV file
  """

  file_name = f'{file_location}/{file_name}'

  try:
    with open(file_name,'r') as prevFile:
      pass
  except FileNotFoundError or UnboundLocalError:
    with open(file_name,'w') as NewFile:
      NewFile.write(header_row)
      NewFile.close()
  with open(file_name,'a') as file:
    for i in data:
      file.write(i)
  file.close()

  return f'File named {file_name} was successfully written in the given location'



def search_results_channel_data(youtube,search_term,total_results,file_name=None):
  """
  Function to get results for search
    
    Usage:
      search_results_channel_data(youtube,search_term,total_results,file_name)
    
    Parameters:
      youtube : Youtube API build
      search_term : The word to be searched (NOTE: mention word without space)
      total_results : Total number of channels needed
      file_name : Custom FileName if needed
    
    Return:
      This function will create a file with CSV extension in the current directory or the path mentioned.
      This function will return a dictionary of the details of CSV created during the execution of this function.

  """

  final_results = {}
  next_page_token = ''

  for search in search_term:
    file_name = f'youtube_data_{search}_{datetime.now()}.csv'
    final_results[search] = ''
    for _ in range(0,total_results,25):
      request = youtube.search().list(
          part='snippet',
          maxResults=25,
          pageToken=next_page_token,
          q=search
      )
      response = request.execute()
      next_page_token = response.get('nextPageToken')
      header_row = 'channel_id,channel_title,video_title,video_description,live_broadcast_content,video_published_time,search_keyword,position_id_result\n'
      row_data = search_results_channel_data_formatter(search_word=search,data=response)
      result = write_csv(file_name,header_row,row_data)
      final_results[search] = result
      
  return final_results


def search_results_channel_data_formatter(search_word,data):
  """
    Function to format the output of the scrapped data of the channels

      Usage:
        search_results_channel_data_formatter(search_word,data)
      Parameters:
        search_word : The word to be searched (NOTE: mention word without space)
        data : 

  """

  main_data = []

  for i in range(len(data['items'])):
    channel_id = data['items'][i]['snippet']['channelId']
    channel_title = data['items'][i]['snippet']['channelTitle']
    video_title = data['items'][i]['snippet']['title']
    video_description = data['items'][i]['snippet']['description']
    live_broadcast_content = data['items'][i]['snippet']['liveBroadcastContent']
    video_published_time = data['items'][i]['snippet']['publishTime']
    position_in_result = i
    
    row_data = f'"{channel_id}","{channel_title}","{video_title}","{video_description}","{live_broadcast_content}","{video_published_time}","{search_word}","{position_in_result}"\n'
    main_data.append(row_data)

  return main_data





def get_video_comments(youtube,video_id):
  """
    Function to get comments of an youtube video
      
      Usage:
        get_video_comments(youtube,video_id)
      
      Parameters:
        youtube : Youtube API
        video_id : ID of the youtube video for which you want to fetch the comments
  """
  request = youtube.commentThreads().list(
      part='snippet,replies',
      videoId=video_id   
  )

  return request.execute()




def get_video_categories_in_region(youtube,region_code):
  """
    Function to get video categories in a region

      Usage:
        get_video_categories_in_region(youtube, region_code)
      
      Parameters:
        youtube : Youtube API
        region_code : Code of the Region for which you want the get the categories
  """

  request = youtube.videoCategories().list(
      part='snippet',
      regionCode=region_code
  )

  return request.execute()



def get_channel_stats(youtube, channel_id):
  """
    Function to get channel statistics 

      Usage:
        get_channel_stats(youtube, channel_id)
      Parameters:
        youtube : Youtube API
        channel_id : ID of the channel for which you want to get the statistics data
  """

  request = youtube.channels().list(
      part='snippet,contentDetails,statistics',
      id=','.join(channel_id))

  response = request.execute()

  return [
      dict(
          Channel_name=response['items'][i]['snippet']['title'],
          Subscribers=response['items'][i]['statistics']['subscriberCount'],
          Views=response['items'][i]['statistics']['viewCount'],
          Total_videos=response['items'][i]['statistics']['videoCount'],
          playlist_id=response['items'][i]['contentDetails']
          ['relatedPlaylists']['uploads'])
      for i in range(len(response['items']))
  ]




def get_video_ids(youtube,playlist_id):
  """
    Function to get video id

      Usage:
        get_video_ids(youtube, playlist_id)
      
      Parameter:
        youtube : Youtube API
        playlist_id : ID of the playlist for which you want the video id's list
  """

  request = youtube.playlistItems().list(
      part='contentDetails',
      playlistId = playlist_id,
      maxResults = 50
  )

  response = request.execute()

  video_ids = [
      response['items'][i]['contentDetails']['videoId']
      for i in range(len(response['items']))
  ]

  next_page_token = response.get('nextPageToken')
  more_pages = True

  while more_pages:
    if next_page_token is None:
      more_pages = False
    else:
      request = youtube.playlistItems().list(
          part='contentDetails',
          playlistId=playlist_id,
          maxResults = 50,
          pageToken = next_page_token
      )
      response = request.execute()


      video_ids.extend(response['items'][i]['contentDetails']['videoId']
                       for i in range(len(response['items'])))
      next_page_token = response.get('nextPageToken')


  return video_ids




def default_comment_count(video):
  try:
    count = video['statistics']['commentCount'] or 0
  except Exception:
    count = 0
  return  count



def get_video_details(youtube, video_ids):
  """
    Function to get basic video details

      Usage:
        get_video_details(youtube, video_ids)
      
      Parameters:
        youtube : Youtube API
        video_ids : ID of the youtube video for which you want to get the details
  """

  all_video_stats = []

  for i in range(0, len(video_ids), 50):
    request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids[i:i+50])
    )
    response = request.execute()
    all_video_stats.extend(
        dict(
            Title=video['snippet']['title'],
            Published_date=video['snippet']['publishedAt'],
            Views=video['statistics']['viewCount'],
            Likes=video['statistics']['likeCount'],
            Comments=default_comment_count(video))
        for video in response['items'])
  return all_video_stats



