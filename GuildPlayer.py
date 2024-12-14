




from YTMGraper import Graper
import threading


# Structure for refrence Only
class Audio:
    def __init__(self):
        self.ID = None
        self.Name = None
        self.Buffer = None
        self.Format = None
        self.Status = "NotInstalled"



class Player():
    def __init__(self):

        self.GuildID = None
        self.Channal = None # this is used to keep track of the data of each guild


        self.AudioData = {
            # "<YoutubeID>" : Aduio()
        }


        self.AudioGraper = Graper()
        self.AudioGraper.AudioData = self.AudioData


        self.AudioPlaying = None
        self.Queue = []
        self.History = []
        self.IsPlaying = False



        # API Functions
        self.PlayFunction = None
        self.StopFunction = None
        self.SeekFunction = None






    def AddToQueue(self, YoutubeID):
        _id = self.AudioGraper.extract_youtube_video_id(YoutubeID)

        try:
            self.AudioData[_id]
        except:
            self.AudioGraper.Preparing(_id)
            
        self.Queue.append(self.AudioData[_id])


    def AddPlayList(self, YoutubePLID):
        _ids = self.AudioGraper.PlaylistHerfsRequest(YoutubePLID)
        for Index, _id in enumerate(_ids):
            self.AddToQueue(_id)
            if Index >= 100:
                return


    async def Update(self):

        if self.IsPlaying == False and self.Channal:
            if not self.AudioPlaying and self.Queue:
                self.AudioPlaying = self.Queue[0]
                self.Queue.pop(0)

            if self.AudioPlaying:
                try:
                    if self.AudioPlaying.Status == "Preparing":
                        return

                    if self.AudioPlaying.Status == "Ready":
                        if self.Channal and not self.IsPlaying:
                            await self.PlayFunction(self.AudioPlaying.Buffer, self.Channal, self.GuildID)
                            self.IsPlaying = True

                    if self.AudioPlaying.Status == "NotInstalled":
                        #self.AudioPlaying.Status = "Preparing" # change the varable just in case so we dont run through errors
                        threading.Thread(target=self.AudioGraper.Donwload, args=(self.AudioPlaying.ID,)).start()


                    if self.AudioPlaying.Status == "Error":
                        self.AudioPlaying.Buffer = None
                        self.AudioPlaying.Status = "NotInstalled"
                        self.IsPlaying = False
                        self.AudioPlaying = None
                except:
                    pass