from command_funcs.yt import get_yt_data, dl_yt_audio
from command_funcs.transcribe_audio import transcribe_audio
from command_funcs.translate_convert import translate_convert_text
from command_funcs.tts import list_languages, google_tts  # , text_to_speech
from command_funcs.export import export_audio
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
    google_tts()


@app.command(help="Export audio to iTunes.")
def export():
    export_audio()


@app.command(
    help="Complete process of downloading audio, transcribing, translating, and exporting for a link"
)
def process():
    yt, _ = get_yt_data()
    link = yt.watch_url
    audio_path = dl_yt_audio(link)
    transcript_path = transcribe_audio(audio_path=audio_path)
    converted_path = translate_convert_text(transcript_path=transcript_path)
    google_tts(path=converted_path)
    # export_audio()


@app.command(help="dev testing command")
def test():
    # list_languages()
    google_tts()


if __name__ == "__main__":
    typer.echo(logo)
    app()
