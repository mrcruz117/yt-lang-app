from helpers import dl_yt_audio, transcribe_or_translate_audio, lang_select


yt_vid_link = "https://www.youtube.com/watch?v=bWfq8Re30Fg"

vid_uuid, len_in_ms, vid_title = dl_yt_audio(link=yt_vid_link, target_path="downloads")

file_path = "downloads/" + vid_title + ".mp3"


chosen_lang = lang_select()
print(chosen_lang)

transcribe_or_translate_audio(
    file_path=file_path, len_in_ms=len_in_ms, vid_uuid=vid_uuid, lang="fr"
)

# translate to other languages

# Display the language choices to the user


# translate each transcription to the chosen language
