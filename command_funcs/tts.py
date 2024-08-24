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
import google.cloud.texttospeech as tts
from dotenv import load_dotenv


console = Console()
progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:.0f}%"),
    TimeElapsedColumn(),
)

load_dotenv()


GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")


# def text_to_speech(path=None):
#     file_choices = os.listdir("transcriptions")

#     if not file_choices:
#         typer.echo("No files to convert.")
#         return
#     else:
#         file = questionary.select(
#             "Please choose a file to convert to speech:", choices=file_choices
#         ).ask()
#         path = f"transcriptions/{file}"

#     # 4000 char chunk limit
#     with open(path, "r") as f:
#         text = f.read()

#     processed_script = split_by_speaker_and_length(path)
#     voices = ["alloy", "onyx", "echo", "nova", "shimmer"]
#     voice_selection = {
#         "Speaker A": voices[0],
#         "Speaker B": voices[1],
#         "Speaker C": voices[2],
#         "Speaker D": voices[3],
#         "Speaker E": voices[4],
#     }

#     file_name = Path(path).stem
#     temp_files = []
#     speech_file_path = f"text_to_speech/{file_name}_tts.mp3"
#     with progress:
#         tts_progress = progress.add_task(
#             "[blue]Converting to speech: ", total=len(processed_script)
#         )
#         for i, part in enumerate(processed_script):
#             speaker = part[0]
#             voice = voice_selection[speaker]
#             for chunk in part[1]:
#                 response = client.audio.speech.create(
#                     model="tts-1",
#                     voice=voice,
#                     input=chunk,
#                 )

#                 temp_file_path = f"text_to_speech/temp/temp_chunk_{i}.mp3"
#                 response.stream_to_file(temp_file_path)
#                 temp_files.append(temp_file_path)
#                 progress.update(tts_progress, advance=1)

#         progress.update(tts_progress, advance=1)
#         progress.remove_task(tts_progress)
#         progress.stop()
#         console.print("[green]✅ Conversion Complete![/green]")
#     with progress:
#         merge_progress = progress.add_task(
#             "[blue]Merging audio: ", total=len(temp_files)
#         )

#         # merge all temp files
#         combined = AudioSegment.empty()
#         for temp_file in temp_files:
#             combined += AudioSegment.from_file(temp_file)
#             progress.update(merge_progress, advance=1)
#         # export to final file
#         combined.export(speech_file_path, format="mp3")
#         progress.stop()
#         console.print("[green]✅ Merge Complete![/green]")

#         # Clean up temporary files
#         for temp_file in temp_files:
#             os.remove(temp_file)


def google_tts(path=None):
    client = tts.TextToSpeechClient(client_options={"api_key": GOOGLE_CLOUD_API_KEY})
    file_choices = os.listdir("transcriptions")

    if not file_choices:
        typer.echo("No files to convert.")
        return
    else:
        if not path:
            file = questionary.select(
                "Please choose a file to convert to speech:", choices=file_choices
            ).ask()
            path = f"transcriptions/{file}"
    file = None
    if not file:
        file = os.path.basename(path)

    with open(path, "r") as f:
        text = f.read()
    voices_by_lang = voice_gen()
    lang = find_lang(file)

    voices = voices_by_lang[lang]

    processed_script = split_by_speaker_and_length(path=path, max_length=4000)

    file_name = Path(path).stem
    temp_files = []

    speech_file_path = f"text_to_speech/{file_name}_tts.mp3"

    # clear chunks directory
    temp_dir = "text_to_speech/temp"
    for file in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    with progress:

        tts_progress = progress.add_task(
            "[blue]Converting to speech: ", total=len(processed_script)
        )
        for i, part in enumerate(processed_script):
            speaker = part[0]

            voice = voices[speaker]

            for j, text_chunk in enumerate(part[1]):
                # console.print(len(text_chunk))
                text_input = tts.SynthesisInput(text=text_chunk)
                voice_params = tts.VoiceSelectionParams(language_code=lang, name=voice)
                audio_config = tts.AudioConfig(
                    audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.8
                )
                response = client.synthesize_speech(
                    input=text_input,
                    voice=voice_params,
                    audio_config=audio_config,
                )

                temp_file_path = f"text_to_speech/temp/temp_chunk_{i}_{j}.mp3"
                with open(temp_file_path, "wb") as out:
                    out.write(response.audio_content)
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

    # text_input = tts.SynthesisInput(text="This is a test. Hello world!")
    # voice_params = tts.VoiceSelectionParams(
    #     language_code="en-US", name="en-US-Journey-D"
    # )
    # audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
    # response = client.synthesize_speech(
    #     input=text_input,
    #     voice=voice_params,
    #     audio_config=audio_config,
    # )

    # with open("text_to_speech/test-output.mp3", "wb") as out:
    #     out.write(response.audio_content)


def unique_languages_from_voices(voices):
    language_set = set()
    for voice in voices:
        for language_code in voice.language_codes:
            language_set.add(language_code)
    return language_set


def list_languages():
    client = tts.TextToSpeechClient(client_options={"api_key": GOOGLE_CLOUD_API_KEY})

    response = client.list_voices()
    console.print(response.voices)
    languages = unique_languages_from_voices(response.voices)

    print(f" Languages: {len(languages)} ".center(60, "-"))
    for i, language in enumerate(sorted(languages)):
        print(f"{language:>10}", end="\n" if i % 5 == 4 else "")


def voice_gen():
    voices = {
        "en-US": {
            "Speaker A": "en-US-Wavenet-B",
            "Speaker B": "en-US-Wavenet-I",
            "Speaker C": "en-US-Wavenet-D",
            "Speaker D": "en-US-Wavenet-H",
        },
        "es-US": {
            "Speaker A": "es-US-Wavenet-B",
            "Speaker B": "es-US-Wavenet-C",
            "Speaker C": "es-US-Wavenet-A",
            "Speaker D": "es-US-Studio-B",
        },
        "fr-FR": {
            "Speaker A": "fr-FR-Wavenet-B",
            "Speaker B": "fr-FR-Wavenet-D",
            "Speaker C": "fr-FR-Wavenet-A",
            "Speaker D": "fr-FR-Wavenet-C",
        },
        "de-DE": {
            "Speaker A": "de-DE-Wavenet-B",
            "Speaker B": "de-DE-Wavenet-E",
            "Speaker C": "de-DE-Wavenet-F",
            "Speaker D": "de-DE-Wavenet-D",
        },
        "it-IT": {
            "Speaker A": "it-IT-Wavenet-C",
            "Speaker B": "it-IT-Wavenet-D",
            "Speaker C": "it-IT-Wavenet-A",
            "Speaker D": "it-IT-Wavenet-B",
        },
        "ja-JP": {
            "Speaker A": "ja-JP-Wavenet-C",
            "Speaker B": "ja-JP-Wavenet-D",
            "Speaker C": "ja-JP-Wavenet-A",
            "Speaker D": "ja-JP-Wavenet-B",
        },
    }

    return voices


def find_lang(file):
    choices = {
        "_en": "en-US",
        "_es": "es-US",
        "_fr": "fr-FR",
        "_de": "de-DE",
        "_it": "it-IT",
        "_ja": "ja-JP",
    }
    for key, lang in choices.items():
        if key in file:
            return lang
    return None
