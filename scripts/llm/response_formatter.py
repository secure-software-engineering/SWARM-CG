import json
import re

from langchain_core.messages.ai import AIMessage


class ReponseFormatter:
    @staticmethod
    def get_transalated_json(data):
        def extract_sections(data):
            """ Extract distinct sections from the provided multi-part data string. """
            sections = {}
            current_section = None
            content = []

            for line in data.splitlines():
                section_match = re.match(r'^# (\w+)$', line)
                if section_match:
                    # Save the previous section if there is one
                    if current_section is not None:
                        sections[current_section] = '\n'.join(content).strip()
                        content = []
                    current_section = section_match.group(1)
                else:
                    content.append(line)
            
            # Save the last section
            if current_section is not None:
                sections[current_section] = '\n'.join(content).strip()

            return sections

        def parse_translated_code(code_section):
            """ Extract and return code blocks from the translated_code section. """
            code_blocks = re.split(r'^```[a-zA-Z]+\n', code_section, flags=re.MULTILINE)
            return [block.strip() for block in code_blocks if block.strip()]

        def parse_call_graph(graph_section):
            """ Convert JSON string from the call_graph section to a Python dictionary. """
            try:
                return json.loads(graph_section)
            except json.JSONDecodeError as e:
                print("Error parsing call graph JSON:", e)
                return {}

        try:
            sections = extract_sections(data)
            if 'translated_code' in sections:
                code_blocks = parse_translated_code(sections['translated_code'])
                print("Code Blocks:", code_blocks)
            if 'call_graph' in sections:
                call_graph = parse_call_graph(sections['call_graph'])
                print("Call Graph:", call_graph)
        except Exception as e:
            print("An error occurred:", str(e))


if __name__ == "__main__":
    data = '# translated_code\n```main.java\nimport java.util.Arrays;\nimport java.util.HashMap;\nimport java.util.Map;\n\npublic class main {\n    public static void main(String[] args) {\n        String.join(" ", Arrays.asList("1", "2", "3"));\n\n        "a b c".split(" ");\n\n        Map<String, Integer> d = new HashMap<>();\n        d.put("a", 1);\n\n        d.entrySet();\n    }\n}\n```\n\n```main2.java\nimport java.util.Arrays;\nimport java.util.HashMap;\nimport java.util.Map;\n\npublic class main {\n    public static void main(String[] args) {\n        String.join(" ", Arrays.asList("1", "2", "3"));\n\n        "a b c".split(" ");\n\n        Map<String, Integer> d = new HashMap<>();\n        d.put("a", 1);\n\n        d.entrySet();\n    }\n}\n```# call_graph\n```\n{\n    "main.main": [\n        "<**JavaString**>.join",\n        "<**JavaString**>.split",\n        "<**JavaMap**>.entrySet"\n    ],\n    "<**JavaString**>.join": [],\n    "<**JavaString**>.split": [],\n    "<**JavaMap**>.entrySet": []\n}\n```'
    ReponseFormatter.get_transalated_json(data)