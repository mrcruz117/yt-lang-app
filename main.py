from helpers import (
    dl_yt_audio,
    transcribe_or_translate_audio,
    lang_select,
    generate_corrected_transcript,
    text_to_speech,
    export_audio,
)
from command_funcs.transcribe_audio import transcribe_audio
from assets.logo import logo
import typer
from db.db_funcs import get_all


app = typer.Typer()


@app.command(help="Download, transcribe, and translate a YouTube video.")
def dl_and_tr():
    vid_uuid, len_in_ms, vid_title = dl_yt_audio(target_path="downloads")
    lang_selection = lang_select()

    file_path = "downloads/" + vid_title + ".mp3"

    transcribe_or_translate_audio(
        file_path=file_path, len_in_ms=len_in_ms, vid_uuid=vid_uuid, lang=lang_selection
    )


@app.command()
def test():
    vid_uuid, len_in_ms, vid_title = dl_yt_audio(target_path="downloads")
    # lang_selection = lang_select()
    transcribe_audio( len_in_ms=len_in_ms, vid_uuid=vid_uuid, lang="")


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


if __name__ == "__main__":
    typer.echo(logo)
    app()
