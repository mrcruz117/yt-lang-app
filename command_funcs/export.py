import os
import shutil
import typer
import questionary
from rich.console import Console
from mutagen.easyid3 import EasyID3
from pathlib import Path

console = Console()


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
