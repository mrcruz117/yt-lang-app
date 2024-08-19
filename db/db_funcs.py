import json
import os

script_dir = os.path.dirname(__file__)

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