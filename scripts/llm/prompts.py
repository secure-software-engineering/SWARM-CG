translation_prompt_system = '''
You are an expert in {source_language} and {target_language} programming languages. You have been given a task to translate the given code from {source_language} to {target_language}. This is for creating a micro-benchmark for call-graph analysis containing code challenges targeting specific language features. Along with the code, you have been provided with the call graph of the code in JSON format. Your task is to translate the code to the mentioned language and provide the call graph for the translated code in JSON format.
'''

translation_prompt_user_json = '''
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
    7. Return a JSON object according to the example answer format provided below without formatting.

Example Question:
1. **Language Feature Category**: param_call

2. **Description**: A parameter is passed as the return value of a different function call.

3. **Source code**: 
```main.py
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
{{
    "main": [
        "main.func",
        "main.func2"
    ],
    "main.func": [
        "main.func3"
    ],
    "main.func2": [],
    "main.func3": []
}}
```
	
Example Answer:
```
{{
    "translated_code": {{
        "main.{filetype_suffix}": "{translated_code_example}"
    }},
    "call_graph": "{translated_call_graph_example}"
}}
```
	
Question: 
1. **Language Feature Category**: {feature_category}
2. **Description**: {description}
3. **Source code**: 
{code}

4. **Call graph**: 
```
{code_call_graph}
```

Answer:
'''

translation_prompt_user = '''
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
    6. Follow the answer format strictly provided below with two sections: translated_code and call_graph. Do not provide any additional information.

Example Question:
1. **Language Feature Category**: param_call

2. **Description**: A parameter is passed as the return value of a different function call.

3. **Source code**: 
```main.py
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
{{
    "main": [
        "main.func",
        "main.func2"
    ],
    "main.func": [
        "main.func3"
    ],
    "main.func2": [],
    "main.func3": []
}}
```
	
Example Answer:
# translated_code
```main.{filetype_suffix}
{translated_code_example}
```

# call_graph
```
{translated_call_graph_example}
```
	
Question: 
1. **Language Feature Category**: {feature_category}
2. **Description**: {description}
3. **Source code**: 
{code}

4. **Call graph**: 
```
{code_call_graph}
```

Answer:
'''

# Example question and answer for javascript
translated_code_example_javascript = r'''
function func(a) {
    a();
}

function func2() {
    return func3;
}

function func3() {
}

func(func2());
'''

translated_callgraph_example_javascript = r'''
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
'''

# Example question and answer for javascript
translated_code_example_java = r'''
public class main {
    public static void main(String[] args) {
        func(func2());
    }

    public static void func(Runnable a) {
        a.run();
    }

    public static Runnable func2() {
        return Main::func3;
    }

    public static void func3() {
        // this function currently does nothing
    }
}
'''

translated_callgraph_example_java = r'''
{
    "main.main": [
        "main.func",
        "main.func2"
    ],
    "main.func": [
        "main.func3"
    ],
    "main.func2": [],
    "main.func3": []
}
'''