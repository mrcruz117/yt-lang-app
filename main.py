from helpers import export_audio, lang_select
from command_funcs.yt import get_yt_data, dl_yt_audio
from command_funcs.transcribe_audio import transcribe_audio
from command_funcs.translate_convert import translate_convert_text
from command_funcs.tts import text_to_speech
from assets.logo import logo
import typer
from db.db_funcs import get_all
from rich.console import Console

console = Console()


app = typer.Typer()


@app.command(help="Download Youtube audio. And save metadata.")
def dl():
    yt, _ = get_yt_data()
    link = yt.watch_url
    dl_yt_audio(link)


@app.command(help="transcribe audio")
def transcribe():
    transcribe_audio()


@app.command(help="Translates text to different languages and CEFR level.")
def translate():
    translate_convert_text()


@app.command(help="Text to speech.")
def tts():
    text_to_speech()


@app.command(help="Export audio to iTunes.")
def export():
    export_audio()


# @app.command(help="dev testing command")
# def test():

#     text_to_speech()


if __name__ == "__main__":
    typer.echo(logo)
    app()
