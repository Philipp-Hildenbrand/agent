import wikipedia, json
from utils.model import CreateCommunicator
from utils.parser import Parser

# -- Configuration --
WIKI_MODEL = json.load(open("config.json", "r"))["MODEL_CONFIG"]["WIKI_MODEL"]

# -- Wiki Search Prompt --
WIKI_PROMPT = """
**Wiki Search**: Use this tool to search Wikipedia for information.
    * **Usage**: `<<<WIKI:'topic'<nex!-pr-amtre?gr+>'language'<nex!-pr-amtre?gr+>'length'>>>`
        * `topic`: The subject to search for.
        * `language`: The language of the Wikipedia page (e.g., 'en' for English, 'de' for German).
        * `length`: Desired length of the answer (e.g., 'one sentence', 'two paragraphs', '5 sentences', 'max 100 words', 'min 2 paragraphs, max 300 words', 'summary'). 'summary' returns the orginal summary from wikipedia
    * **Example**: `<<<WIKI:'Artificial Intelligence'<nex!-pr-amtre?gr+>'en'<nex!-pr-amtre?gr+>'one paragraph, 150 words'>>>`.
    * **Note**: The tool will return a summarized answer based on the desired length.
"""

# -- Internal Wiki-Prompt --
INTERNAL_WIKI_PROMPT = """
You are an AI assistant specialized in searching and summarizing information from Wikipedia.
Your goal is to find comprehensive information on the topic "{topic}" in {language} language,
and then summarize it to a {length} length. If the length is 'summary', return the original summary from Wikipedia without any modifications by the GET_SUMMARY tool.
You must ONLY use the provided Wikipedia tools and your output should be based solely on the information retrieved from Wikipedia.
Do NOT use any prior knowledge! Do NOT simulate the interaction with the tools!

Your available tools for Wikipedia interaction are:
* **SET_LANG**: Set the language for Wikipedia searches.
    * **Usage**: `<<<SET_LANG:'language_code'>>>`
    * **Example**: `<<<SET_LANG:'de'>>>` for German, or `<<<SET_LANG:'en'>>>` for English.
* **SEARCH**: Search for a topic on Wikipedia.
    * **Usage**: `<<<SEARCH:'search_query'>>>`
    * **Example**: `<<<SEARCH:'Artificial Intelligence'>>>`
* **GET_PAGE_CONTENT**: Get the full content of a specific Wikipedia page.
    * **Usage**: `<<<GET_PAGE_CONTENT:'page_title'>>>`
    * **Example**: `<<<GET_PAGE_CONTENT:'Artificial intelligence'>>>`
* **GET_SUMMARY**: Get a summary of a specific Wikipedia page. This is useful for getting quick overviews.
    * **Usage**: `<<<GET_SUMMARY:'page_title'>>>`
    * **Example**: `<<<GET_SUMMARY:'Artificial intelligence'>>>`

When you have gathered all necessary information and successfully summarized it to the requested length,
use the **WIKI_RESULT** tool.
    * **Usage**: `<<<WIKI_RESULT:'Your summarized answer here.'>>>`
    * **Example**: `<<<WIKI_RESULT:'Artificial intelligence is a field of computer science...'>>>`
    * **REMEMBER**: Use this tool not in combination with any other tools! Use this only if you are finished with your task!

You will receive the tool output after each tool execution. Use this output to guide your next steps.
Start by setting the language, then search for the topic, and finally return the result to the user.
"""

# -- Wiki Search Class --
class WikiSearch:
    def __init__(self):
        self.wiki_llm = CreateCommunicator(WIKI_MODEL)
        self.init_prompt = INTERNAL_WIKI_PROMPT
        self.parser = Parser()

    # Wiki Search
    def search(self, topic: str="", language: str="en", length: str="summary", max_turns: int=10) -> str:
        try:
            self.context = []
            current_internal_prompt = self.init_prompt.replace('{topic}', topic).replace('{language}', language).replace('{length}', length)
            for i in range(max_turns):
                print(f"🧠 Internal Wiki-LLM Output: {current_internal_prompt[1:50].replace("\n", " ")}...")
                wiki_llm_response, self.context = self.wiki_llm.chat(current_internal_prompt, self.context)
                print(f"🧠 Internal Wiki-LLM Action: {wiki_llm_response[1:50].replace("\n", " ")}...")
                tool_calls = self.parser.extract_tagged_sections(wiki_llm_response)
                output = []
                for i, tool_call in enumerate(tool_calls):
                    params = self.parser.parse_tool_call(tool_call)
                    if params[0] == "SET_LANG":
                        try:
                            wikipedia.set_lang(params[1])
                            output.append(f"Output from tool{i if i != 0 else ''}: Successfully set Wikipedia language to '{params[1]}'. ")
                        except Exception as e:
                            output.append(f"Output from tool{i if i != 0 else ''}: Error setting language: {e} ")
                    elif params[0] == "SEARCH":
                        try:
                            search_results = wikipedia.search(params[1])
                            if search_results:
                                output.append(f"Output from tool{i if i != 0 else ''}: Search Results (top 5): " + "".join(search_results[:5]) + " ")
                            else:
                                output.append(f"Output from tool{i if i != 0 else ''}: No search results found. ")
                        except Exception as e:
                            output.append(f"Output from tool{i if i != 0 else ''}: Error during Wikipedia search: {e} ")
                    elif params[0] == "GET_PAGE_CONTENT":
                        try:
                            page = wikipedia.page(params[1], auto_suggest=False)
                            output.append(f"Output from tool{i if i != 0 else ''}: Page Content for '{params[1]}':\n{page.content[:2000]}... Page Summary:\n{page.summary} ")
                        except wikipedia.exceptions.PageError:
                            output.append(f"Output from tool{i if i != 0 else ''}: Error: Page '{params[1]}' not found. ")
                        except wikipedia.exceptions.DisambiguationError as e:
                            output.append(f"Output from tool{i if i != 0 else ''}: Disambiguation Error for '{params[1]}'. Options: {e.options[:5]} ")
                        except Exception as e:
                            output.append(f"Output from tool{i if i != 0 else ''}: Error getting page content for '{params[1]}': {e} ")
                    elif params[0] == "GET_SUMMARY":
                        try:
                            page = wikipedia.page(params[1], auto_suggest=False)
                            output.append(f"Output from tool{i if i != 0 else ''}: Page Summary for '{params[1]}':\n{page.summary} ")
                        except wikipedia.exceptions.PageError:
                            output.append(f"Output from tool{i if i != 0 else ''}: Error: Page '{params[1]}' not found. ")
                        except wikipedia.exceptions.DisambiguationError as e:
                            output.append(f"Output from tool{i if i != 0 else ''}: Disambiguation Error for '{params[1]}'. Options: {e.options[:5]} ")
                        except Exception as e:
                            output.append(f"Output from tool{i if i != 0 else ''}: Error getting page summary for '{params[1]}': {e} ")
                    elif params[0] == "WIKI_RESULT":
                        return f"Result from Wikipedia-Search: {params[1]}"
                    else:
                        output.append(f"Output from tool{i if i != 0 else ''}: Unknown tool call: {tool_call}. ")
                current_internal_prompt = "".join(output)
            return "Error: Wikipedia search could not be completed within the maximum internal turns."
        except Exception as e:
            return f"An unexpected error occurred during Wikipedia search: {e}"