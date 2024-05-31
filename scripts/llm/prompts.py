translation_prompt = '''
You are an expert in {source_language} and {target_language} programming languages. You have been given a task to translate the given code from {source_language} to {target_language}. This is for creating a micro-benchmark for call-graph analysis containing code challenges targeting specific language features. Along with the code, you have been provided with the call graph of the code in JSON format. Your task is to translate the code to the mentioned language and provide the call graph for the translated code in JSON format.

Each question has four parts:
	1. **Language Feature Category**: {source_language} language feature category
	2. **Description**: description of code as comments at the top of the code
	3. **Source code**: {source_language} code delimited by triple quotes
	4. **Call graph**: call graph of {source_language} code in JSON format delimited by triple quotes. 

Follow the instructions below to complete the task for each question: 
	1. Translate the given {source_language} code into {target_language}.
	2. Provide the call graph in JSON format for the translated code.
    3. Do not include additional comments in the output code.
    4. If the given code is in two separate files the file names will be mentioned, the translated code should also be as separate files with their file names.
    5. Use the below example question and answer as training data. 
    6. Follow the answer format in JSON strictly. Do not provide any additional information.

Example Question:
1. **Language Feature Category**: param_call

2. **Description**: A parameter is passed as the return value of a different function call.

3. **Source code**: 
```
def func(a):
    a()

def func2():
    return func3

def func3():
    pass

func(func2())
```

4. **Call graph**: 
```
{
    "main": [
        "main.func",
        "main.func2"
    ],
    "main.func": [
        "main.func3"
    ],
    "main.func2": [],
    "main.func3": []
}
```
	
Example Answer:
{{
    "language_feature": "param_call",
    "description": "A parameter is passed as the return value of a different function call.",
    "translated_code": {translated_code_example},
    "call_graph": "{translated_call_graph_example}"
}}
	
Question: 
1. **Language Feature Category**: {feature_category}

2. **Description**: {description}

3. **Source code**: 
```
{code}
```

4. **Call graph**: 
```
{call_graph}
```
'''

