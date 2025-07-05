# -- Importing Tools --
from utils.parser import Parser

# -- ToolProcessor Class --
class ToolProcessor:
    def __init__(self, file_manager, shell_executor, ask_user, wiki, image_analyzer, database):
        self.file_manager = file_manager
        self.shell_executor = shell_executor
        self.ask_user = ask_user
        self.wiki = wiki
        self.image_analyzer = image_analyzer
        self.database = database
        self.parser = Parser()

    def process(self, model_response: str) -> str:
        tool_calls = self.parser.extract_tagged_sections(model_response)
        outputs = []
        for i, tool_call in enumerate(tool_calls):
            params = self.parser.parse_tool_call(tool_call)
            if params[0] == "FILE" and self.file_manager is not None:
                try:
                    if params[1] == "read":
                        result = self.file_manager.read(params[2])
                    elif params[1] == "write":
                        result = self.file_manager.write(params[2], params[3])
                    elif params[1] == "append":
                        result = self.file_manager.append(params[2], params[3])
                    elif params[1] == "list":
                        result = self.file_manager.list(params[2])
                    else:
                        result = f"Error: Unknown FILE action '{params[1]}'."
                    outputs.append(f"Tool Output{i if i != 0 else ''}:" + result)
                except Exception as e:
                    outputs.append(f"Error executing FILE tool{i if i != 0 else ''}: {e}")
            elif params[0] == "SHELL" and self.shell_executor is not None:
                try:
                    result = self.shell_executor.execute(params[1])
                    outputs.append(f"Tool Output{i if i != 0 else ''}:" + result)
                except Exception as e:
                    outputs.append(f"Error executing SHELL tool{i if i != 0 else ''}: {e}")
            elif params[0] == "ASK_USER" and self.ask_user is not None:
                try:
                    result = self.ask_user.ask(params[1])
                    outputs.append(f"Tool Output{i if i != 0 else ''}:" + result)
                except Exception as e:
                    outputs.append(f"Error executing ASK_USER tool{i if i != 0 else ''}: {e}")
            elif params[0] == "WIKI" and self.wiki is not None:
                try:
                    result = self.wiki.search(params[1])
                    outputs.append(f"Tool Output{i if i != 0 else ''}:" + result)
                except Exception as e:
                    outputs.append(f"Error executing WIKI tool{i if i != 0 else ''}: {e}")
            elif params[0] == "IMAGE" and self.image_analyzer is not None:
                try:
                    result = self.image_analyzer.analyze(params[2], params[1])
                    outputs.append(f"Tool Output{i if i != 0 else ''}:" + result)
                except Exception as e:
                    outputs.append(f"Error executing IMAGE tool{i if i != 0 else ''}: {e}")
            elif params[0] == "DATA" and self.database is not None:
                try:
                    if params[1] == "read":
                        result = self.database.read(params[2], params[3], params[4])
                    elif params[1] == "write":
                        result = self.database.write(params[2], params[3], params[4], params[5])
                    elif params[1] == "list":
                        result = self.database.list(params[2])
                    else:
                        result = f"Error: Unknown DATA action '{params[1]}'."
                    outputs.append(f"Tool Output{i if i != 0 else ''}:" + result)
                except Exception as e:
                    outputs.append(f"Error executing DATA tool{i if i != 0 else ''}: {e}")
            elif params[0] == "RESULT":
                outputs.append(params[1])
            else:
                outputs.append(f"Error: Unknown tool{i if i != 0 else ''} call.")
        if len(tool_calls) == 1:
            if self.parser.parse_tool_call(tool_calls[0])[0] == "RESULT":
                return "FINISHED", "".join(outputs)
        return "CONTINUE", "".join(str(output) for output in outputs if output)