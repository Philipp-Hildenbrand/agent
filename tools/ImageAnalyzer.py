from utils.model import CreateCommunicator
import json, os

# -- Configuration --
IMAGE_MODEL = json.load(open("config.json", "r"))["MODEL_CONFIG"]["IMAGE_MODEL"]
AGENT_BASE_DIR = json.load(open("config.json", "r"))["AGENT_BASE_DIR"]

# -- Image Analyzer Prompt --
IMAGE_ANALYZER_PROMPT = """
**Image Analyzer**: Use this tool to analyze and process images.
    * **Usage**: `<<<IMAGE:'path_to_image'<nex!-pr-amtre?gr+>'message'>>>`
    * **Example**: `<<<IMAGE:'test.jpg'<nex!-pr-amtre?gr+>'What is this image about?'>>>`.
"""

# -- Image Analyzer Class --
class ImageAnalyzer:
    def __init__(self):
        self.communicator = CreateCommunicator(IMAGE_MODEL, mode="img")

    # -- Analyze Image --
    def analyze(self, message: str="", image_path: str=None):
        try:
            full_path = os.path.join(AGENT_BASE_DIR, image_path)
            result = self.communicator.chat(message, full_path)[0]
            return f"Analysis result: {result}"
        except Exception as e:
            return f"Error analyzing image: {e}"