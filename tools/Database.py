# -- Importing Packages --
import json, os

# -- Database Prompt --
DATABASE_PROMPT = """
**Database**: Use this tool to store and retrieve information.
    * **Write**: `<<<DATA:'write'<nex!-pr-amtre?gr+>'content_to_store'<nex!-pr-amtre?gr+>'path_with_name'>>>`
        * **'content_to_store'**: The data (as a string) to be stored.
        * **'path_with_name'**: The full path to where the content should be saved, including the final data name. If the path or name already exists, an error will be returned.
        * **Example**: `<<<DATA:'write'<nex!-pr-amtre?gr+>'my_secret_key'<nex!-pr-amtre?gr+>'settings/api/key'>>>`
    * **Read**: `<<<DATA:'read'<nex!-pr-amtre?gr+>'path_to_data'>>>`
        * **'path_to_data'**: The full path to the data, including its name. If the path does not exist, an error will be returned.
        * **Example**: `<<<DATA:'read'<nex!-pr-amtre?gr+>'settings/api/key'>>>`
    * **List**: `<<<DATA:'list'<nex!-pr-amtre?gr+>'path_to_container'>>>`
        * **'path_to_container'**: The path to a directory/container whose contents you want to list (e.g., "settings/api"). If the path points directly to content (not a container) or does not exist, an error will be returned. Use `''` (empty string) to list the root level.
        * **Example**: `<<<DATA:'list'<nex!-pr-amtre?gr+>'settings/api'>>>`
    * **INFO**: This tool is crucial for your operation and learning. It should be used for:
        * **Logging**: Storing various types of logs, including system events, operational details, and especially **errors** for later retrieval and analysis. This helps in debugging and understanding past issues.
        * **Memory/User Context**: Remembering specific details for the user, such as preferences or previous conversation points.
        * **Storage**: Crucially, **every user question and your corresponding short answer** should be stored here.
        * This tool can be used in combination with other tools.
    * **PATHS**: "context/{topic}": Use this for 
"""

# -- Database Class --

class Database:
    def __init__(self):
        try:
            self.path = json.load(open("config.json", "r"))["DATABASE_PATH"]
        except FileNotFoundError:
            raise ValueError("config.json not found.")
        except json.JSONDecodeError:
            raise ValueError("Error decoding config.json.")

        try:
            with open(self.path, "r") as f:
                json.load(f)
        except json.JSONDecodeError:
            raise ValueError("The database file is not valid JSON.")

    def _load_data(self):
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_data(self, data):
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    def write(self, content: str, path: str):
        db = self._load_data()
        path_parts = path.split('/')
        current_level = db

        for i, part in enumerate(path_parts):
            if i == len(path_parts) - 1: # Last part is the data name
                if part in current_level:
                    return "Error: Path already exists. Cannot overwrite."
                current_level[part] = content
            else:
                if part not in current_level:
                    current_level[part] = {}
                elif not isinstance(current_level[part], dict):
                    return "Error: Path conflicts with existing content. Cannot create nested structure."
                current_level = current_level[part]
        self._save_data(db)
        return "Data successfully written."

    def read(self, path: str):
        db = self._load_data()
        path_parts = path.split('/')
        current_level = db

        for i, part in enumerate(path_parts):
            if part not in current_level:
                return "Error: Path not found."
            if i == len(path_parts) - 1: # Last part
                return current_level[part]
            
            if not isinstance(current_level[part], dict):
                return "Error: Path points to content, not a container." # If an intermediate part is not a dict
            current_level = current_level[part]
        return "Error: Path not found." # Should not be reached if path is valid

    def list(self, path: str):
        db = self._load_data()
        path_parts = path.split('/')
        current_level = db

        for i, part in enumerate(path_parts):
            if part not in current_level:
                return "Error: Path not found."
            
            if i == len(path_parts) - 1: # Last part
                if isinstance(current_level[part], dict):
                    return list(current_level[part].keys())
                else:
                    return "Error: Path points directly to content, not a listable container."
            
            if not isinstance(current_level[part], dict):
                return "Error: Intermediate path element is not a dictionary."
            current_level = current_level[part]
        
        # If the path is empty or leads to the root
        if not path_parts or path == "":
             return list(db.keys())

        return "Error: Path not found or unexpected structure." # Fallback for unhandled cases