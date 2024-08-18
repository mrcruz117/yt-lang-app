from pytubefix import YouTube
from pytubefix.cli import on_progress
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("KEY: ", OPENAI_API_KEY)

client = OpenAI(api_key=OPENAI_API_KEY)

yt_vid_link = "https://www.youtube.com/watch?v=RA0NikgVcg0"

yt = YouTube(yt_vid_link, on_progress_callback=on_progress)
print(yt.title)


audio_streams = yt.streams.filter(only_audio=True, file_extension="mp4")

ys = yt.streams.get_audio_only()
ys.download(mp3=True, output_path="downloads")

file_path = "downloads/" + yt.title + ".mp3"

audio_file = open(file_path, "rb")

transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

print(transcription.text)
