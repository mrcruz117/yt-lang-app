import os
import questionary
from pydub import AudioSegment
import typer
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    BarColumn,
)
from rich.console import Console
import assemblyai as aai
from db.db_funcs import get_title_id_dict, get_media_info


AAI_API_KEY = os.getenv("AAI_API_KEY")
aai.settings.api_key = AAI_API_KEY
console = Console()
transcriber = aai.Transcriber()


progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:.0f}%"),
    TimeElapsedColumn(),
)


def transcribe_audio(lang=""):

    all_items = os.listdir("downloads")
    file_choices = [item for item in all_items if item.endswith(".mp3")]

    if not file_choices:
        typer.echo("No files to convert.")
        return
    else:
        file = questionary.select(
            "Please choose a file to convert level:", choices=file_choices
        ).ask()
        audio_path = f"downloads/{file}"

    expected_speaker_count = questionary.select(
        "How many speakers are in the audio?", choices=["1", "2", "3", "4", "5"]
    ).ask()
    expected_speaker_count = int(expected_speaker_count)

    title_dict = get_title_id_dict()
    # remove the .mp3 extension
    title = file[:-4]
    vid_uuid = title_dict[title]

    info = get_media_info(vid_uuid)
    len_in_ms = info["length"] * 1000

    audio_segment = AudioSegment.from_file(audio_path, "mp4")
    chunk_length_ms = 1000 * 60 * 20  # 20 min
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speakers_expected=expected_speaker_count,
        speech_model=aai.SpeechModel.nano,
        # language_code="en-US",
    )
    with progress:
        text_progress = progress.add_task("[blue]Converting to text: ", total=len_in_ms)
        count = 0
        for i in range(0, len_in_ms, chunk_length_ms):

            chunk = audio_segment[i : i + chunk_length_ms]
            chunk.export(f"chunks/chunk_{count}.mp3", format="mp3")

            # get transcription/translation
            audio_file = open(f"chunks/chunk_{count}.mp3", "rb")
            count += 1
            transcript = transcriber.transcribe(audio_file, config)

            # write to file in /transcriptions
            for utterance in transcript.utterances:
                # $$ is to help separate the clips by speaker
                clip = f"Speaker {utterance.speaker}: {utterance.text}$$\n"
                with open(f"transcriptions/{vid_uuid}_{lang}.txt", "a") as f:
                    f.write(clip)

            progress.update(text_progress, advance=chunk_length_ms)
        progress.stop()
        console.print("[green]✅ Transcription Complete![/green]")
        os.system("rm -rf chunks/*")
