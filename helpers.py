from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix import YouTube
from pytubefix.cli import on_progress
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import time

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def dl_yt_audio(link, target_path):
    """
    Downloads the audio from a YouTube video and saves it to the target path.

    returns the video's yt UUID. Use for caching purposes.

    and returns the length of the video in milliseconds. for chunking
    """

    yt = YouTube(link, on_progress_callback=on_progress)

    # for caching purposes later
    vid_uuid = yt.video_id

    print(yt.title)

    audio_streams = yt.streams.filter(only_audio=True)
    len_in_sec = yt.length
    len_in_ms = len_in_sec * 1000

    ys = yt.streams.get_audio_only()

    ys.download(mp3=True, output_path=target_path)

    return vid_uuid, len_in_ms, yt.title


def transcribe_or_translate_audio(file_path, len_in_ms, vid_uuid):
    audio_segment = AudioSegment.from_file(file_path, "mp4")

    chunk_length_ms = 1000 * 60 * 20  # 20 min

    # clear folder contents before processing
    os.system("rm -rf chunks/*")
    os.system("rm -rf transcriptions/*")

    total_chunks = len_in_ms // chunk_length_ms + 1

    start_time = time.time()

    for i in range(0, len_in_ms, chunk_length_ms):
        print(f"Processing chunk {i} to {i + chunk_length_ms}")
        chunk = audio_segment[i : i + chunk_length_ms]
        chunk.export(f"chunks/chunk_{i}.mp3", format="mp3")

        # get transcription
        print("Transcribing/translating chunk...")
        audio_file = open(f"chunks/chunk_{i}.mp3", "rb")
        # This worked! :)
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="fr",
        )

        end_time = time.time()

        print(f"Translation took {end_time - start_time:.2f} seconds")

        # write to file in /transcriptions
        with open("transcriptions/transcription_" + vid_uuid + ".txt", "a") as f:
            f.write(transcription.text)
        current_chunk = i // chunk_length_ms + 1
        percentage_completion = (current_chunk / total_chunks) * 100
        print(f"Completed {percentage_completion:.2f}%")
