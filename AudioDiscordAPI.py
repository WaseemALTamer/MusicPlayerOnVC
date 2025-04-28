from Constants import VideoStatus
from discord.ext import commands
from GuildPlayer import Player
import threading
import discord
import asyncio
import random
import io
import gc


      



class AudioAPI():

    def __init__(self, Token, TickRate=5):
        
        self.Token = Token
        self.TickRate = TickRate # this only controls the update functions
        
        self.intents = discord.Intents.all()
        self.intents.message_content = True
        self.intents.voice_states = True  # Enable voice state intent
        self.Bot = commands.Bot(command_prefix='/', intents=self.intents)

        self.Guilds = {
                #GuildID : <Player From GuildPlayer>
        }


        self.setup_commands()
        self.Bot.run(self.Token)
        





    def setup_commands(self):
        @self.Bot.tree.command(name='play', description='Play a song through a YouTube URL')
        async def play(interaction: discord.Interaction, url: str):
            await self.OnPlay(interaction, url)

        @self.Bot.tree.command(name='play_next', description='Play a song Next through a YouTube URL')
        async def playNext(interaction: discord.Interaction, url: str):
            await self.OnPlayNext(interaction, url)

        @self.Bot.tree.command(name='loop_queue', description='puts the song that end at the end of the Queue -> Takse: [(True or False), (1,0)]')
        async def LoopQueue(interaction: discord.Interaction, state: bool):
            await self.OnLoopQueue(interaction, state)

        @self.Bot.tree.command(name='loop', description='Repeats the Audio after it ends -> Takse: [(True or False), (1,0)]')
        async def Loop(interaction: discord.Interaction, state: bool):
            await self.OnLoop(interaction, state)

        @self.Bot.tree.command(name='playlist', description='Play a playlist through its YouTube URL')
        async def playlist(interaction: discord.Interaction, url: str):
            await self.On_PlayList(interaction, url)

        @self.Bot.tree.command(name='skip', description="Skip the currently playing song")
        async def skip(interaction: discord.Interaction):
            await self.On_Skip(interaction)

        @self.Bot.tree.command(name='skip_chunk', description='Skips the current song + next <Num> songs')
        async def SkipChunk(interaction: discord.Interaction, num: int):
            await self.OnSkipChunk(interaction, num)

        @self.Bot.tree.command(name='queue_pop', description='Removes Specific song from Queue 1 being the first on the queue')
        async def QueuePop(interaction: discord.Interaction, num: int):
            await self.OnQueuePop(interaction, num)

        @self.Bot.tree.command(name='disconnect', description="Disconnect the bot from the voice channel")
        async def disconnect(interaction: discord.Interaction):
            await self.OnDisconnect(interaction)

        @self.Bot.tree.command(name="pause", description="Pause the music that is playing")
        async def pause(interaction: discord.Interaction):
            await self.On_Pause(interaction)

        @self.Bot.tree.command(name="resume", description="Resume the music that is playing")
        async def resume(interaction: discord.Interaction):
            await self.On_Resume(interaction)

        @self.Bot.tree.command(name="show_queue", description="Shows the queue")
        async def show_queue(interaction: discord.Interaction):
            await self.On_Show_Queue(interaction)

        @self.Bot.tree.command(name="show_history", description="Shows the queue")
        async def show_history(interaction: discord.Interaction):
            await self.On_Show_History(interaction)

        @self.Bot.tree.command(name="clear_queue", description="Clear the current queue")
        async def clear_queue(interaction: discord.Interaction):
            await self.On_Clear_Queue(interaction)

        @self.Bot.tree.command(name="shuffle_queue", description="Shuffle the content of the queue")
        async def shuffle_queue(interaction: discord.Interaction):
            await self.On_Shuffle_Queue(interaction)

        @self.Bot.tree.command(name="currently_playing", description="Show current song playing")
        async def currently_playing(interaction: discord.Interaction):
            await self.On_Currently_Playing(interaction)


        @self.Bot.event
        async def on_ready():
            print(f'Logged in as {self.Bot.user}!')
            asyncio.create_task(self.Update())  # Start the Update loop
            await self.Bot.tree.sync()  # Sync slash commands with Discord
            print("Commands synced successfully!")


        @self.Bot.event
        async def on_voice_state_update(member, before, after):
            if member.bot:
                return

            voice_client = discord.utils.get(self.Bot.voice_clients, guild=member.guild)
            if voice_client is None or not voice_client.is_connected():
                return

            channel = voice_client.channel
            if len([m for m in channel.members if not m.bot]) == 0: # Checks if the bot is the last one in the VC
                try:
                    await voice_client.disconnect()
                    _guildID = member.guild.id
                    if _guildID in self.Guilds:
                        self.Guilds[_guildID].Queue = []
                        self.Guilds[_guildID].IsPlaying = False
                        self.Guilds[_guildID].AudioPlaying = None
                        threading.Thread(target=gc.collect).start() # start the garbage collector on another thread 
                    print(f"Disconnected from {channel} in {member.guild.name} because it was empty.")
                except Exception as e:
                    print(f"Error while auto-disconnecting from empty channel: {e}")









    async def On_Skip(self, interaction):
        Channal = interaction.guild.voice_client
        Channal.stop()
        await interaction.response.send_message(f'Skiped')


    async def OnSkipChunk(self, interaction, Num):
        Channal = interaction.guild.voice_client
        _guildID = interaction.user.guild.id
        Queue = self.Guilds[_guildID].Queue
        Channal.stop()
        for i in range(Num):
            Queue.pop(0)
        await interaction.response.send_message(f'Skiped curernt song and the next {Num} songs')

    async def OnQueuePop(self, interaction, Num):
        Channal = interaction.guild.voice_client
        _guildID = interaction.user.guild.id
        Queue = self.Guilds[_guildID].Queue
        Song = Queue[Num - 1]
        Queue.pop(Num - 1)  # -1 since we dont take it by index we take it as the list represented for the user
                            # sorry developers the array strt from 1 as everybody else thinks
        await interaction.response.send_message(f'Removed "{Song.Name != VideoStatus.UNKNOWN_TITLE or Song.ID}" from Queue')

    async def On_Pause(self, interaction):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)

        Channal = interaction.guild.voice_client
        if Channal is not None:
            Channal.pause()
        await interaction.response.send_message(f'Paused')


    async def On_Resume(self, interaction):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)

        Channal = interaction.guild.voice_client
        if Channal is not None:
            Channal.resume()
        await interaction.response.send_message(f'Resumed')

    async def OnLoopQueue(self, interaction, state):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)
        _guildID = interaction.user.guild.id

        self.Guilds[_guildID].SetQueueLoopBack(state)

        await interaction.response.send_message(f"Queue Looping -> {self.Guilds[_guildID].QueueLoopBack}")


    async def OnLoop(self, interaction, state):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)
        _guildID = interaction.user.guild.id


        
        self.Guilds[_guildID].SetAudioLoopBack(state)

        await interaction.response.send_message(f"Queue Looping -> {self.Guilds[_guildID].AudioLoopBack}")


    async def On_Show_Queue(self, interaction):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)

        _guildID = interaction.user.guild.id
        Queue = self.Guilds[_guildID].Queue
        SongPlaying = self.Guilds[_guildID].AudioPlaying

        Message = "Queue" + "\n"
        Message += "======================" + "\n"
        if SongPlaying:
            Message += f"Current Song Playing -> {SongPlaying.Name}" + "\n"
        else:
            Message += f"Current Song Playing -> None" + "\n"
            
        for index, Object in enumerate(Queue):
            if Object.Name != VideoStatus.UNKNOWN_TITLE:
                if len(Message + str(Object.Name)) >= 1800:
                    Message += "======================" + "\n"
                    Message += f"+{len(Queue) - (index + 1)} More on Queue" + "\n"
                    break
                Message += "======================" + "\n"
                Message += f"{index + 1}. {Object.Name}" + "\n"
            else:
                if len(Message + str(Object.ID)) >= 1800:
                    Message += "======================" + "\n"
                    Message += f"+{len(Queue) - (index + 1)} More on Queue" + "\n"
                    break
                Message += "======================" + "\n"
                Message += f"{index + 1}. <https://www.youtube.com/{Object.ID}>" + "\n"

        Message += "======================" + "\n"
        await interaction.response.send_message(Message)


    async def On_Show_History(self, interaction):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)

        _guildID = interaction.user.guild.id
        Queue = self.Guilds[_guildID].History
        SongPlaying = self.Guilds[_guildID].AudioPlaying

        Message = "Queue" + "\n"
        Message += "======================" + "\n"
        if SongPlaying:
            Message += f"Current Song Playing -> {SongPlaying.Name}" + "\n"
        else:
            Message += f"Current Song Playing -> None" + "\n"
            
        for index, Object in enumerate(Queue):
            if Object.Name:
                if len(Message + str(Object.Name)) >= 1800:
                    Message += "======================" + "\n"
                    Message += f"+{len(Queue) - (index + 1)} More on Queue" + "\n"
                    break
                Message += "======================" + "\n"
                Message += f"{index + 1}. {Object.Name}" + "\n"
            else:
                if len(Message + str(Object.ID)) >= 1800:
                    Message += "======================" + "\n"
                    Message += f"+{len(Queue) - (index + 1)} More on Queue" + "\n"
                    break
                Message += "======================" + "\n"
                Message += f"{index + 1}. <https://www.youtube.com/{Object.ID}>" + "\n"

        Message += "======================" + "\n"
        await interaction.response.send_message(Message)


    async def On_Currently_Playing(self, interaction):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)

        _guildID = interaction.user.guild.id
        SongPlaying = self.Guilds[_guildID].AudioPlaying
        Message = "No song is playing currently"
        if SongPlaying:
            Message = f"{SongPlaying.Name}" + "\n"
            Message += f"https://www.youtube.com/{SongPlaying.ID}"

        await interaction.response.send_message(Message)


    async def OnDisconnect(self, interaction):
        Channal = interaction.guild.voice_client
        if Channal is not None:
            _guildID = interaction.user.guild.id
            self.Guilds[_guildID].Queue = []
            self.Guilds[_guildID].AudioData.clear()
            Channal.stop()
            await Channal.disconnect()
        await interaction.response.send_message(f'Disconnected')



    async def On_Clear_Queue(self, interaction):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)
        _guildID = interaction.user.guild.id
        self.Guilds[_guildID].Queue = []
        await interaction.response.send_message(f'Cleared the Queue')

    async def On_Shuffle_Queue(self, interaction):
        _discordServerID = interaction.user.guild.id
        self.InitNewGuild(_discordServerID)

        _guildID = interaction.user.guild.id
        random.shuffle(self.Guilds[_guildID].Queue)
        await interaction.response.send_message(f'Shuffled the Queue')


    async def OnPlay(self, interaction, url): # Intraction\
        _user = interaction.user
        _discordServerID = _user.guild.id

        if not _user.voice or not _user.voice.channel:
            Message = f"You're not in a voice channel!"
            await interaction.response.send_message(Message)
            return # return if the user is not in the channal
        
        _channel = _user.voice.channel

        self.InitNewGuild(_discordServerID)  # try to initiate the new server components


        # If the bot is not already connected, connect it to the channel
        if interaction.guild.voice_client is None:
            await _channel.connect()
        else:
            await interaction.guild.voice_client.move_to(_channel)

        self.Guilds[_discordServerID].Channal = interaction.guild.voice_client
        await interaction.response.send_message(f'imported the audio content')
        threading.Thread(target=self.Guilds[_discordServerID].AddToQueue, args=(url,)).start()



    async def OnPlayNext(self, interaction, url): # Intraction\
        _user = interaction.user
        _discordServerID = _user.guild.id

        if not _user.voice or not _user.voice.channel:
            Message = f"You're not in a voice channel!"
            await interaction.response.send_message(Message)
            return # return if the user is not in the channal
        
        _channel = _user.voice.channel

        self.InitNewGuild(_discordServerID)  # try to initiate the new server components


        # If the bot is not already connected, connect it to the channel
        if interaction.guild.voice_client is None:
            await _channel.connect()
        else:
            await interaction.guild.voice_client.move_to(_channel)

        self.Guilds[_discordServerID].Channal = interaction.guild.voice_client
        await interaction.response.send_message(f'imported the audio content')
        threading.Thread(target=lambda: self.Guilds[_discordServerID].AddToQueue(url, None, 0)).start()



    async def On_PlayList(self, interaction, url):
        _user = interaction.user
        _discordServerID = _user.guild.id

        if not _user.voice or not _user.voice.channel:
            Message = f"You're not in a voice channel!"
            await interaction.response.send_message(Message)
            return # return if the user is not in the channal
        
        _channel = _user.voice.channel


        

        self.InitNewGuild(_discordServerID)  # try to initiate the new server components


        # If the bot is not already connected, connect it to the channel
        if interaction.guild.voice_client is None:
            await _channel.connect()
        else:
            await interaction.guild.voice_client.move_to(_channel)

        self.Guilds[_discordServerID].Channal = interaction.guild.voice_client
        await interaction.response.send_message(f'imported the playList')
        threading.Thread(target=self.Guilds[_discordServerID].AddPlayList, args=(url,)).start()

        

        


    async def PlaySound(self, Buffer, Channal, GuildID):
        try:
            AudioSource = io.BytesIO(Buffer)
            AudioSource = discord.FFmpegPCMAudio(source=AudioSource, pipe=True)
            Channal.play(AudioSource, bitrate=196, signal_type="music", fec=True, expected_packet_loss=0.15,
                                after=lambda error: self.OnAudioEnd(GuildID))
        except:
            pass



    async def Update(self):
        try:
            for Key, Object in self.Guilds.items(): # this will update all the functions
                if not Object.Channal.is_connected():
                    Object.IsPlaying = False
                    Object.AudioPlaying = None
                    Object.Channal = None
                    Object.Queue = []
                    Object.AudioData.clear()
                await Object.Update()
        except:
            pass

        # set the loop back
        await asyncio.sleep(1/ self.TickRate)
        asyncio.create_task(self.Update())



    def OnAudioEnd(self, GuildID):
        self.Guilds[GuildID].IsPlaying = False
        self.Guilds[GuildID].AudioPlaying = None



    def InitNewGuild(self, GuildID):
        try:
            self.Guilds[GuildID]
        except:
            Component = self.Guilds[GuildID] = Player()
            Component.PlayFunction = self.PlaySound
            Component.GuildID = GuildID