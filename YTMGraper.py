# This file Simply Grabs the audio from youtube videos
# this files requies the yt-dlp library and ffmpeg library to be on your system
# Note that pytube should also be installed as well


from urllib.parse import urlparse, parse_qs
from Constants import VideoStatus
import subprocess
import yt_dlp


# Structure
class Audio:
    def __init__(self):
        self.ID = None
        self.Name = None
        self.Buffer = None
        self.Format = None
        self.Status = VideoStatus.NOT_INSTALLED
        self.m3u8Playlist = None



class Graper:
    def __init__(self):


        self.AudioData = { # This Hashmap should be passed from its parant class to this 
            # "<YoutubeID>" : Aduio() 
        }



    def Preparing(self, URL, Title=None):
        try:
            if Title:
                _video_title = Title
            else:
                _video_title = VideoStatus.UNKNOWN_TITLE
                try:
                    # This section needs fix where it gets the video name for you "efficinatly"

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
            print(e)

    #this function is slow esspically if there is more than 50 videos in one play list check the pytube.Playlist to know why
    def PlaylistHerfsRequest(self, playlist_url):
        ydl_opts = {
            'ignoreerrors': True,
            'quiet': True,
            'extract_flat': True,
        }
        _id = self.extract_playlist_id(playlist_url)
        canonical_url = f"https://www.youtube.com/playlist?list={_id}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(canonical_url, download=False)
            if info is None:
                return
            
            videos_info = []
            entries = info.get('entries')
            if not entries:
                raise ValueError("No videos found in the playlist or playlist is private/unavailable.")
            
            for entry in entries:
                if entry is None:
                    continue
                title = entry.get('title')
                video_id = entry.get('id')
                if not title or not video_id:
                    continue
                url = f"https://www.youtube.com/watch?v={video_id}"
                videos_info.append([url, title])
        
        return videos_info

            

    def Donwload(self, YoutubeID):

        #_yt = YouTube(URL)
        #_video_title = _yt.title

        #_youtubeID = self.extract_youtube_video_id(URL)
        Container = self.AudioData[YoutubeID]
        Container.Status = VideoStatus.PREPARING

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
            Container.Status = VideoStatus.READY
            return Buffer
        else:
            Container.Status = VideoStatus.ERROR


    def Grap_m3u8_And_Title(self, YoutubeID):


        Container = self.AudioData[YoutubeID]
        Container.Status = VideoStatus.PREPARING

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/{YoutubeID}", download=False)
                title = info.get('title')

                # Filter audio-only formats that use m3u8
                m3u8_audio_url = None
                for fmt in info.get('formats', []):
                    if (
                        fmt.get('protocol') in ['m3u8', 'm3u8_native']
                        and fmt.get('vcodec') == 'none'  # means audio-only
                    ):
                        m3u8_audio_url = fmt.get('url')
                        break

                Container.Name, Container.m3u8Playlist = title, m3u8_audio_url
                Container.Status = VideoStatus.HAS_MEU8_URL
        except:
            Container.Status = VideoStatus.ERROR

            

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
        
    def extract_playlist_id(self, youtube_url):
        parsed_url = urlparse(youtube_url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('list', [None])[0]





if __name__ == "__main__":
    url = "watch?v=fWNaR-rxAic"
    x = Graper()
    import time
    EllipsisTime = time.time()
    x.Preparing(url)
    y = x.Donwload(url)
    print(f"Time Taken to download: {time.time() - EllipsisTime}")
    y = x.Convert(y)
    print(f"Time Taken to Convert: {time.time() - EllipsisTime}")
    print(len(y))
    x.SaveMusic(y,"hello.mp4")
    print(f"Time Taken to Convert: {time.time() - EllipsisTime}")