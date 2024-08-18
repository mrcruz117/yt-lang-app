from pytubefix import YouTube
from pytubefix.cli import on_progress
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

yt_vid_link = "https://www.youtube.com/watch?v=RA0NikgVcg0"

yt = YouTube(yt_vid_link, on_progress_callback=on_progress)
print(yt.title)


audio_streams = yt.streams.filter(only_audio=True)
len_in_sec = yt.length
len_in_ms = len_in_sec * 1000

ys = yt.streams.get_audio_only()

ys.download(mp3=True, output_path="downloads")

file_path = "downloads/" + yt.title + ".mp3"

audio_segment = AudioSegment.from_file(file_path, "mp4")

chunk_length_ms = 1000 * 60 * 10  # 10 min

# clear folder contents before processing
os.system("rm -rf chunks/*")
os.system("rm -rf transcriptions/*")

total_chunks = len_in_ms // chunk_length_ms + 1

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
    current_chunk = i // chunk_length_ms + 1
    percentage_completion = (current_chunk / total_chunks) * 100
    print(f"Completed {percentage_completion:.2f}%")