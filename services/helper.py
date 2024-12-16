import re

class Helper:
    @staticmethod
    def group_ts_files_by_room(object_keys):
        """
        Groups .ts files by room number.

        :param object_keys: List of S3 object keys (file paths).
        :return: Dictionary with room numbers as keys and lists of .ts files as values.
        """
        room_ts_dict = {}

        try:
            for key in object_keys:
                # Check if the key represents a .ts file
                if key.endswith('.ts'):
                    # Extract the room number using regex (assuming the room number format)
                    match = re.search(r'room/(\d+)', key)  # Adjust regex to match your naming convention
                    if match:
                        room_number = match.group(1)
                        if room_number not in room_ts_dict:
                            room_ts_dict[room_number] = []
                        room_ts_dict[room_number].append(key)
        except TypeError as e:
            print(f"Error: Invalid object_keys input. Expected a list of strings. {e}")
            raise ValueError("object_keys must be a list of strings.") from e
        except Exception as e:
            print(f"Unexpected error while grouping .ts files by room: {e}")
            raise

        return room_ts_dict
