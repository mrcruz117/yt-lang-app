from helpers import (
    dl_yt_audio,
    transcribe_or_translate_audio,
    lang_select,
    generate_corrected_transcript,
    text_to_speech,
    export_audio,
)
from assets.logo import logo
import typer
from db.db_funcs import get_all


app = typer.Typer()


@app.command()
def main():
    vid_uuid, len_in_ms, vid_title = dl_yt_audio(target_path="downloads")
    lang_selection = lang_select()

    file_path = "downloads/" + vid_title + ".mp3"

    transcribe_or_translate_audio(
        file_path=file_path, len_in_ms=len_in_ms, vid_uuid=vid_uuid, lang=lang_selection
    )


@app.command()
def test():
    # db = get_all()
    # print(db)
    test_link = "https://www.youtube.com/watch?v=jlSsxyWxlaM"
    vid_uuid, len_in_ms, vid_title = dl_yt_audio(
        link=test_link, target_path="downloads"
    )
    lang_selection = lang_select()

    file_path = "downloads/" + vid_title + ".mp3"

    transcribe_or_translate_audio(
        file_path=file_path, len_in_ms=len_in_ms, vid_uuid=vid_uuid, lang=lang_selection
    )


@app.command()
def convert():
    path = "transcriptions/jlSsxyWxlaM_es.txt"
    generate_corrected_transcript(path)


@app.command()
def tts():
    text_to_speech()


@app.command()
def export():
    export_audio()


if __name__ == "__main__":
    typer.echo(logo)
    app()
