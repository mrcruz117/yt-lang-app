from pytubefix import YouTube
from pytubefix.cli import on_progress


yt_vid_link = "https://www.youtube.com/watch?v=J7aiEwp1x9k"

yt = YouTube(yt_vid_link, on_progress_callback=on_progress)
print(yt.title)


audio_streams = yt.streams.filter(only_audio=True, file_extension="mp4")

ys = yt.streams.get_audio_only()
ys.download(mp3=True, output_path="downloads")
