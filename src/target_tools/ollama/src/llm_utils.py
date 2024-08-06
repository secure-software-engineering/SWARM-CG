import os
import re
import time
import traceback
from pathlib import Path
from langchain.chat_models import ChatOpenAI
import multiprocessing



def process_file(file_path, llm, openai_llm, prompt_id):
    pass