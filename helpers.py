from pytubefix import YouTube
from pytubefix.cli import on_progress


def dl_yt_audio(link, target_path):
    """
    Downloads the audio from a YouTube video and saves it to the target path.

    returns the video's yt UUID. Use for caching purposes.

    and returns the length of the video in milliseconds. for chunking
    """

    yt = YouTube(link, on_progress_callback=on_progress)

    # for caching purposes later
    vid_uuid = yt.video_id

    print(yt.title)

    audio_streams = yt.streams.filter(only_audio=True)
    len_in_sec = yt.length
    len_in_ms = len_in_sec * 1000

    ys = yt.streams.get_audio_only()

    ys.download(mp3=True, output_path=target_path)

    return vid_uuid, len_in_ms, yt.title
