import os
from deepgram import DeepgramClient, PrerecordedOptions
from pydub import AudioSegment
from dotenv import load_dotenv
from models import User, Snippet, MasterTranscript
from services import Helper, S3Service
import asyncio
import aiofiles


# Directory of the running script
current_dir = os.path.dirname(__file__)

# Set paths for ffmpeg and ffprobe
AudioSegment.converter = os.getenv("CONVERTER_PATH")
AudioSegment.ffprobe = os.getenv("FFPROBE_PATH")

# Load environment variables
load_dotenv()

# List S3 objects and group .ts files by room
object_keys = S3Service.list_s3_objects(os.getenv("BUCKET_NAME"))
grouped_files_by_room = Helper.group_ts_files_by_room(object_keys)
specific_room_ts = grouped_files_by_room[os.getenv("ARBITRARY_ROOM")]

# Initialize users and queue
users = {"1000005685": User("1000005685"), "1000005686": User("1000005686")}
queue = []

#Creating a queue, last file is oldest
while specific_room_ts:
    file = S3Service.generate_presigned_url(os.getenv("BUCKET_NAME"), specific_room_ts.pop())
    file = Snippet(file)
    queue.append(file)

#Initialize a MasterTranscript
master_transcript = MasterTranscript()

# Initialize Deepgram client
deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))


async def process_snippet(curr_snippet):
    """
    Process a single snippet asynchronously.
    """
    try:
        file_path = os.path.join(current_dir, str(await curr_snippet.audio()))
        # Asynchronously open and read the audio file
        async with aiofiles.open(file_path, 'rb') as buffer_data:
            payload = {'buffer': await buffer_data.read()}  # Read file content asynchronously
            options = PrerecordedOptions(smart_format=True, model="nova-2", language="en-US")

            # Await the asynchronous transcription
            response = await deepgram.listen.asyncrest.v('1').transcribe_file(payload, options)
            pure_transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            curr_snippet.transcription = pure_transcript
            print(pure_transcript)

            # Construct the JSON line and add it to the user's transcript
            json_line = {
                "uid": str(curr_snippet.uid),
                "start_time": str(curr_snippet.start_time),
                "end_time": str(await curr_snippet.end_time()),
                "text": str(curr_snippet.transcription),
            }
            User.add_json_line(users, curr_snippet.uid, json_line, master_transcript)

    except Exception as e:
        print(f"Error processing snippet: {curr_snippet}. Error: {e}")


# manage_snippet_process



async def process_queue(queue):
    """
    Process the entire queue of snippets asynchronously.
    """
    tasks = [process_snippet(snippet) for snippet in queue]
    await asyncio.gather(*tasks)  # Run all snippet processing tasks concurrently


async def main():
    await process_queue(queue)
    # Print user data
    print(users["1000005685"])
    print(users["1000005686"])
    print(master_transcript)

# Execute the main function
if __name__ == "__main__":
    asyncio.run(main())

