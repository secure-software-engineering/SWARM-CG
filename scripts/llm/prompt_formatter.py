import logging

import llm.prompts
import tiktoken
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(f"main.{__name__}")


class PromptFormatter:
    """
    A class that handles formatting prompts based on prompt type.

    Attributes:
        prompt_handlers (dict): A dictionary mapping prompt types to their corresponding handler methods.
    """

    def __init__(self, show_token_count=False):
        self.prompt_handlers = {
            "generic": self.process_generic_prompt,
        }
        self.show_token_count = show_token_count

    def get_token_count(self, text, prompt_id):
        """
        Retrieves the token count of the given text.

        Args:
            text (str): The text to be tokenized.

        Returns:
            int: The token count.
        """
        prices_per_token = {
            "gpt-3.5-turbo-0125": 0.0000005,
            "gpt-4-turbo": 0.00001,
            "gpt-4": 0.00001,
        }
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        number_of_tokens_3_5 = len(encoding.encode(text))
        logger.debug(
            f"Number of tokens for model `gpt-3.5-turbo`: {number_of_tokens_3_5}"
            + f" Cost: {number_of_tokens_3_5 * prices_per_token['gpt-3.5-turbo-0125']:.5f}"
            + f" Prompt: {prompt_id}"
        )

        encoding = tiktoken.encoding_for_model("gpt-4")
        number_of_tokens_4 = len(encoding.encode(text))
        logger.debug(
            f"Number of tokens for model `gpt-4-turbo`: {number_of_tokens_4}"
            + f" Cost: {number_of_tokens_4 * prices_per_token['gpt-4']:.5f}"
            + f" Prompt: {prompt_id}"
        )

        return {
            "gpt-3.5-turbo": number_of_tokens_3_5,
            "gpt-4-turbo": number_of_tokens_4,
        }

    def _get_prompt_by_id(self, prompt_id):
        """
        Retrieves the prompt template based on the given prompt ID.

        Args:
            prompt_id (str): The ID of the prompt.

        Returns:
            str: The prompt template.
        """
        return eval(f"llm.prompts.{prompt_id}").strip()

    def process_generic_prompt(self, prompt_id, text):
        """
        Processes a generic prompt by formatting the prompt template with the given text.

        Args:
            prompt_id (str): The ID of the prompt.
            text (str): The text to be included in the prompt.

        Returns:
            str: The formatted prompt.
        """
        prompt = PromptTemplate(
            template=self._get_prompt_by_id(prompt_id),
            input_variables=["text"],
        )

        prompt_data = {
            "text": text,
        }

        _input = prompt.format_prompt(**prompt_data)

        if self.show_token_count:
            self.get_token_count(_input.to_string(), prompt_id)
        return _input.to_string()

    def process_system_chat_prompt(self, prompt_id_system, prompt_id, text):
        system_prompt = self._get_prompt_by_id(prompt_id_system)
        user_prompt = self._get_prompt_by_id(prompt_id)

        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", user_prompt)]
        )

        prompt_data = {
            "code": text,
        }

        _input = prompt.format_messages(**prompt_data)

        if self.show_token_count:
            self.get_token_count("".join([x.pretty_repr() for x in _input]), prompt_id)
        return _input

    def format_prompt(self, prompt_id, prompt_type, text):
        # TODO: Remove this
        """
        Formats a prompt based on the given prompt ID, prompt type, and text.

        Args:
            prompt_id (str): The ID of the prompt.
            prompt_type (str): The type of the prompt.
            text (str): The text to be included in the prompt.

        Returns:
            str: The formatted prompt.

        Raises:
            ValueError: If no handler is found for the given prompt type.
        """
        try:
            handler = self.prompt_handlers.get(prompt_type)

            if handler is None:
                raise ValueError(f"No handlers found for: {prompt_id}")

            return handler(prompt_id, text)
        except ValueError as ve:
            logger.error(str(ve))
            return ""
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}", stack_info=True)
            return ""
