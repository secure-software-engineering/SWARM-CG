import logging
import multiprocessing

import requests
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from utils.exceptions import TimeoutException

logger = logging.getLogger(f"main.{__name__}")


class LLMRunner:
    """
    A class that represents a runner for the LLM (Language Model) system.

    Args:
        model (str): The name of the LLM model to use.
        ollama_url (str, optional): The URL of the Ollama server. Defaults to None.
        openai_key (str, optional): The API key for OpenAI. Defaults to None.
        temperature (float, optional): The temperature parameter for generating responses. Defaults to 0.1.
        request_timeout (int, optional): The timeout duration for making requests. Defaults to 60.
        run_in_subprocess (bool, optional): Whether to run the LLM in a subprocess. Defaults to True.
        enable_streaming (bool, optional): Whether to enable streaming for the LLM. Defaults to True.
    """

    def __init__(
        self,
        model,
        ollama_url=None,
        openai_key=None,
        temperature=0.0,
        request_timeout=60,
        run_in_subprocess=False,
        enable_streaming=True,
        enable_chat=False,
        stop=[
            "<|start_header_id|>",
            "<|end_header_id|>",
            "<|eot_id|>",
            "<|reserved_special_token",
        ],
    ) -> None:
        self.run_in_subprocess = run_in_subprocess
        self.ollama_url = ollama_url
        self.model = model
        self.request_timeout = request_timeout
        self.stop = stop

        if self.model.startswith(("gpt-", "ft:gpt-")):
            self.llm = ChatOpenAI(
                model_name=model,
                temperature=temperature,
                openai_api_key=openai_key,
            )
            self.llm.bind(response_format={"type": "json_object"})
        else:
            if enable_chat:
                self.llm = ChatOllama(
                    model=model,
                    callback_manager=(
                        CallbackManager([StreamingStdOutCallbackHandler()])
                        if enable_streaming
                        else None
                    ),
                    temperature=temperature,
                    timeout=request_timeout,
                    stop=self.stop,
                )
            else:
                self.llm = Ollama(
                    model=model,
                    callback_manager=(
                        CallbackManager([StreamingStdOutCallbackHandler()])
                        if enable_streaming
                        else None
                    ),
                    temperature=temperature,
                    timeout=request_timeout,
                    stop=self.stop,
                )
            self.llm.base_url = self.ollama_url
            self._kickstart_ollama_model()

    def is_ollama_online(self):
        """
        Check if the Ollama server is online.

        Returns:
            bool: True if the Ollama server is online, False otherwise.
        """
        try:
            logger.info(f"Checking Ollama server status at {self.ollama_url}")
            res = requests.get(self.ollama_url)
            if res.status_code == 200:
                if res.text == "Ollama is running":
                    return True
            return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return False

    def _kickstart_ollama_model(self):
        """
        Deploy the model before the actual prompt.
        """
        if not self.model.startswith(("gpt-", "ft:gpt-")):
            if self.is_ollama_online():
                logger.info("Ollama is online!")
                logger.info("Loading model...")
                self.llm.timeout = 600
                self.llm.invoke("Dummy prompt. limit your response to 1 letter.")
                self.llm.timeout = self.request_timeout
                logger.info(f"{self.model} Model loaded!")
            else:
                logger.error("Ollama server is not online!!!")
                return ""

    def _invoke_runner(self, llm, prompt, queue):
        """
        Invoke the LLM runner with the given prompt.

        Args:
            llm (LangChain model): The LangChain model instance to use.
            prompt (str): The prompt to invoke the LLM with.
            queue (multiprocessing.Queue): The queue for communication between processes.
        """
        try:
            output = llm.invoke(prompt)
            queue.put(output)
        except Exception as e:
            queue.put(e)

    def process_prompt(self, prompt):
        """
        Process the given prompt using the LLM runner.

        Args:
            prompt_id (str): The ID of the prompt.
            prompt_type (str): The type of the prompt.
            text (str): The text of the prompt.

        Returns:
            str: The output generated by the LLM runner.
        """
        try:
            if self.run_in_subprocess:
                # Queue for communication between processes
                queue = multiprocessing.Queue()

                # Create a process for llm.invoke
                process = multiprocessing.Process(
                    target=self._invoke_runner,
                    args=(self.llm, prompt, queue),
                )
                process.start()

                # Wait for the process to finish with a timeout (e.g., 60 seconds)
                process.join(timeout=self.request_timeout)

                if process.is_alive():
                    logger.error(f"Timeout occurred for prompt:\n {prompt}")
                    process.terminate()  # Terminate the process if it's still running
                    process.join()
                    raise TimeoutException("process_prompt timeout")

                result = queue.get_nowait()

                if isinstance(result, Exception):
                    raise result

                output = result
            else:
                output = self.llm.invoke(prompt)

            if isinstance(self.llm, ChatOpenAI):
                output = output.content

            return output
        except Exception as e:
            # traceback.print_exc()
            logger.error(f"Prompt failed: {e}")
            return ""
