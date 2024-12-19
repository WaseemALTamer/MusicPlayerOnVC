from discord.ext import commands
from GuildPlayer import Player
import discord.ext.commands
import discord.ext
import threading
import discord
import asyncio
import random
import io


      



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

        @self.Bot.tree.command(name='playlist', description='Play a playlist through its YouTube URL')
        async def playlist(interaction: discord.Interaction, url: str):
            await self.On_PlayList(interaction, url)

        @self.Bot.tree.command(name='skip', description="Skip the currently playing song")
        async def skip(interaction: discord.Interaction):
            await self.On_Skip(interaction)

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


    async def On_Skip(self, interaction):
        Channal = interaction.guild.voice_client
        Channal.stop()
        await interaction.response.send_message(f'Skiped')


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
        _channel = _user.voice.channel
        self.InitNewGuild(_discordServerID)  # try to initiate the new server components

        if _user.voice is None:
            await interaction.response.send_message("You're not in a voice channel!")
            return

        # If the bot is not already connected, connect it to the channel
        if interaction.guild.voice_client is None:
            await _channel.connect()
        else:
            await interaction.guild.voice_client.move_to(_channel)

        self.Guilds[_discordServerID].Channal = interaction.guild.voice_client
        await interaction.response.send_message(f'imported the audio content')
        threading.Thread(target=self.Guilds[_discordServerID].AddToQueue, args=(url,)).start()



    async def On_PlayList(self, interaction, url):
        _user = interaction.user
        _discordServerID = _user.guild.id
        _channel = _user.voice.channel
        self.InitNewGuild(_discordServerID)  # try to initiate the new server components

        if _user.voice is None:
            await interaction.response.send_message("You're not in a voice channel!")
            return

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