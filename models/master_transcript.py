import bisect

class MasterTranscript:
    def __init__(self):
        self.master_transcript = []

    def add_json_line_to_master(self, json_obj):
        """
        Adds a JSON line to the master_transcript in a sorted manner.

        Args:
            json_obj (dict): JSON object to add to the master_transcript.
        """
        # Use binary search to find the correct position to insert
        key = int(json_obj["start_time"])
        position = bisect.bisect_left([int(item["start_time"]) for item in self.master_transcript], key)

        # Insert the new object at the correct position
        self.master_transcript.insert(position, json_obj)

        print(f"Added to master transcript: {json_obj}")

    def __repr__(self):
        """
        String representation of the User class showing the master transcript.
        """
        return f"{self.master_transcript}"

