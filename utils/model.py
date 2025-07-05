import json, time, ollama, base64, os, google.generativeai as genai
from collections import deque
from PIL import Image

# -- Configuration --
MODELS = json.load(open("config.json", "r"))["MODELS"]
LLM_MODEL = json.load(open("config.json", "r"))["MODEL_CONFIG"]["LLM_MODEL"]
WIKI_MODEL = json.load(open("config.json", "r"))["MODEL_CONFIG"]["WIKI_MODEL"]

# -- Init Prompt --
INIT_PROMPT = """
You are an AI-Assistant designed to solve complex problems by executing a plan step-by-step.
Your available tools to achieve the goal are:
{file_editor_prompt}
{shell_executor_prompt}
{ask_user_prompt}
{wiki_prompt}
{image_analyzer_prompt}
{database_prompt}
**RESULT**: Use this tool ONLY when the task is completely finished or you dont know what to do next.
    * **Usage**: `<<<RESULT:'Your final, detailed answer and explanation.'>>>`
    * **Example**: `<<<RESULT:'I finished your task. Look in the file "result.txt" for more details'>>>`. Don't add extra quotes.
    * **Important**: You can't use this tool in combination with any other tool.
{only_one_tool_prompt}

**Instructions for using tools:**
1.  **Plan First**: Before starting, think about a plan to solve the task.
2.  **One Tool At A Time**: As a general rule, use one tool per response to ensure you can process the output correctly. For simple, related tasks (like creating a directory then a file inside it), you may use multiple tools.
3.  **Verify Your Work**: Always test your code or commands. Before testing, double-check your code for errors to save time.
4.  **Tool Format**: You must use tools by outputting the exact format: `<<<TOOL_NAME:'argument1'<nex!-pr-amtre?gr+>'argument2'<nex!-pr-amtre?gr+>...>>>`.
5.  **CRUCIAL FORMATTING RULE**: The content for any tool argument MUST be the exact literal text or code. Do not add extra quotes around it or escape internal quotes. The argument starts immediately after its opening `'` and ends immediately before its closing `'`. Use <nex!-pr-amtre?gr+> to separate arguments.
    **Note**: Do nou use special quotes for strings etc. in your code, just use normal quotes.
    **VERY IMPORTANT for Code/Multi-line Text**: When providing code or any text that requires multiple lines (e.g., a Python script, configuration file content), **you MUST include actual newline characters** directly within the string argument.
6.  **Tool Output**: After you use a tool, you will receive a message prefixed with "Tool Output:". Use this output to decide your next step. (If you uset two tools or more, all tool outputs will be listed here.)
7.  **Final Answer**: When the task is fully complete and verified, use the `RESULT` tool to provide the final solution and a brief explanation of what you did.
**CRUCIAL RULE**: NEVER try to recreate any aviable tool with python code! NEVER use a tool if it doesn't make sense! Don't ask the user useless questions! Try to think again for yourself! Find the best tool for each action!
* **INFO**: If you work with paths or files: paths relative to your working directory are not absolute (they don't start with '/').

**Here is your task to solve:**
"""

class Waiter:
    def __init__(self):
        self.calls = {}

    # Wait if needed based on rate limits from the MODELS-Config
    def wait_if_needed(self, model_idx: str):
        model_rate_limit = MODELS[model_idx]['rate_limit']
        if model_rate_limit is not False and model_rate_limit is not None and model_idx in MODELS:
            time_window = model_rate_limit[0]
            rate_limit = model_rate_limit[1]
            if model_idx not in self.calls:
                self.calls[model_idx] = deque()
            current_time = time.time()
            while self.calls[model_idx] and self.calls[model_idx][0] <= current_time - time_window:
                self.calls[model_idx].popleft()
            if len(self.calls[model_idx]) >= rate_limit:
                time_to_wait = (self.calls[model_idx][0] + time_window) - current_time
                if time_to_wait > 0:
                    print(f"🚫 Rate-limit for {model_idx} hit. Waiting for {time_to_wait:.2f} seconds...")
                    time.sleep(time_to_wait)
                    current_time_after_wait = time.time()
                    while self.calls[model_idx] and self.calls[model_idx][0] <= current_time_after_wait - time_window:
                        self.calls[model_idx].popleft()
            self.calls[model_idx].append(time.time())

    # Verify models on start of the programm
    def verify(self):
        if MODELS[LLM_MODEL]["text"] != [True, True]:
            raise Exception(f"⚠️ Error during model verification: {LLM_MODEL} is not a text model")
        if MODELS[WIKI_MODEL]["text"] != [True, True]:
            raise Exception(f"⚠️ Error during model verification: {WIKI_MODEL} is not a text model")

# 4. LLM COMMUNICATORS

# -- Create Waiter Instance --
WAITER = Waiter()
WAITER.verify()

# -- Gemini Communicator Class --
class GeminiCommunicator:
    def __init__(self, model_idx: str, mode: str="txt"):
        model_config = MODELS[model_idx]
        genai.configure(api_key=model_config['api_key'])
        self.model = genai.GenerativeModel(model_config['name'])
        self.model_idx = model_idx
        self.mode = mode

    # Chat Method
    def chat(self, message: str, context: list) -> tuple[str, list]:
        try:
            if self.mode == "txt":
                WAITER.wait_if_needed(self.model_idx)
                chat_session = self.model.start_chat(history=context)
                response = chat_session.send_message(message)
                model_response = response.text
                updated_context = chat_session.history
                return model_response, updated_context
            elif self.mode == "img":
                if not os.path.exists(context):
                    return("Error: Invalid image path provided!", [])
                image = Image.open(context)
                contents = [message, image]
                WAITER.wait_if_needed(self.model_idx)
                response = self.model.generate_content(contents)
                description = response.text
                return description, []
        except Exception as e:
            raise Exception(f"Error during Gemini chat communication: {e}")

# -- Ollama Communicator Class --
class OllamaCommunicator:
    def __init__(self, model_idx: str, mode: str="txt"):
        model = MODELS[model_idx]
        host = model["host"]
        self.model_idx = model_idx
        self.model_name = model["name"]
        self.client = ollama.Client(host=host)
        self.mode = mode

    # Chat Method
    def chat(self, message: str, context: list) -> tuple[str, list]:
        try:
            if self.mode == "txt":
                messages_to_send = context + [{'role': 'user', 'content': message}]
                WAITER.wait_if_needed(self.model_idx)
                response = self.client.chat(model=self.model_name, messages=messages_to_send)
                model_response_content = response['message']['content']
                updated_context = messages_to_send + [{'role': 'assistant', 'content': model_response_content}]
                return model_response_content, updated_context
            elif self.mode == "img":
                if not os.path.exists(context):
                    return("Error: Invalid image path provided!", [])
                with open(context, "rb") as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                    messages = [{
                    'role': 'user',
                    'content': message,
                    'images': [image_base64]
                    }]
                    WAITER.wait_if_needed(self.model_idx)
                    response = self.client.chat(
                            model=self.model_name,
                            messages=messages,
                            stream=False
                    )
                    description = response['message']['content']
                    return description, []
            else:
                raise ValueError(f"Unknown mode: {self.mode}")
        except Exception as e:
            raise Exception(f"Error during Ollama chat communication: {e}")

# -- Create Communicator Class --
class CreateCommunicator:
    def __init__(self, model_idx: str, mode: str="txt"):
        model_config = MODELS[model_idx]
        model_type = model_config["type"]
        if model_type == "Gemini":
            self.__class__ = GeminiCommunicator
            self.__init__(model_idx, mode)
        elif model_type == "Ollama":
            self.__class__ = OllamaCommunicator
            self.__init__(model_idx, mode)
        else:
            raise ValueError(f"Unbekannter Modelltyp: {model_config['type']}")