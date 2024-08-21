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


def translate_convert_text(path=None):

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
        system_prompt
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


def split_by_speaker_and_length(path):
    with open(path, "r") as f:
        text = f.read()

    # Split text into complete sentences
    split_by_speaker = text.split("$$")
    console.print("Split by speaker:", split_by_speaker)

    max_length = 4000
    ordered_script = []

    for part in split_by_speaker:
        if not part.strip():
            continue
        console.print("Part:", part)
        speaker, text = part.split(":", 1)
        speaker = speaker.strip()
        console.print(f"{speaker}")
        console.print(f"Text: {text}")

        sentences = re.split(r"[.!?？。！]", text)
        console.print("Sentences:", sentences)

        chunked_text = []
        chunk = ""
        for sentence in sentences:
            if len(chunk) + len(sentence) < max_length:
                chunk += sentence
            else:
                chunk = chunk
                chunked_text.append(chunk + ".")
                console.print("Chunk added:", chunk)
                chunk = sentence
        if chunk.strip():
            chunked_text.append(chunk)
            console.print("Final chunk added:", chunk)

        ordered_script.append([speaker, chunked_text])
        # console.print(f"Ordered script for {speaker}:", chunked_text)
    console.print("FINAL SCRIPT: ",ordered_script)
    return ordered_script
