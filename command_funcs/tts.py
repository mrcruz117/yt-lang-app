import os
import typer
import questionary
from rich.progress import Progress
from rich.console import Console
from rich.progress import (
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    BarColumn,
)
import openai
from pydub import AudioSegment
from pathlib import Path
from command_funcs.translate_convert import split_by_speaker_and_length

console = Console()
progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:.0f}%"),
    TimeElapsedColumn(),
)
client = openai.Client()


def text_to_speech(path=None):
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

    processed_script = split_by_speaker_and_length(path)
    voices = ["alloy", "onyx", "echo", "nova", "shimmer"]
    voice_selection = {
        "Speaker A": voices[0],
        "Speaker B": voices[1],
        "Speaker C": voices[2],
        "Speaker D": voices[3],
        "Speaker E": voices[4],
    }

    file_name = Path(path).stem
    temp_files = []
    speech_file_path = f"text_to_speech/{file_name}_tts.mp3"
    with progress:
        tts_progress = progress.add_task(
            "[blue]Converting to speech: ", total=len(processed_script)
        )
        for i, part in enumerate(processed_script):
            speaker = part[0]
            voice = voice_selection[speaker]
            for chunk in part[1]:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=chunk,
                )

                temp_file_path = f"text_to_speech/temp/temp_chunk_{i}.mp3"
                response.stream_to_file(temp_file_path)
                temp_files.append(temp_file_path)
                progress.update(tts_progress, advance=1)

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
