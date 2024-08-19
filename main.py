from pytubefix import YouTube
from pytubefix.cli import on_progress
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import time
from helpers import dl_yt_audio

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


yt_vid_link = "https://www.youtube.com/watch?v=bWfq8Re30Fg"

vid_uuid, len_in_ms, vid_title = dl_yt_audio(link=yt_vid_link, target_path="downloads")

file_path = "downloads/" + vid_title + ".mp3"

audio_segment = AudioSegment.from_file(file_path, "mp4")

chunk_length_ms = 1000 * 60 * 20  # 20 min

# clear folder contents before processing
os.system("rm -rf chunks/*")
os.system("rm -rf transcriptions/*")

total_chunks = len_in_ms // chunk_length_ms + 1

start_time = time.time()

for i in range(0, len_in_ms, chunk_length_ms):
    print(f"Processing chunk {i} to {i + chunk_length_ms}")
    chunk = audio_segment[i : i + chunk_length_ms]
    chunk.export(f"chunks/chunk_{i}.mp3", format="mp3")

    # get transcription
    print("Transcribing chunk...")
    print("Translating chunk...")
    audio_file = open(f"chunks/chunk_{i}.mp3", "rb")
    # This worked! :)
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="fr",
    )

    end_time = time.time()

    print(f"Translation took {end_time - start_time:.2f} seconds")

    # write to file in /transcriptions
    with open("transcriptions/transcription_" + vid_uuid + ".txt", "a") as f:
        f.write(transcription.text)
    current_chunk = i // chunk_length_ms + 1
    percentage_completion = (current_chunk / total_chunks) * 100
    print(f"Completed {percentage_completion:.2f}%")

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
