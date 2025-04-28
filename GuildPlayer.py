# this file doesnt use typing because i couldnt add the typing library
# and make it run on my linux machine so if you  want to do it i would
# love to see it in the file



from Constants import VideoStatus
from YTMGraper import Graper
import threading



# Structure for refrence Only
class Audio:
    def __init__(self):
        self.ID = None
        self.Name = None
        self.Buffer = None
        self.Format = None
        self.Status = VideoStatus.NOT_INSTALLED



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
        self.QueueLoopBack = False # Read only (if you want to change it use the function "SetQueueLoopBack")
        self.AudioLoopBack = False # read only (if you want to change it use the function "SetAudioLoopBack")



        # API Functions
        self.PlayFunction = None
        self.StopFunction = None # not implemented and for the discord api it wont be
        self.SeekFunction = None # still need to be implemented




    def SetQueueLoopBack(self, state):
        if state == True:
            self.QueueLoopBack = state
        elif not state == False:
            self.QueueLoopBack = state
        else:
            self.QueueLoopBack = not self.QueueLoopBack

        if self.QueueLoopBack and self.AudioPlaying and (not self.Queue or (self.Queue and self.Queue[0] != self.AudioPlaying)):
            self.Queue.append(self.AudioPlaying)
         
        


    def SetAudioLoopBack(self, state):
        if state == True:
            self.AudioLoopBack = state
        elif not state == False:
            self.AudioLoopBack = state
        else:
            self.AudioLoopBack = not self.AudioLoopBack

        if self.AudioLoopBack and self.AudioPlaying and (not self.Queue or (self.Queue and self.Queue[0] != self.AudioPlaying)):
            self.Queue.insert(0, self.AudioPlaying)

        if not self.AudioLoopBack and self.Queue and self.Queue[0] == self.AudioPlaying:
            self.Queue.pop(0)
            
            



    def AddToQueue(self, ID, Title=None, Index=None):

        _id = self.AudioGraper.extract_youtube_video_id(ID)
        try:
            self.AudioData[_id]
        except:
            self.AudioGraper.Preparing(_id, Title=Title)
        
        if Index == None:
            self.Queue.append(self.AudioData[_id])
        else:
            self.Queue.insert(Index, self.AudioData[_id])


    def AddPlayList(self, YoutubePLID):
        _ids_titles = self.AudioGraper.PlaylistHerfsRequest(YoutubePLID)
        for _id, _title in _ids_titles:
            self.AddToQueue(_id, Title=_title)


    # this update function should be ran in a loop
    async def Update(self):

        if self.IsPlaying == False and self.Channal:
            if not self.AudioPlaying and self.Queue:

         
                self.AudioPlaying = self.Queue[0]
                self.Queue.pop(0)


                if not self.History or self.History[-1] != self.AudioPlaying: # make sure that the last element is not already there this helps prevent looped audio showing on history more than once 
                    self.History.append(self.AudioPlaying) # What ever got played add to History


                if self.QueueLoopBack:
                    self.Queue.append(self.History[-1]) # simply just add it at the end

                if self.AudioLoopBack:
                    self.Queue.insert(0, self.History[-1]) # simply just insert it back at the start





            if self.AudioPlaying:
                try:
                    if self.AudioPlaying.Status == VideoStatus.PREPARING:
                        return

                    if self.AudioPlaying.Status == VideoStatus.READY:
                        if self.Channal and not self.IsPlaying:
                            await self.PlayFunction(self.AudioPlaying.Buffer, self.Channal, self.GuildID)
                            self.IsPlaying = True

                    if self.AudioPlaying.Status == VideoStatus.NOT_INSTALLED:
                        #self.AudioPlaying.Status = "Preparing" # change the varable just in case so we dont run through errors
                        threading.Thread(target=self.AudioGraper.Donwload, args=(self.AudioPlaying.ID,)).start()


                    if self.AudioPlaying.Status == VideoStatus.ERROR:
                        self.AudioPlaying.Buffer = None
                        self.AudioPlaying.Status = VideoStatus.NOT_INSTALLED
                        self.AudioData = []
                        self.IsPlaying = False
                        self.AudioPlaying = None
                except:
                    pass