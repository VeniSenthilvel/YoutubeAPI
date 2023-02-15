from googleapiclient import discovery



class Support():dfgdfg

  def __init__(self):
    self.default_file_name = 'YoutubeAPI.csv'
    return



  def write_csv(self, file_location='.', file_name=None, header_row=None, data=None):
    """
      Function to write data in a csv file format
        
        Usage:
          write_csv(file_name, header_row, data)

        Parameters:
          file_name : Name of the file to save the gathered data
          header_row : Custom Title/Header for your CSV data file
          data : Data to write into the CSV file
    """
    self.file_name = f'{file_location}/{file_name}' if file_name is not None else self.default_file_name

    try:
      with open(self.file_name,'r') as prevFile:
        pass
    except FileNotFoundError or UnboundLocalError:
      with open(self.file_name,'w') as NewFile:
        NewFile.write(header_row)
        NewFile.close()
    with open(self.file_name,'a') as file:
      for i in data:
        file.write(i)
    file.close()

    return f'File named {self.file_name} was successfully written in the given location'

  

class YoutubeAPI():
  
  def __init__(self, key):
    """
      To initialize the Youtube API
        Usage:
          youtube = YoutubeInti(key)
        Parameters:
          key : api key from your authorized google developers account 
    """
    self.youtube = discovery.build('youtube','v3',developerKey=key)
    return 



  


  def search_channel_for(self, search_term, total_results=20, file_name=None):
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
      file_name = f'YoutubeAPI_{search}_.csv' if file_name is None else file_name
      final_results[search] = ''
      for _ in range(0,total_results,25):
        request = self.youtube.search().list(
            part='snippet',
            maxResults=25,
            pageToken=next_page_token,
            q=search
        )
        response = request.execute()
        next_page_token = response.get('nextPageToken')
        header_row = 'channel_id,channel_title,video_title,video_description,live_broadcast_content,video_published_time,search_keyword,position_id_result\n'
        row_data = self.search_results_channel_data_formatter(search_word=search,data=response)
        result = Support().write_csv(file_name=file_name,header_row=header_row,data=row_data)
        final_results[search] = result
        file_name=None

    return final_results


  def search_results_channel_data_formatter(self, search_word, data):
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





  def get_video_comments(self, video_id):
    """
      Function to get comments of an youtube video
        
        Usage:
          get_video_comments(youtube,video_id)
        
        Parameters:
          youtube : Youtube API
          video_id : ID of the youtube video for which you want to fetch the comments
    """
    request = self.youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id   
    )

    return request.execute()




  def get_video_categories_in_region(self, region_code='in'):
    """
      Function to get video categories in a region

        Usage:
          get_video_categories_in_region(youtube, region_code)
        
        Parameters:
          youtube : Youtube API
          region_code : Code of the Region for which you want the get the categories
    """

    request = self.youtube.videoCategories().list(
        part='snippet',
        regionCode=region_code
    )

    return request.execute()



  def get_channel_stats(self, channel_id):
    """
      Function to get channel statistics 

        Usage:
          get_channel_stats(youtube, channel_id)
        Parameters:
          youtube : Youtube API
          channel_id : ID of the channel for which you want to get the statistics data
    """

    request = self.youtube.channels().list(
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




  def get_video_ids(self, playlist_id):
    """
      Function to get video id

        Usage:
          get_video_ids(youtube, playlist_id)
        
        Parameter:
          youtube : Youtube API
          playlist_id : ID of the playlist for which you want the video id's list
    """

    request = self.youtube.playlistItems().list(
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
        request = self.youtube.playlistItems().list(
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




  def default_comment_count(self, video):
    try:
      count = video['statistics']['commentCount'] or 0
    except Exception:
      count = 0
    return  count



  def get_video_details(self, video_ids):
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
      request = self.youtube.videos().list(
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
              Comments=self.default_comment_count(video))
          for video in response['items'])
    return all_video_stats

