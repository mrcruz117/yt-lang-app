import os
import re
import typer
import questionary
from command_funcs.prompts import system_prompt
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    BarColumn,
)
from rich.console import Console
import openai

console = Console()

progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.percentage:.0f}%"),
    TimeElapsedColumn(),
)
client = openai.Client()


def translate_convert_text(transcript_path=None):

    file_choices = os.listdir("transcriptions")

    if not file_choices:
        typer.echo("No files to convert.")
        return
    else:
        if not transcript_path:
            file = questionary.select(
                "Please choose a file to convert level:", choices=file_choices
            ).ask()
            transcript_path = f"transcriptions/{file}"
    file = None
    if not file:
        file = os.path.basename(transcript_path)

    lang = lang_select()
    file_name = file.split(".")[0]

    level_choices = ["No level change", "A1", "A2", "B1", "B2", "C1", "C2"]
    level_choice = questionary.select(
        "Please choose a level to convert to:", choices=level_choices
    ).ask()
    prompt_addition = f"Translate this to {level_choice} level {lang}."
    if level_choice == "No level change":
        prompt_addition = f"Translate this to {lang}."

    full_prompt = (
        system_prompt
        + f" Try to keep a comparable length to the source. {prompt_addition}"
    )
    text = ""
    with open(transcript_path, "r") as f:
        text = f.read()

    # split text into complete sentences
    processed_script = split_by_speaker_and_length(transcript_path)

    with progress:
        convert_progress = progress.add_task(
            "[blue]Converting text level: ", total=len(processed_script)
        )
        for part in processed_script:
            # progress.update(convert_progress, advance=1, description=f"{speaker}")
            speaker = part[0]

            text = "" + speaker + ": "

            for chunk in part[1]:

                translation = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": full_prompt},
                        {"role": "user", "content": chunk},
                    ],
                    stream=True,
                )

                for response in translation:
                    if response.choices[0].delta.content is not None:
                        text += response.choices[0].delta.content
                        # text += " "
                    else:
                        break
            text += "$$\n"
            path_concat = f"transcriptions/{file_name}_{level_choice}_{lang}.txt"
            if level_choice == "No level change":
                path_concat = f"transcriptions/{file_name}_NA_{lang}.txt"

            with open(path_concat, "a") as f:
                f.write(text)
            progress.update(convert_progress, advance=1)
        progress.stop()
        typer.echo("Conversion complete!")

    return path_concat


def split_by_speaker_and_length(path="", max_length=4000):
    with open(path, "r") as f:
        text = f.read()

    # Split text into complete sentences
    split_by_speaker = text.split("$$")

    ordered_script = []

    for part in split_by_speaker:
        if not part.strip():
            continue
        speaker, text = part.split(":", 1)
        speaker = speaker.strip()

        # sentences = re.split(r"(?<=[.!?？。！])", text)
        sentences = re.split(r'(?<=[.!?？。！]) +', text)
        # console.print(sentences)
        chunked_text = []
        chunk = ""
        for sentence in sentences:
            if len(chunk) + len(sentence) < max_length:
                chunk += sentence
            else:
                chunk = chunk
                chunked_text.append(chunk)
                chunk = sentence
        if chunk.strip():
            chunked_text.append(chunk)

        ordered_script.append([speaker, chunked_text])
        # console.print(f"Ordered script for {speaker}:", chunked_text)
    # console.print("FINAL SCRIPT: ", (ordered_script))
    return ordered_script


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
