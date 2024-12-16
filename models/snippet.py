import uuid
from urllib.parse import urlparse
import os
import requests
import subprocess
from mutagen.mp3 import MP3
from datetime import datetime, timedelta
import httpx
import aiofiles
import asyncio
import tempfile


class Snippet:
    def __init__(self, url):
        """
        Initialize a Snippet instance with the given URL.

        Args:
            url (str): The URL of the audio snippet.
        """
        self.url = url
        self._room = None
        self._uid = None
        self._start_time = None
        self._audio = None
        self._end_time = None
        self.transcription = None

    @property
    def room(self):
        """Extract the room number from the URL."""
        if self._room is None:
            try:
                path = urlparse(self.url).path
                self._room = path.split('/')[2]  # Assuming room is always the third segment
            except IndexError:
                self._room = None
        return self._room

    @property
    def uid(self):
        """Extract the UID from the URL."""
        if self._uid is None:
            try:
                path = urlparse(self.url).path
                # Locate and parse the `uid_s_<number>` segment
                for segment in path.split('__'):
                    if segment.startswith("uid_s"):
                        _uid = segment.split("_")[2]  # Extract the UID
                        break
                return _uid
            except Exception as e:
                print(f"Error extracting UID: {e}")
                return None
        return self._uid

    @property
    def start_time(self):
        """Extract the time from the filename."""
        if self._start_time is None:
            try:
                path = urlparse(self.url).path
                filename = path.split('/')[-1]
                _start_time = filename.split('_')[-1].split('.')[0]
                return _start_time
            except IndexError:
                print("IndexError")
                return None
        return self._start_time

    async def audio(self):
        """
        Asynchronously extracts audio from a given .ts file URL and converts it to .mp3.

        Returns:
            str: Path to the extracted .mp3 file, or None if an error occurs.
        """
        if self._audio is None:
            try:
                # Construct the output file path
                conv_name = f"{self.room}/{self.uid}/{self.start_time}.mp3"
                os.makedirs(os.path.dirname(conv_name), exist_ok=True)
                print(conv_name)

                # Create a unique temporary file for .ts
                temp_filename = f"temp_{uuid.uuid4().hex}.ts"

                # Fetch the file from the URL asynchronously
                async with httpx.AsyncClient() as client:
                    response = await client.get(self.url, timeout=30)
                    if response.status_code != 200:
                        raise Exception(f"Failed to fetch file: {response.status_code}")
                    # Save the file as a unique temporary .ts file asynchronously
                    async with aiofiles.open(temp_filename, "wb") as f:
                        await f.write(response.content)

                # Use FFmpeg to extract audio asynchronously
                ffmpeg_cmd = ["ffmpeg", "-i", temp_filename, "-q:a", "0", "-map", "a", conv_name]
                process = await asyncio.create_subprocess_exec(
                    *ffmpeg_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    raise Exception(f"FFmpeg failed: {stderr.decode()}")

                # Cache the MP3 file path
                self._audio = conv_name
                return self._audio

            except Exception as e:
                print(f"Error processing audio: {e}")
                return None

            finally:
                # Ensure the unique temporary file is deleted
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        return self._audio


    async def end_time(self):
        """
        Calculate the end time by adding the duration of the MP3 file to the start time.

        Returns:
            str: The end time in the same format as the start time, or None if an error occurs.
        """
        if self._end_time is None:
            try:
                # Await the asynchronous audio method
                audio_path = await self.audio()
                if not audio_path or not os.path.exists(audio_path):
                    return None

                # Load the MP3 file to get its duration
                audio = MP3(audio_path)
                duration = int(audio.info.length)  # Duration in seconds

                # Convert the start time to a datetime object
                start_datetime = datetime.strptime(self.start_time, "%Y%m%d%H%M%S%f")

                # Add the duration to the start time
                end_datetime = start_datetime + timedelta(seconds=duration)

                # Cache and return the end time in the same format as the start time
                self._end_time = end_datetime.strftime("%Y%m%d%H%M%S")
                return self._end_time

            except Exception as e:
                print(f"Error calculating end time: {e}")
                return None
        return self._end_time

    def __repr__(self):
        return (f"Snippet(room={self.room}, uid={self.uid}, start_time={self.start_time}, "
                f"end_time={self.end_time}, audio={self.audio}, transcription={self.transcription})")

