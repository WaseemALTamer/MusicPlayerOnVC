# This file Simply Grabs the audio from youtube videos
# this files requies the yt-dlp library and ffmpeg library to be on your system
# Note that pytube should also be installed as well


from urllib.parse import urlparse, parse_qs
from pytube import YouTube, Playlist
import subprocess



# Structure
class Audio:
    def __init__(self):
        self.ID = None
        self.Name = None
        self.Buffer = None
        self.Format = None
        self.Status = "NotInstalled"



class Graper():
    def __init__(self):


        self.AudioData ={ # This Hashmap should be passed from its parant class to this 
            # "<YoutubeID>" : Aduio() 
        }



    def Preparing(self, URL, Title=None):
        try:
            if Title:
                _video_title = Title
            else:
                try:
                    #_yt = YouTube(URL)
                    #_video_title = _yt.title
                    pass
                except:
                    pass
            _youtubeID = self.extract_youtube_video_id(URL)
            Container = self.AudioData[_youtubeID] = Audio()
            Container.ID = _youtubeID
            Container.Name = _video_title
        except Exception as e:
            pass

    #this function is slow esspically if there is more than 50 videos in one play list check the pytube.Playlist to know why
    def PlaylistHerfsRequest(self, playlist_url):
        playlist = Playlist(playlist_url)
        url_title_pairs = [[video.watch_url, None] for video in playlist.videos]
        return url_title_pairs
        

    def Donwload(self, YoutubeID):

        #_yt = YouTube(URL)
        #_video_title = _yt.title

        #_youtubeID = self.extract_youtube_video_id(URL)
        Container = self.AudioData[YoutubeID]
        Container.Status = "Preparing"

        Command = [
                    'yt-dlp',
                    '--format', 'bestaudio/best',
                    '--quiet',
                    '--no-warnings',
                    '-o', '-', 
                    f'https://www.youtube.com/{YoutubeID}'
                ]

        Proccess = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        Buffer, ErrorCode = Proccess.communicate()
        Proccess.wait()

        if not ErrorCode:
            Container.Buffer = Buffer
            Container.Status = "Ready"
            return Buffer
        else:
            Container.Status = "Error"



    def Convert(self, Data, Container="wav"):
        Command = [
                    'ffmpeg',
                    '-i', 'pipe:0',  # Input from stdin
                    '-f', Container,     # Format as MP3
                    '-acodec', 'libmp3lame',  # Use MP3 codec
                    '-ab', '192k',   # Bitrate
                    'pipe:1'         # Output to stdout
                ]

        Proccess = subprocess.Popen(Command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        Buffer, _ = Proccess.communicate(input=Data)  # Pass Data here
        Proccess.wait()

        if not Proccess.returncode:
            return Buffer



    def SaveMusic(self, Data, FileName):
        with open(FileName, "wb") as f:
            f.write(Data)



    def extract_youtube_video_id(self, url):
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [''])[0]
            return f"watch?v={video_id}"
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return ''




if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=gtfReGLyM_4"
    x = Graper()
    import time
    EllipsisTime = time.time()
    y = x.Donwload(url)
    print(f"Time Taken to download: {time.time() - EllipsisTime}")
    y = x.Convert(y)
    print(f"Time Taken to Convert: {time.time() - EllipsisTime}")
    print(len(y))