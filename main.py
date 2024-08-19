from dotenv import load_dotenv
from helpers import dl_yt_audio, transcribe_or_translate_audio


yt_vid_link = "https://www.youtube.com/watch?v=bWfq8Re30Fg"

vid_uuid, len_in_ms, vid_title = dl_yt_audio(link=yt_vid_link, target_path="downloads")

file_path = "downloads/" + vid_title + ".mp3"

transcribe_or_translate_audio(
    file_path=file_path, len_in_ms=len_in_ms, vid_uuid=vid_uuid
)

# translate to other languages
lang_choices = ["es", "fr", "de", "it", "ja"]

# Display the language choices to the user
print("Please choose a language from the following options:")
for i, lang in enumerate(lang_choices, 1):
    print(f"{i}. {lang}")

# Prompt the user to choose a language
choice = int(input("Enter the number corresponding to your choice: "))

# Validate the user's choice
if 1 <= choice <= len(lang_choices):
    chosen_lang = lang_choices[choice - 1]
    print(f"You have chosen: {chosen_lang}")
else:
    print("Invalid choice. Please run the program again and choose a valid option.")

chosen_lang = lang_choices[choice - 1]

# translate each transcription to the chosen language
