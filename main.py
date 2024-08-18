from pytubefix import YouTube
from pytubefix.cli import on_progress
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import io


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("KEY: ", OPENAI_API_KEY)

client = OpenAI(api_key=OPENAI_API_KEY)

yt_vid_link = "https://www.youtube.com/watch?v=RA0NikgVcg0"

yt = YouTube(yt_vid_link, on_progress_callback=on_progress)
print(yt.title)


audio_streams = yt.streams.filter(only_audio=True)

# print("Audio Streams: ", audio_streams)
ys = yt.streams.get_audio_only()
print(ys)

ys.download(mp3=True, output_path="downloads")

file_path = "downloads/" + yt.title + ".mp3"

# audio_file = open(file_path, "rb")
audio_segment = AudioSegment.from_file(file_path, "mp4")

chunk_length_ms = 1000 * 60  # 1 min

first_1_minute = audio_segment[:chunk_length_ms]

# Convert the AudioSegment to a file-like object
first_1_minute.export("chunks/clip.mp3", format="mp3")

audio_file = open("chunks/clip.mp3", "rb")


transcription = client.audio.transcriptions.create(
    model="whisper-1", file=audio_file
)

print(transcription.text)

# for i, chunk in enumerate(chunks):
#     chunk_io = io.BytesIO()
#     chunk.export(chunk_io, format="mp3")
#     chunk_io.seek(0)

#     transcription = client.audio.transcriptions.create(model="whisper-1", file=chunk_io)
#     print(f"Chunk {i + 1}/{len(chunks)}: {transcription.text}")
