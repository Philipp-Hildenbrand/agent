# -- Importing Tools --
from tools.AskUser import AskUser, ASK_USER_PROMPT
from tools.FileEditor import FileEditor, FILE_EDITOR_PROMPT
from tools.Shell import ShellExecutor, SHELL_EXECUTOR_PROMPT
from tools.WikiSearch import WikiSearch, WIKI_PROMPT
from tools.ImageAnalyzer import ImageAnalyzer, IMAGE_ANALYZER_PROMPT
from tools.Database import Database, DATABASE_PROMPT
from utils.model import CreateCommunicator, Waiter, INIT_PROMPT
from utils.processor import ToolProcessor
from utils.parser import Parser
from utils.prompts import ONLY_ONE_TOOL_PROMPT
import json, os

# -- Configuration --
ACTIVATED_TOOLS = json.load(open("config.json", "r"))["ACTIVATED_TOOLS"]
LLM_MODEL = json.load(open("config.json", "r"))["MODEL_CONFIG"]["LLM_MODEL"]
TOOL_OUTPUTS = json.load(open("config.json", "r"))["TOOL_OUTPUTS"]
THOUGHTS_IN_TERMINAL = json.load(open("config.json", "r"))["THOUGHTS_IN_TERMINAL"]
AGENT_BASE_DIR = json.load(open("config.json", "r"))["AGENT_BASE_DIR"]

# -- Agent Class --
class Agent:
    def __init__(self):
        self.llm = CreateCommunicator(LLM_MODEL)
        file_editor = FileEditor() if ACTIVATED_TOOLS["file_editor"] else None
        shell_executor = ShellExecutor() if ACTIVATED_TOOLS["shell_executor"] else None
        ask_user = AskUser() if ACTIVATED_TOOLS["ask_user"] else None
        wiki = WikiSearch() if ACTIVATED_TOOLS["wiki"] else None
        image_analyzer = ImageAnalyzer()
        database = Database()
        self.tool_processor = ToolProcessor(file_editor, shell_executor, ask_user, wiki, image_analyzer, database)
        self.parser = Parser()
        self.context = []
        self.WAITER = Waiter()
        self.init_prompt = self._build_init_prompt()

    # Build Initial Prompt
    def _build_init_prompt(self):
        prompt = INIT_PROMPT
        prompt = prompt.replace("{file_editor_prompt}", FILE_EDITOR_PROMPT if ACTIVATED_TOOLS["file_editor"] else "")
        prompt = prompt.replace("{shell_executor_prompt}", SHELL_EXECUTOR_PROMPT if ACTIVATED_TOOLS["shell_executor"] else "")
        prompt = prompt.replace("{ask_user_prompt}", ASK_USER_PROMPT if ACTIVATED_TOOLS["ask_user"] else "")
        prompt = prompt.replace("{wiki_prompt}", WIKI_PROMPT if ACTIVATED_TOOLS["wiki"] else "")
        prompt = prompt.replace("{only_one_tool_prompt}", ONLY_ONE_TOOL_PROMPT if not any(ACTIVATED_TOOLS.values()) else "")
        prompt = prompt.replace("{image_analyzer_prompt}", IMAGE_ANALYZER_PROMPT if ACTIVATED_TOOLS["image_analyzer"] else "")
        prompt = prompt.replace("{database_prompt}", DATABASE_PROMPT if ACTIVATED_TOOLS["database"] else "")
        return prompt

    # Reset the Context of the Agent
    def reset_context(self):
        self.context = []

    def run(self, task: str, max_turns: int=40):
        self.WAITER.wait_if_needed(LLM_MODEL)
        print(f"======= Starting Task =======")
        os.makedirs(AGENT_BASE_DIR, exist_ok=True)
        prompt = self.init_prompt + task

        for turn in range(max_turns):
            print(f"\n--- Turn {turn + 1}/{max_turns} ---")
            print("🤖 Agent is thinking...")
            llm_response, self.context = self.llm.chat(prompt, self.context)
            print(f"▶️ Agent Action:\n{llm_response if THOUGHTS_IN_TERMINAL else ''.join([f'⚙️ {_} \n' for _ in self.parser.extract_tagged_sections(llm_response)])}")
            status, tool_output = self.tool_processor.process(llm_response)
            if status == "FINISHED":
                print("\n✅ Task Finished!")
                print("===========================")
                print(f"🏁 Final Result:\n→ {tool_output}")
                print("===========================\n\n")
                return
            else: # status == "CONTINUE"
                if TOOL_OUTPUTS:
                    print(f"\n🛠️ Tool Output:\n{tool_output}")
                prompt = tool_output
        print("\n🚫 Task incomplete: Maximum turns reached.")

# -- Main --
if __name__ == "__main__":
    agent = Agent()
    while True:
        task = input("Enter your task for the agent: ")
        if task.lower() == "exit":
            agent = None
            break
        elif task.lower() == "reset":
            agent.reset_context()
        else:
            agent.run(task)