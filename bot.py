import os
import discord
from discord.ext import commands
import yt_dlp

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

ytdl_options = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": False,
    "default_search": "ytsearch1",
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    }
}

ffmpeg_options = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(ytdl_options)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("ش "):
        song_name = message.content[2:].strip()

        if not song_name:
            await message.channel.send("⚠️ Enter a song name.")
            return

        if not message.author.voice:
            await message.channel.send("🎧 Join a voice channel first.")
            return

        voice_channel = message.author.voice.channel

        if message.guild.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = message.guild.voice_client
            if vc.channel != voice_channel:
                await vc.move_to(voice_channel)

        await message.channel.send("Searching...")

        try:
            info = ytdl.extract_info(song_name, download=False)

            if "entries" in info:
                info = info["entries"][0]

            audio_url = info["url"]
            title = info.get("title", "الأغنية")

            duration = info.get("duration", 0)
            minutes = duration // 60
            seconds = duration % 60

            if vc.is_playing():
                vc.stop()

            source = discord.FFmpegPCMAudio(
                audio_url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                **ffmpeg_options
            )

            vc.play(source)

            await message.channel.send(
    f"╭─ 🎵 Now Playing\n"
    f"├ **{title}**\n"
    f"├ ⏱️ {minutes}:{seconds:02d}\n"
    f"╰ {message.author.mention}"
)

        except Exception as e:
            await message.channel.send("❌ Playback Error")
            print(e)

    elif message.content == "س":
        vc = message.guild.voice_client

        if vc and vc.is_playing():
            vc.stop()
            await message.channel.send("قفلنا قفلنا")
        else:
            await message.channel.send("⚠️ Nothing is currently playing.")


bot.run(TOKEN)