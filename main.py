from helpers import (
    # dl_yt_audio,
    transcribe_or_translate_audio,
    lang_select,
    generate_corrected_transcript,
    text_to_speech,
    export_audio,
)
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
    generate_corrected_transcript()


# @app.command(help="Download, transcribe, and translate a YouTube video.")
# def dl():
#     vid_uuid, len_in_ms, vid_title = dl_yt_audio(target_path="downloads")
#     lang_selection = lang_select()

#     file_path = "downloads/" + vid_title + ".mp3"

#     transcribe_or_translate_audio(
#         file_path=file_path, len_in_ms=len_in_ms, vid_uuid=vid_uuid, lang=lang_selection
#     )


@app.command(help="Convert a transcript to a different CEFR level.")
def convert():
    path = "transcriptions/jlSsxyWxlaM_es.txt"
    generate_corrected_transcript(path)


@app.command(help="Text to speech.")
def tts():
    text_to_speech()


@app.command(help="Export audio to iTunes.")
def export():
    export_audio()


@app.command(help="dev testing command")
def test():
    # dl_yt_audio()
    # transcribe_audio()
    # translate_convert_text()
    text_to_speech()


if __name__ == "__main__":
    typer.echo(logo)
    app()
