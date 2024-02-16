import os
import random
import uuid

import requests
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Message, ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")
WORDS_FILE = "ky_words_mini_compact_no_repeat.txt"
WORDS_COUNT = 5  # Number of words to send to the user

dp = Dispatcher(Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML))

# Add words command description
dp.bot.set_my_commands([BotCommand(command="words", description="Send 5 random words with their sounds")])

def get_random_words():
    # Read words from the file
    with open(WORDS_FILE, "r", encoding="utf-8") as file:
        words = file.readlines()
    
    # Select 5 random words
    random_words = random.sample(words, WORDS_COUNT)
    return random_words

async def send_word_and_sound(message):
    random_words = get_random_words()

    for word in random_words:
        word = word.strip()  # Remove leading/trailing whitespace
        
        # Construct API request payload
        payload = {
            "text": word,
            "speaker_id": "1"  # Assuming speaker ID is fixed
        }

        # Set headers with authorization token
        headers = {
            'Authorization': AUTHORIZATION_TOKEN
        }

        try:
            # Send POST request to API
            response = requests.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()  # Raise exception for non-200 status codes

            # Check if the response contains audio data
            if response.headers.get('content-type') == 'audio/mpeg':
                audio_data = response.content

                # Create a unique filename using UUID
                filename = f"audio_{str(uuid.uuid4())}.mp3"

                # Create or overwrite the audio file (avoiding potential write errors)
                with open(filename, 'wb') as f:
                    f.write(audio_data)

                # Send the word and the corresponding audio file to the user
                await message.answer(f"Word: {word}")
                await message.answer_audio(audio=open(filename, 'rb'))

                # Delete the saved audio file to avoid clutter
                os.remove(filename)
            else:
                await message.answer(f"Unexpected response format for word '{word}': audio data not found")

        except (ValueError, requests.RequestException) as e:
            await message.answer(f"Sorry, an error occurred for word '{word}': {e}")

@dp.message_handler(commands=["words"])
async def words_handler(message: Message):
    await send_word_and_sound(message)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
