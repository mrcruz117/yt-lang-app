import json
import os
from rich.console import Console

script_dir = os.path.dirname(__file__)
console = Console()

db_path = os.path.join(script_dir, "database.json")
# {'users': {}, 'mediaInfo': {}, 'transcriptionsPaths': {}}


def get_all():
    with open(db_path, "r") as f:
        data = json.load(f)

    return data


def add_media_info(yt):
    with open(db_path, "r") as f:
        data = json.load(f)

    data["mediaInfo"][yt.video_id] = {
        "id": yt.video_id,
        "title": yt.title,
        "length": yt.length,
    }

    with open(db_path, "w") as f:
        json.dump(data, f, indent=4)
    console.print("Media info added to database.")


def get_media_ids():
    with open(db_path, "r") as f:
        data = json.load(f)

    return data["mediaInfo"].keys()


def get_media_info(vid_uuid):
    with open(db_path, "r") as f:
        data = json.load(f)

    return data["mediaInfo"][vid_uuid]


def add_transcription_path(lang, vid_uuid, path):
    with open(db_path, "r") as f:
        data = json.load(f)

    id = f"{vid_uuid}_{lang}"

    data["transcriptionsPaths"][id] = path

    with open(db_path, "w") as f:
        json.dump(data, f, indent=4)


def transcript_exists(lang, vid_uuid):
    with open(db_path, "r") as f:
        data = json.load(f)

    id = f"{vid_uuid}_{lang}"

    return id in data["transcriptionsPaths"]


def get_title_id_dict():
    with open(db_path, "r") as f:
        data = json.load(f)

    return {info["title"]: id for id, info in data["mediaInfo"].items()}
