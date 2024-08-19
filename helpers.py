from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix import YouTube
from pytubefix.cli import on_progress
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import time
import typer
import questionary
from rich.progress import Progress, SpinnerColumn, TextColumn

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def dl_yt_audio(link="", target_path="downloads"):
    """
    Downloads the audio from a YouTube video and saves it to the target path.

    returns the video's yt UUID. Use for caching purposes.

    and returns the length of the video in milliseconds. for chunking
    """

    link = questionary.text("Please enter the YouTube video link:").ask()

    yt = YouTube(link, on_progress_callback=on_progress)

    # for caching purposes later
    vid_uuid = yt.video_id

    # Confirm the video name before downloading
    confirm = questionary.confirm(
        f"\n'{yt.title}'\n\nConfirm download?", default=True
    ).ask()
    if not confirm:
        typer.echo("Download cancelled.")
        return

    audio_streams = yt.streams.filter(only_audio=True)
    len_in_sec = yt.length
    len_in_ms = len_in_sec * 1000

    ys = yt.streams.get_audio_only()

    ys.download(mp3=True, output_path=target_path)

    typer.echo(f"✅ Download Complete!")

    return vid_uuid, len_in_ms, yt.title


def transcribe_or_translate_audio(file_path, len_in_ms, vid_uuid, lang="en"):
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
            language=lang,
        )

        end_time = time.time()

        print(f"Translation took {end_time - start_time:.2f} seconds")

        # write to file in /transcriptions
        with open(f"transcriptions/{lang}_{vid_uuid}.txt", "a") as f:
            f.write(transcription.text)
        current_chunk = i // chunk_length_ms + 1
        percentage_completion = (current_chunk / total_chunks) * 100
        print(f"Completed {percentage_completion:.2f}%")


def lang_select():
    lang_choices = ["en", "es", "fr", "de", "it", "ja"]
    lang_selection = questionary.select(
        "Please choose a language:", choices=lang_choices
    ).ask()
    typer.echo(f"Selected language: {lang_selection}")
    return lang_selection
