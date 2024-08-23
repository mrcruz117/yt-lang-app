from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix import YouTube
from pytubefix.cli import on_progress
from openai import OpenAI
import os
import shutil
from mutagen.easyid3 import EasyID3
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

progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:.0f}%"),
    TimeElapsedColumn(),
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

    # audio_streams = yt.streams.filter(only_audio=True)
    len_in_sec = yt.length
    len_in_ms = len_in_sec * 1000

    ys = yt.streams.get_audio_only()

    ys.download(mp3=True, output_path=target_path)

    console.print("[green]✅ Download Complete![/green]")

    return vid_uuid, len_in_ms, yt.title


def transcribe_or_translate_audio(file_path, len_in_ms, vid_uuid, lang="en"):
    audio_segment = AudioSegment.from_file(file_path, "mp4")

    chunk_length_ms = 1000 * 60 * 20  # 20 min

    with progress:
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
                prompt="Transcribe this audio to the selected language. Try to include punctuation where appropriate.",
            )

            # write to file in /transcriptions
            with open(f"transcriptions/{vid_uuid}_{lang}.txt", "a") as f:
                f.write(transcription.text)

            progress.update(translate_progress, advance=chunk_length_ms)
        progress.stop()
        console.print("[green]✅ Transcription Complete![/green]")
        os.system("rm -rf chunks/*")


def generate_corrected_transcript(path=None):

    file_choices = os.listdir("transcriptions")

    if not file_choices:
        typer.echo("No files to convert.")
        return
    else:
        file = questionary.select(
            "Please choose a file to convert level:", choices=file_choices
        ).ask()
        path = f"transcriptions/{file}"

    level_choices = ["A1", "A2", "B1", "B2", "C1", "C2"]
    level_choice = questionary.select(
        "Please choose a level to convert to:", choices=level_choices
    ).ask()

    full_prompt = (
        "".join(system_prompt)
        + f" Try to keep a comparable length to the source. Convert this to {level_choice} level."
    )
    text = ""
    with open(path, "r") as f:
        text = f.read()

    # split text into complete sentences
    sentences = re.split(r"[.!?。]", text)

    chunk = ""
    path = path.split(".")
    path = path[0] + f"_{level_choice.lower()}." + path[1]
    with progress:
        convert_progress = progress.add_task(
            "[blue]Converting text level: ", total=len(sentences) + 1
        )
        for sentence in sentences:
            if len(chunk) + len(sentence) < 1000:
                chunk += sentence + ". "
            else:
                chunk = chunk + "."

                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
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
            progress.update(convert_progress, advance=1)
        if chunk.strip():
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
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
        progress.update(convert_progress, advance=1)
        progress.stop()
        console.print("[green]✅ Conversion Complete![/green]")
    return stream


def text_to_speech(path="transcriptions/jlSsxyWxlaM_es.txt"):
    file_choices = os.listdir("transcriptions")

    if not file_choices:
        typer.echo("No files to convert.")
        return
    else:
        file = questionary.select(
            "Please choose a file to convert to speech:", choices=file_choices
        ).ask()
        path = f"transcriptions/{file}"

    # 4000 char chunk limit
    with open(path, "r") as f:
        text = f.read()

    sentences = re.split(r"[.!?？。！]", text)
    voice = "alloy"  # "onyx"

    chunk = ""
    file_name = Path(path).stem
    temp_files = []
    speech_file_path = f"text_to_speech/{file_name}_tts.mp3"
    with progress:
        tts_progress = progress.add_task(
            "[blue]Converting to speech: ", total=len(sentences) + 1
        )
        for i, sentence in enumerate(sentences):
            if len(chunk) + len(sentence) < 4000:
                chunk += sentence + ". "
            else:
                chunk = chunk + "."

                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=chunk,
                )

                temp_file_path = f"text_to_speech/temp/temp_chunk_{i}.mp3"
                response.stream_to_file(temp_file_path)
                temp_files.append(temp_file_path)
                chunk = sentence + ". "
            progress.update(tts_progress, advance=1)
        if chunk.strip():
            temp_file_path = f"text_to_speech/temp/temp_chunk_final.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=chunk,
            )

            response.stream_to_file(temp_file_path)
            temp_files.append(temp_file_path)
        progress.update(tts_progress, advance=1)
        progress.remove_task(tts_progress)
        progress.stop()
        console.print("[green]✅ Conversion Complete![/green]")
    with progress:
        merge_progress = progress.add_task(
            "[blue]Merging audio: ", total=len(temp_files)
        )

        # merge all temp files
        combined = AudioSegment.empty()
        for temp_file in temp_files:
            combined += AudioSegment.from_file(temp_file)
            progress.update(merge_progress, advance=1)
        # export to final file
        combined.export(speech_file_path, format="mp3")
        progress.stop()
        console.print("[green]✅ Merge Complete![/green]")

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


def export_audio():
    file_choices = os.listdir("text_to_speech")

    if not file_choices:
        typer.echo("No files to export.")
        return
    else:
        file = questionary.select(
            "Please choose a file to export:", choices=file_choices
        ).ask()
        path = f"text_to_speech/{file}"

    path_id = Path(path).stem.split("_")[0]
    export_path = f"/Users/mrcruz/Music/iTunes/iTunes Music/Ai-tts/{path_id}"

    # Ensure the export path exists and is a directory
    if not os.path.isdir(export_path):
        typer.echo(f"Error: {export_path} is not a directory.")
        confirm = questionary.confirm(
            "Would you like to create this directory?", default=True
        ).ask()
        if not confirm:
            typer.echo("Export cancelled.")
            return
        os.makedirs(export_path)
        console.print(f"[yellow]⚠️ Created directory: {export_path}[/yellow]")

    # Copy the file to the export path
    try:
        destination_path = os.path.join(export_path, os.path.basename(path))
        shutil.copy(path, destination_path)

        # Add metadata to the copied file
        audio = EasyID3(destination_path)
        audio["artist"] = "Ai-tts"
        audio["album"] = path_id
        audio.save()
        console.print(f"[yellow]⚠️ Added metadata to: {destination_path}[/yellow]")
        console.print("[green]✅ Export Complete![/green]")
        # play
        # abs_destination_path = os.path.abspath(destination_path)
        os.system(f'open "{destination_path}"')

    except Exception as e:
        console.print(f"[red]❌ Export Failed: {e}[/red]")

    return
