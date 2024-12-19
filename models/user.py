import json
import bisect
from models import master_transcript

class User:
    def __init__(self, uid):
        """
        Initialize a User instance with an empty master transcript.

        Args:
            uid (str): User id.
        """
        self.uid = uid
        self.user_transcript = []  # This will store the line-separated JSON as a list of JSON strings

    @staticmethod
    def add_json_line(users, uid, json_obj, master_transcript):
        """
        Adds a JSON line to the specified user's transcript by UID in a sorted manner.
        Also adds the JSON line into the master_transcript.

        Args:
            users (dict): Dictionary of User instances keyed by UID.
            uid (str): Unique identifier for the user.
            json_obj (dict): JSON object to add to the user's transcript.
            master_transcript (MasterTranscript): A list of all merged transcripts.

        Raises:
            ValueError: If the UID is not found or the JSON object is invalid.
        """
        if uid not in users:
            raise ValueError(f"User with UID '{uid}' not found.")

        user = users[uid]

        # Use binary search to find the correct position to insert
        key = int(json_obj["start_time"])
        position = bisect.bisect_left([int(item["start_time"]) for item in user.user_transcript], key)

        # Insert the new object at the correct position
        user.user_transcript.insert(position, json_obj)

        # Add the new JSON object to the master transcript
        master_transcript.add_json_line_to_master(json_obj)

        print(f"Added to user {uid}: {json_obj}")


    def __repr__(self):
        """
        String representation of the User class showing the master transcript.
        """
        return f"uid(name={self.uid}, user_transcript=\n{self.user_transcript})"


