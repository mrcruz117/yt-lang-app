import questionary
from db.db_funcs import add_media_info, get_media_ids, get_media_info
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix import YouTube
from pytubefix.cli import on_progress
import typer
from rich.console import Console

console = Console()


def get_yt_data(link=None):
    if not link:
        link = questionary.text("Enter the YouTube link:").ask()

    yt = YouTube(link, on_progress_callback=on_progress)

    # for caching purposes later
    vid_uuid = yt.video_id
    len_in_sec = yt.length
    len_in_ms = len_in_sec * 1000

    exists = get_media_info(vid_uuid)
    if not exists:
        add_media_info(yt)

    return yt, {"vid_uuid": vid_uuid, "len_in_ms": len_in_ms, "title": yt.title}


def dl_yt_audio(link=None):

    if not link:
        saved_ids = get_media_ids()
        links = {get_media_info(id)["title"]: id for id in saved_ids}
        titles = list(links.keys())
        chosen_vid = questionary.select(
            "Select a video to download:", choices=titles
        ).ask()

        link = f"https://www.youtube.com/watch?v={links[chosen_vid]}"

    yt, metadata = get_yt_data(link)
    ys = yt.streams.get_audio_only()

    target_path = "downloads"
    ys.download(mp3=True, output_path=target_path)
    console.print("Audio downloaded.")
    return metadata["vid_uuid"], metadata["len_in_ms"], metadata["title"]
