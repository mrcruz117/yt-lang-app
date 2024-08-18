from pytubefix import YouTube
from pytubefix.cli import on_progress
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import io


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

yt_vid_link = "https://www.youtube.com/watch?v=RA0NikgVcg0"

yt = YouTube(yt_vid_link, on_progress_callback=on_progress)
print(yt.title)


audio_streams = yt.streams.filter(only_audio=True)
len_in_sec = yt.length
len_in_ms = len_in_sec * 1000

# print("Audio Streams: ", audio_streams)
ys = yt.streams.get_audio_only()

ys.download(mp3=True, output_path="downloads")

file_path = "downloads/" + yt.title + ".mp3"

# audio_file = open(file_path, "rb")
audio_segment = AudioSegment.from_file(file_path, "mp4")

chunk_length_ms = 10000 * 60  # 10 min

# clear folder contents
os.system("rm -rf chunks/*")
os.system("rm -rf transcriptions/*")

for i in range(0, len_in_ms, chunk_length_ms):
    print(f"Processing chunk {i} to {i + chunk_length_ms}")
    chunk = audio_segment[i : i + chunk_length_ms]
    chunk.export(f"chunks/chunk_{i}.mp3", format="mp3")

    # get transcription
    print("Transcribing chunk...")
    audio_file = open(f"chunks/chunk_{i}.mp3", "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    # write to file in /transcriptions
    with open("transcriptions/transcription_" + yt.video_id + ".txt", "a") as f:
        f.write(transcription.text)


# Convert the AudioSegment to a file-like object
# first_1_minute.export("chunks/clip.mp3", format="mp3")

# audio_file = open("chunks/clip.mp3", "rb")


# transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

# print(transcription.text)

# for i, chunk in enumerate(chunks):
#     chunk_io = io.BytesIO()
#     chunk.export(chunk_io, format="mp3")
#     chunk_io.seek(0)

#     transcription = client.audio.transcriptions.create(model="whisper-1", file=chunk_io)
#     print(f"Chunk {i + 1}/{len(chunks)}: {transcription.text}")
