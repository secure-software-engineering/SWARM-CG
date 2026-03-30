questions_based_1_system = (
    "You will examine and identify the function calls in the given {language} code. You"
    " have to examine the code in detail by resolving the alias of variables."
)

questions_based_1_py = """## Task Description

**Objective**: Examine and identify the function calls in the given {language} code and answer the questions.

**Instructions**:
1. For each question below, list all function calls as a comma-separated list on one line.
2. Do not include additional explanations or commentary in your answers.
3. If there are no calls, leave the answer blank.
4. Include implicit function calls triggered by Python semantics:
   - `ClassName()` or `raise ClassName` calls `ClassName.__init__`, not `ClassName` itself
   - A `for` loop over an object calls its `__iter__` and `__next__` methods
5. If a function is called through an alias or variable reference, resolve and list the actual function being invoked.
6. Only include a function if it is actually invoked with `()` in that scope. Assigning, returning, or passing a function as an argument without invoking it is NOT a call.
7. When a return value is itself invoked in the same expression (e.g., `f()()`), attribute all resulting calls to the scope containing that expression, not inside `f`.
8. Import statements are not function calls.
9. Use `<builtin>.name` format for built-in functions (e.g., `<builtin>.len`, `<builtin>.range`).
10. Example of {language} code, questions, and answers are given below. This example should be used as training data.

**Format for Answers**:
- Provide your answer next to each question number, on one line.
- Do not include the questions in your answer.
- Example:
    1. simple.func
    2. simple.examplefunc
    3.

**Example Python Code**:
```main.py
class Counter:
    def __init__(self):
        pass

def return_func():
    func()

def func():
    a = return_func
    return a

Counter()
a = func
a()()
```

**Example Questions**:
1. What are the module level function calls in the file "main.py"?
2. What are the function calls inside the "main.return_func" function in the file "main.py"?
3. What are the function calls inside the "main.func" function in the file "main.py"?
4. What are the function calls inside the "main.Counter.__init__" function in the file "main.py"?

**Example Answers**:
1. main.Counter.__init__, main.func, main.return_func
2. main.func
3.
4.

**Explanation of Example Answers**:
- Q1: `Counter()` implicitly calls `Counter.__init__` (not `Counter`). `a = func; a()` calls `func`. `a()()` means `func()` returns `return_func`, which is then also called at module level — both calls belong here, not inside `func`.
- Q2: `return_func` explicitly calls `func()`.
- Q3: Inside `func`, `a = return_func` is only an assignment — `return_func` is not invoked, so it is not listed.
- Q4: `Counter.__init__` has no calls in its body.

**{language} Code Provided**:

{code}

**Questions**:
{questions}

**Answers**:
{answers}"""

questions_based_1_js = """## Task Description

**Objective**: Examine and identify the function calls in the given {language} code and answer the questions.

**Instructions**:
1. For each question below, list all function calls as a comma-separated list on one line.
2. Do not include additional explanations or commentary in your answers.
3. If there are no calls, leave the answer blank.
4. Include implicit function calls triggered by JavaScript semantics:
   - `new ClassName()` calls the constructor, which should be identified as `ClassName`
   - Prototype method calls should be resolved to their actual definition on the prototype chain
5. If a function is called through an alias or variable reference, resolve and list the actual function being invoked.
6. Only include a function if it is actually invoked with `()` in that scope. Assigning, returning, or passing a function as an argument without invoking it is NOT a call.
7. When a return value is itself invoked in the same expression (e.g., `f()()`), attribute all resulting calls to the scope containing that expression, not inside `f`.
8. Import/require statements are not function calls.
9. Example of {language} code, questions, and answers are given below. This example should be used as training data.

**Format for Answers**:
- Provide your answer next to each question number, on one line.
- Do not include the questions in your answer.
- Example:
    1. simple.func
    2. simple.examplefunc
    3.

**Example Javascript Code**:
```main.js
function returnFunc() {{
    func();
}}

function func() {{
    a = returnFunc;
    return a;
}}

a = func;
a()();
```

**Example Questions**:
1. What are the module level function calls in the file "main.js"?
2. What are the function calls inside the "main.returnFunc" function in the file "main.js"?
3. What are the function calls inside the "main.func" function in the file "main.js"?

**Example Answers**:
1. main.func, main.returnFunc
2. main.func
3.

**Explanation of Example Answers**:
- Q1: `a = func; a()` calls `func`. `a()()` means `func()` returns `returnFunc`, which is then also called at module level — both calls belong here, not inside `func`.
- Q2: `returnFunc` explicitly calls `func()`.
- Q3: Inside `func`, `a = returnFunc` is only an assignment — `returnFunc` is not invoked, so it is not listed.

**{language} Code Provided**:

{code}

**Questions**:
{questions}

**Answers**:
{answers}"""

questions_based_1_java = """## Task Description

**Objective**: Examine the provided {language} code, analyze the function calls, and answer the questions about the caller-target relationships.

**Instructions**:
1. For each question provide the target functions as a comma-separated list on one line.
2. **IMPORTANT**: Format every target as `[FullyQualifiedClass]:[methodName]([paramTypes])`:
   - Example: `vc.Class:target(java.lang.String[])`
3. Do not include additional explanations or comments in your answers.
4. Do not include the questions in your response. Only list the answers using the question number format shown below.
5. If there are no calls, leave the answer blank.
6. Only include a method if it is actually invoked with `()` in that scope. Passing a method reference without invoking it is NOT a call.
7. When a return value is itself invoked in the same expression (e.g., `f()()`), attribute all resulting calls to the scope containing that expression.
8. For methods called through aliases or references, resolve and return the actual target method.
9. `new ClassName()` calls the constructor `ClassName:<init>()`.
10. Example of {language} code, questions, and answers are given below. This example should be used as training data.

**Format for Response**:
    1. vc.Class:targetFunction(), vc.Class:targetFunction2()
    2. vc.Class:anotherTargetFunction()
    3.

**Example Java Code**:
```java
// vc/Class.java
package vc;

class Class {{

    public void target(){{ }}

    public static void main(String[] args){{
        Class cls = new Class();
        cls.target();
    }}
}}
```

**Example Questions**:
1. What are the target functions invoked by the caller "main(java.lang.String[])" in the "vc/Class" class?

**Example Answers**:
1. vc.Class:<init>(), vc.Class:target()

**{language} Code Provided**:

{code}

**Questions**:
{questions}

**Answers**:
{answers}"""

prompt_template_questions_based_1_py = [
    {
        "role": "system",
        "content": questions_based_1_system,
    },
    {
        "role": "user",
        "content": questions_based_1_py,
    },
]

prompt_template_questions_based_1_py_no_sys = [
    {
        "role": "user",
        "content": questions_based_1_system + "\n\n" + questions_based_1_py,
    },
]

prompt_template_questions_based_1_js = [
    {
        "role": "system",
        "content": questions_based_1_system,
    },
    {
        "role": "user",
        "content": questions_based_1_js,
    },
]

prompt_template_questions_based_1_js_no_sys = [
    {
        "role": "user",
        "content": questions_based_1_system + "\n\n" + questions_based_1_js,
    },
]

prompt_template_questions_based_1_java = [
    {
        "role": "system",
        "content": questions_based_1_system,
    },
    {
        "role": "user",
        "content": questions_based_1_java,
    },
]

prompt_template_questions_based_1_java_no_sys = [
    {
        "role": "user",
        "content": questions_based_1_system + "\n\n" + questions_based_1_java,
    },
]

# #############################################################################
# HeaderGenCS Prompts
# #############################################################################

questions_based_1_system_py_callsites = (
    "You will examine and identify the fully qualified names of function calls in the"
    " given Python code. You have to examine the code in detail by resolving the alias"
    " of variables."
)

questions_based_1_py_callsites = """## Task Description

**Objective**: Examine and identify the fully qualified names of function calls in the given {language} code, including class methods with both the class name and the method name.

**Instructions**:
1. For each question below, provide a concise answer indicating the fully qualified name of function call in that line, including class name for methods.
2. List every function call in that line as a comma separated list.
3. Do not include additional explanations or commentary in your answers.
4. Example of {language} code, questions, and answers are given below. This example should be used as training data.

**Format for Answers**:
- Provide your answer next to each question number, using only one word.
- Add the line number of where the function is defined in the program to the answer separated by ":"
- Count the line number from 1
- Make sure to include the question number in your response
- Do not include the questions in your answer.
- Example:
    1. simple.func:1
    2. simple.examplefunc:2
    3. func:5

**Example {language} Code**:
```main.py
def simple_function():
    pass

def another_function():
    pass

simple_function()
another_function()
```

**Example Questions**:
1. What are the fully qualified function calls at line 7 in file 'main.py'?
2. What are the fully qualified function calls at line 8 in file 'main.py'?

**Example Answers**:
1. main.simple_function:1
2. main.another_function:4

**{language} Code Provided**:

{code}

**Questions**:
{questions}

**Answers**:
{answers}"""

prompt_template_questions_based_1_py_callsites = [
    {
        "role": "system",
        "content": questions_based_1_system_py_callsites,
    },
    {
        "role": "user",
        "content": questions_based_1_py_callsites,
    },
]

prompt_template_questions_based_1_py_callsites_no_sys = [
    {
        "role": "user",
        "content": questions_based_1_system_py_callsites
        + "\n\n"
        + questions_based_1_py_callsites,
    },
]
