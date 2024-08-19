from helpers import dl_yt_audio, transcribe_or_translate_audio, lang_select
from assets.logo import logo
import typer


app = typer.Typer()


@app.command()
def main():
    vid_uuid, len_in_ms, vid_title = dl_yt_audio(target_path="downloads")
    lang_selection = lang_select()

    file_path = "downloads/" + vid_title + ".mp3"

    transcribe_or_translate_audio(
        file_path=file_path, len_in_ms=len_in_ms, vid_uuid=vid_uuid, lang=lang_selection
    )


# @app.command()
# def set_config():
#     typer.echo("config")


if __name__ == "__main__":
    typer.echo(logo)
    app()
