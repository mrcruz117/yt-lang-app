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
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    BarColumn,
)
from rich.console import Console
from db.db_funcs import add_media_info
import re
from pathlib import Path

step_progress = Progress(
    SpinnerColumn("simpleDots"),
)

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
console = Console()

system_prompt = (
    "You are a language model assistant helping a user transcribe and translate a YouTube video. ",
    "You are an expert on the CEFR scale and can provide accurate translations in multiple languages ",
    "while also converting the content to a different level on the CEFR scale. ",
    "(A1, A2, B1, B2, C1, C2) ",
)


def dl_yt_audio(link="", target_path="downloads"):
    """
    Downloads the audio from a YouTube video and saves it to the target path.

    returns the video's yt UUID. Use for caching purposes.

    and returns the length of the video in milliseconds. for chunking
    """
    if not link:
        link = questionary.text("Please enter the YouTube video link:").ask()

    yt = YouTube(link, on_progress_callback=on_progress)

    # for caching purposes later
    vid_uuid = yt.video_id

    # add_media_info(yt)

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

    console.print("[green]✅ Download Complete![/green]")

    return vid_uuid, len_in_ms, yt.title


def transcribe_or_translate_audio(file_path, len_in_ms, vid_uuid, lang="en"):
    audio_segment = AudioSegment.from_file(file_path, "mp4")

    chunk_length_ms = 1000 * 60 * 20  # 20 min

    # clear folder contents before processing
    os.system("rm -rf chunks/*")
    os.system("rm -rf transcriptions/*")

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        translate_progress = progress.add_task("[blue]Translating: ", total=len_in_ms)
        count = 0
        for i in range(0, len_in_ms, chunk_length_ms):

            chunk = audio_segment[i : i + chunk_length_ms]
            chunk.export(f"chunks/chunk_{count}.mp3", format="mp3")

            # get transcription/translation
            audio_file = open(f"chunks/chunk_{count}.mp3", "rb")
            count += 1
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=lang,
            )
            # post process here

            # write to file in /transcriptions
            with open(f"transcriptions/{vid_uuid}_{lang}.txt", "a") as f:
                f.write(transcription.text)

            progress.update(translate_progress, advance=chunk_length_ms)
        progress.stop()
        console.print("[green]✅ Transcription Complete![/green]")


def generate_corrected_transcript(path):
    full_prompt = (
        "".join(system_prompt)
        + " Try to keep a comparable length to the source. Convert this to A1 level."
    )
    text = ""
    with open(path, "r") as f:
        text = f.read()

    # split text into complete sentences
    sentences = re.split(r"[.!?]", text)

    chunk = ""
    path = path.split(".")
    path = path[0] + "_a1." + path[1]
    for sentence in sentences:
        if len(chunk) + len(sentence) < 1000:
            chunk += sentence + ". "
        else:
            chunk = chunk + "."

            print("chunk formed: ", chunk[:50])
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": chunk},
                ],
                stream=True,
            )
            # typer.echo(stream)

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:

                    with open(f"{path}", "a") as f:
                        f.write(chunk.choices[0].delta.content)
            chunk = sentence + ". "
    if chunk.strip():
        print("final chunk formed: ", chunk)
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": chunk},
            ],
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                with open(f"{path}", "a") as f:
                    f.write(chunk.choices[0].delta.content)
    return stream


def text_to_speech(path="transcriptions/jlSsxyWxlaM_es.txt"):
    # 4000 char chunk limit
    with open(path, "r") as f:
        text = f.read()

    sentences = re.split(r"[.!?]", text)
    voice = "alloy"  # "onyx"

    chunk = ""
    file_name = Path(path).stem
    temp_files = []
    speech_file_path = f"text_to_speech/{file_name}_tts.mp3"
    for i, sentence in enumerate(sentences):
        if len(chunk) + len(sentence) < 4000:
            chunk += sentence + ". "
        else:
            chunk = chunk + "."

            print("chunk formed: ", chunk[:50])

            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=chunk,
            )

            temp_file_path = f"text_to_speech/temp/temp_chunk_{i}.mp3"
            response.stream_to_file(temp_file_path)
            temp_files.append(temp_file_path)
            chunk = sentence + ". "
    if chunk.strip():
        print("final chunk formed: ", chunk[:50])
        temp_file_path = f"text_to_speech/temp/temp_chunk_final.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=chunk,
        )

        response.stream_to_file(temp_file_path)
        temp_files.append(temp_file_path)

    # merge all temp files
    combined = AudioSegment.empty()
    for temp_file in temp_files:
        combined += AudioSegment.from_file(temp_file)

    # export to final file
    combined.export(speech_file_path, format="mp3")

    # Clean up temporary files
    for temp_file in temp_files:
        os.remove(temp_file)


def lang_select():
    lang_choices = ["english", "spanish", "french", "german", "italian", "japanese"]

    lang_selection = questionary.select(
        "Please choose a language:", choices=lang_choices
    ).ask()

    lang = {
        "english": "en",
        "spanish": "es",
        "french": "fr",
        "german": "de",
        "italian": "it",
        "japanese": "ja",
    }

    return lang[lang_selection]
