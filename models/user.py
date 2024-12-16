import json

class User:
    def __init__(self, uid):
        """
        Initialize a User instance with an empty master transcript.

        Args:
            uid (str): User id.
        """
        self.uid = uid
        self.master_transcript = []  # This will store the line-separated JSON as a list of JSON strings

    @staticmethod
    def add_json_line(users, uid, json_obj):
        """
        Adds a JSON line to the specified user's master transcript by UID in a sorted manner.

        Args:
            users (dict): Dictionary of User instances keyed by UID.
            uid (str): Unique identifier for the user.
            json_obj (dict): JSON object to add to the user's transcript.

        Raises:
            ValueError: If the UID is not found or the JSON object is invalid.
        """
        if uid not in users:
            raise ValueError(f"User with UID '{uid}' not found.")

        user = users[uid]

        # Add the new JSON object
        user.master_transcript.append(json_obj)

        # Ensure the master_transcript is sorted by start_time and end_time
        user.master_transcript.sort(
            key=lambda x: (int(x["start_time"]), int(x["end_time"]))
        )

        print(f"Added to user {uid}: {json_obj}")


    def __repr__(self):
        """
        String representation of the User class showing the master transcript.
        """
        return f"uid(name={self.uid}, master_transcript=\n{self.master_transcript})"