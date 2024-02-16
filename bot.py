import os
import random
import re
import uuid

import requests
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ContentType, Message, ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
SPEAKER_ID = os.getenv("SPEAKER_ID")
AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")
MESSAGE_LIMIT = 1000  # Message length limit
WORDS_FILE_PATH = "ky_words_mini_compact_no_repeat.txt"  # Path to the file containing words

dp = Dispatcher(Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML))

# Add start command description
dp.bot.set_my_commands([BotCommand(command="start", description="Starts the text-to-speech bot"),
                        BotCommand(command="words", description="Send 5 random words with their sounds")])

@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    await message.answer(" Hi! Send me a text message containing only Cyrillic letters, and I'll convert it to an audio file using the API you provided.")

@dp.message_handler(commands=["words"])
async def words_handler(message: Message):
    # Read words from the file
    with open(WORDS_FILE_PATH, "r", encoding="utf-8") as file:
        words = file.readlines()

    # Select 5 random words
    random_words = random.sample(words, 5)

    for word in random_words:
        # Remove newline character
        word = word.strip()

        # Construct API request payload
        payload = {
            "text": word,
            "speaker_id": SPEAKER_ID
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

                # Send the audio file to the user
                await message.answer(f"Word: {word}")
                await message.answer_audio(audio=open(filename, 'rb'))

                # Delete the saved audio file to avoid clutter
                os.remove(filename)
            else:
                await message.answer("Unexpected response format: audio data not found")

        except (ValueError, requests.RequestException) as e:
            await message.answer(f"Sorry, an error occurred: {e}")

@dp.message_handler(content_types=ContentType.TEXT)
async def text_handler(message: Message):
    user_text = message.text

    # Check if the length of the message exceeds the limit
    if len(user_text) > MESSAGE_LIMIT:
        await message.answer(f"Sorry, the message length should not exceed {MESSAGE_LIMIT} characters.")
        return

    # Remove punctuation from the message
    user_text = re.sub(r'[^\w\sа-яА-ЯёЁ]', '', user_text)

    # Check if the message contains only Cyrillic letters
    if not re.match(r'^[а-яА-ЯёЁ\s]+$', user_text):
        await message.answer("Sorry, please only use Cyrillic letters.")
        return

    # Construct API request payload
    payload = {
        "text": user_text,
        "speaker_id": SPEAKER_ID
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

            # Send the audio file to the user
            await message.answer_audio(audio=open(filename, 'rb'))

            # Delete the saved audio file to avoid clutter
            os.remove(filename)
        else:
            await message.answer("Unexpected response format: audio data not found")

    except (ValueError, requests.RequestException) as e:
        await message.answer(f"Sorry, an error occurred: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
