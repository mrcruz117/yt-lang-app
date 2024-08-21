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


def transcribe_audio(len_in_ms, vid_uuid, lang=""):

    expected_speaker_count = questionary.select(
        "How many speakers are in the audio?", choices=["1", "2", "3", "4", "5"]
    ).ask()
    expected_speaker_count = int(expected_speaker_count)
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speakers_expected=expected_speaker_count,
        speech_model=aai.SpeechModel.nano,
        # language_code="en-US",
    )
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

    audio_segment = AudioSegment.from_file(audio_path, "mp4")
    chunk_length_ms = 1000 * 60 * 20  # 20 min
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


# def transcribe_or_translate_audio(file_path, len_in_ms, vid_uuid, lang="en"):
#     audio_segment = AudioSegment.from_file(file_path, "mp4")

#     chunk_length_ms = 1000 * 60 * 20  # 20 min

#     with progress:
#         translate_progress = progress.add_task("[blue]Translating: ", total=len_in_ms)
#         count = 0
#         for i in range(0, len_in_ms, chunk_length_ms):

#             chunk = audio_segment[i : i + chunk_length_ms]
#             chunk.export(f"chunks/chunk_{count}.mp3", format="mp3")

#             # get transcription/translation
#             audio_file = open(f"chunks/chunk_{count}.mp3", "rb")
#             count += 1
#             transcription = client.audio.transcriptions.create(
#                 model="whisper-1",
#                 file=audio_file,
#                 language=lang,
#                 prompt="Transcribe this audio to the selected language. Try to include punctuation where appropriate.",
#             )

#             # write to file in /transcriptions
#             with open(f"transcriptions/{vid_uuid}_{lang}.txt", "a") as f:
#                 f.write(transcription.text)

#             progress.update(translate_progress, advance=chunk_length_ms)
#         progress.stop()
#         console.print("[green]✅ Transcription Complete![/green]")
#         os.system("rm -rf chunks/*")
