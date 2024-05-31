import json
import re

from langchain_core.messages.ai import AIMessage


class ReponseFormatter:
    @staticmethod
    def get_vulnerability(record):
        # Test if record can be cast as an int and return it otherwise try to parse it somehow
        if isinstance(record, AIMessage):
            record = record.content
        try:
            cwe_number = int(record)
            return cwe_number
        except ValueError:
            # Try to extract the cwe number from the record
            try:
                cwe_number = int(re.search(r"\d+", record).group())
                return cwe_number
            except Exception as e:
                return 00

    @staticmethod
    def get_binary_vulnerability(record):
        # Test if record can be cast as an int and return it otherwise try to parse it somehow
        if isinstance(record, AIMessage):
            record = record.content
        try:
            if record.lower() in ["true", "false"]:
                return record.lower()
            else:
                is_true = False
                is_false = False
                if re.search(r"true", record, re.IGNORECASE):
                    is_true = True
                if re.search(r"false", record, re.IGNORECASE):
                    is_false = True
                if is_true and is_false:
                    # If both are present, return false
                    return "false"  # Default to false to match SA tools
                elif is_true:
                    return "true"
                elif is_false:
                    return "false"
                else:
                    return "false"  # Default to false to match SA tools
        except ValueError:
            return "false"  # Default to false to match SA tools

    @staticmethod
    def escape_markdown(text):
        """
        Escape Markdown special characters in the given string.

        Args:
        text (str): The input string to escape.

        Returns:
        str: The escaped Markdown string.
        """
        if isinstance(text, AIMessage):
            text = text.content
        # Characters to escape in Markdown
        markdown_chars = [
            # "\\",
            "`",
            # "*",
            # "_",
            # "{",
            # "}",
            # "[",
            # "]",
            # "(",
            # ")",
            # "#",
            # "+",
            # "-",
            # ".",
            # "!",
        ]  # noqa

        # Escape each character with a backslash
        for char in markdown_chars:
            text = text.replace(char, f"\\{char}")

        return text

    @staticmethod
    def make_md_collapsable(title, content):
        """
        Create a collapsable Markdown section with the given title and content.

        Args:
        title (str): The title of the collapsable section.
        content (str): The content of the collapsable section.

        Returns:
        str: The Markdown-formatted collapsable section.
        """
        # Escape special characters in the title and content
        title = ReponseFormatter.escape_markdown(title)
        content = ReponseFormatter.escape_markdown(content)

        # Create the collapsable section
        collapsable = f"\n\n<details><summary>{title}</summary>\n\n\n```\n{content}\n```\n\n</details>\n\n"

        return collapsable
