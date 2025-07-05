import os, json

# -- Configuration --
AGENT_BASE_DIR = json.load(open("config.json", "r"))["AGENT_BASE_DIR"]

# -- File Editor Prompt --
FILE_EDITOR_PROMPT = """
**File Editor**: Read, write, append, and list files from your workspace.
    * **Read**: `<<<FILE:'read'<nex!-pr-amtre?gr+>'path/to/file.txt'>>>`
    * **Write**: `<<<FILE:'write'<nex!-pr-amtre?gr+>'path/to/file.txt'<nex!-pr-amtre?gr+>'content_to_write'>>>` (overwrites file)
    * **Append**: `<<<FILE:'append'<nex!-pr-amtre?gr+>'path/to/file.txt'<nex!-pr-amtre?gr+>'content_to_append'>>>`
    * **List**: `<<<FILE:'list'<nex!-pr-amtre?gr+>'path/to/directory'<nex!-pr-amtre?gr+>'mode'<nex!-pr-amtre?gr+>'contents'>>>` (use `'.'` for the current directory. example: `<<<FILE:'list'<nex!-pr-amtre?gr+>'.'>>>`). modes: `ls`(d, lists only the path), `lsc'(lists the path recursively). contents is a list with 4 params; the first is if the size of files/dictories should be shown, the second is if the type(file/directory) should be shown, the third is if the content should be shown, and the fourth is the maxlength of the content(in charakters).
    * **Example**: `<<<FILE:'read'<nex!-pr-amtre?gr+>'data.txt'>>>`, `<<<FILE:'write'<nex!-pr-amtre?gr+>'data.txt'<nex!-pr-amtre?gr+>'Hello World!'>>>`, `<<<FILE:'list'<nex!-pr-amtre?gr+>'.'<nex!-pr-amtre?gr+>'ls'<nex!-pr-amtre?gr+>'[True, False, True, 100]'>>>`.
    * **IMPORTANT**: Never use a backslash for a quote or before a quote if not needed for something special.
    * **Info**: if you want to write a literal backslash (`\`) to a file(so that the backslash is like any other character), use <bs> instead. Don't use this for newlines. NEVER!! Use `\n` for newlines. This counts for every newsline in every file_format.
"""

# -- File Editor Class --
class FileEditor:
    # Helper Function
    def _get_agent_path(self, file_path: str=".") -> str:
        # Prevent directory traversal attacks
        sanitized_path = os.path.normpath(file_path).lstrip('./\\')
        return os.path.join(AGENT_BASE_DIR, sanitized_path)

    # Read Tool
    def read(self, file_path: str=".") -> str:
        try:
            full_path = self._get_agent_path(file_path)
            with open(full_path, 'r', encoding='utf-8') as file:
                return f"Content of file at {file_path} is:\n{file.read()}"

        except FileNotFoundError:
            return f"Error: File not found at '{file_path}'."

        except Exception as e:
            return f"Error reading file '{file_path}': {e}"

    # Write Tool
    def write(self, file_path: str=".", content: str="") -> str:
        try:
            content = content.replace("\\'", "'")
            content = content.replace('\\"', '"')
            content = content.replace("\\n", "\n")
            content = content.replace("\\t", "\t")
            content = content.replace("<bs>", "\\")
            full_path = self._get_agent_path(file_path)
            os.makedirs(os.path.dirname(full_path) or AGENT_BASE_DIR, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return f"Successfully wrote to '{file_path}'."

        except Exception as e:
            return f"Error writing to file '{file_path}': {e}"

    # Append Tool
    def append(self, file_path: str=".", content: str="") -> str:
        try:
            content = content.replace("\'", "'")
            content = content.replace('\"', '"')
            content = content.replace("\\n", "\n")
            content = content.replace("\\t", "\t")
            content = content.replace("<bs>", "\\")
            full_path = self._get_agent_path(file_path)
            with open(full_path, 'a', encoding='utf-8') as file:
                file.write(content)
            return f"Successfully appended to '{file_path}'."

        except Exception as e:
            return f"Error appending to file '{file_path}': {e}"

    # List Tool
    def list(self, path: str=".", mode: str="ls", contents: list=[False, False, False, 0]) -> str:
        include_size = contents[0]
        include_type = contents[1]
        include_content = contents[2]
        max_content_len = contents[3] if contents[3] > 0 else float('inf')

        top_level_data = {
            "listed_path": path,
            "size": 0,
            "content": {}
        }
        
        try:
            full_dir_path = self._get_agent_path(path)

            if not os.path.isdir(full_dir_path):
                return json.dumps({"error": f"Directory not found or is not a directory at '{path}'."}, indent=4)

            def _process_directory(current_abs_path, is_root=False):
                current_dir_size = 0
                current_dir_content = {}

                entries = os.listdir(current_abs_path)

                entries.sort()

                for entry_name in entries:
                    entry_abs_path = os.path.join(current_abs_path, entry_name)
                    entry_details = {}

                    if os.path.isfile(entry_abs_path):
                        file_size = os.path.getsize(entry_abs_path)
                        current_dir_size += file_size
                        
                        if include_type:
                            entry_details["type"] = "file"
                        if include_size:
                            entry_details["size"] = file_size
                        if include_content:
                            try:
                                with open(entry_abs_path, 'r', encoding='utf-8') as file:
                                    file_content = file.read()
                                    if len(file_content) > max_content_len:
                                        entry_details["content"] = file_content[:int(max_content_len)] + "..."
                                    else:
                                        entry_details["content"] = file_content
                            except Exception:
                                entry_details["content"] = "Non readable content"
                        current_dir_content[entry_name] = entry_details

                    elif os.path.isdir(entry_abs_path):
                        if mode == "lsc" or (mode == "ls" and is_root):
                            subdir_result, subdir_size = _process_directory(entry_abs_path)
                            current_dir_size += subdir_size
                            
                            subdir_details = {}
                            if include_type:
                                subdir_details["type"] = "directory"
                            if include_size:
                                subdir_details["size"] = subdir_size
                            subdir_details["content"] = subdir_result
                            current_dir_content[entry_name] = subdir_details
                        elif mode == "ls" and not is_root:
                            entry_details = {}
                            if include_type:
                                entry_details["type"] = "directory"
                            current_dir_content[entry_name] = entry_details
                            
                return current_dir_content, current_dir_size

            if mode == "ls":
                def _build_dir_structure(current_abs_path, is_recursive_mode):
                    current_struct_content = {}
                    current_struct_size = 0

                    try:
                        entries = os.listdir(current_abs_path)
                        entries.sort()
                    except OSError:
                        return {"error": "Cannot list directory"}, 0

                    for entry_name in entries:
                        entry_abs_path = os.path.join(current_abs_path, entry_name)
                        entry_details = {}

                        if os.path.isfile(entry_abs_path):
                            file_size = os.path.getsize(entry_abs_path)
                            current_struct_size += file_size
                            
                            if include_type:
                                entry_details["type"] = "file"
                            if include_size:
                                entry_details["size"] = file_size
                            if include_content:
                                try:
                                    with open(entry_abs_path, 'r', encoding='utf-8') as file:
                                        file_content = file.read()
                                        if len(file_content) > max_content_len:
                                            entry_details["content"] = file_content[:int(max_content_len)] + "..."
                                        else:
                                            entry_details["content"] = file_content
                                except Exception:
                                    entry_details["content"] = "Non readable content"
                            current_struct_content[entry_name] = entry_details

                        elif os.path.isdir(entry_abs_path):
                            subdir_content, subdir_size = {}, 0
                            if is_recursive_mode:
                                subdir_content, subdir_size = _build_dir_structure(entry_abs_path, True)
                            elif mode == "ls" and include_content:
                                temp_content, temp_size = _build_dir_structure(entry_abs_path, False)
                                subdir_content = temp_content

                                total_subdir_size = 0
                                for _r, _d, _f in os.walk(entry_abs_path):
                                    for _file in _f:
                                        total_subdir_size += os.path.getsize(os.path.join(_r, _file))
                                subdir_size = total_subdir_size

                            current_struct_size += subdir_size

                            dir_details = {}
                            if include_type:
                                dir_details["type"] = "directory"
                            if include_size:
                                dir_details["size"] = subdir_size
                            if include_content:
                                dir_details["content"] = subdir_content
                            
                            current_struct_content[entry_name] = dir_details
                    
                    return current_struct_content, current_struct_size

                if mode == "lsc":
                    processed_content, total_size = _build_dir_structure(full_dir_path, True)
                elif mode == "ls":
                    processed_content, total_size = _build_dir_structure(full_dir_path, False)
                    total_size = 0
                    for _r, _d, _f in os.walk(full_dir_path):
                        for _file in _f:
                            total_size += os.path.getsize(os.path.join(_r, _file))

                else:
                    return json.dumps({"error": "Invalid mode. Use 'ls' or 'lsc'."}, indent=4)

                top_level_data["size"] = total_size
                top_level_data["content"] = processed_content
                
                if not include_size:
                    del top_level_data["size"]
                    def _remove_key_recursive(d, key_to_remove):
                        if isinstance(d, dict):
                            d.pop(key_to_remove, None)
                            for k, v in d.items():
                                if k == "content" and isinstance(v, dict):
                                    _remove_key_recursive(v, key_to_remove)
                                elif isinstance(v, dict):
                                    _remove_key_recursive(v, key_to_remove)
                    
                    _remove_key_recursive(top_level_data["content"], "size")
                    
                if not include_type:
                    def _remove_key_recursive_type(d, key_to_remove):
                        if isinstance(d, dict):
                            d.pop(key_to_remove, None)
                            for k, v in d.items():
                                if k == "content" and isinstance(v, dict):
                                    _remove_key_recursive_type(v, key_to_remove)
                                elif isinstance(v, dict):
                                    _remove_key_recursive_type(v, key_to_remove)
                    
                    _remove_key_recursive_type(top_level_data["content"], "type")
                
                if not include_content:
                    def _remove_key_recursive_content(d, key_to_remove):
                        if isinstance(d, dict):
                            d.pop(key_to_remove, None)
                            for k, v in d.items():
                                if k == "content" and isinstance(v, dict):
                                    _remove_key_recursive_content(v, key_to_remove)
                                elif isinstance(v, dict):
                                    _remove_key_recursive_content(v, key_to_remove)
                    
                    _remove_key_recursive_content(top_level_data["content"], "content")


                if not top_level_data["content"] and include_content:
                    top_level_data["content"] = "Directory is empty."
                elif not top_level_data["content"]:
                     top_level_data["content"] = {}
            
                return json.dumps(top_level_data, indent=4)

        except FileNotFoundError:
            return json.dumps({"error": f"Directory not found at '{path}'."}, indent=4)
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred while listing '{path}': {e}"}, indent=4)