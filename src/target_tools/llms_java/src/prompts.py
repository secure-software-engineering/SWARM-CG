questions_based_1_system = (
    "You will examine and identify the function calls in the given {language} code. You"
    " have to examine the code in detail by resolving the alias of variables."
)

questions_based_1_java = """## Task Description

**Objective**: Examine and identify the function calls in the given {language} code and answer the questions.

**Instructions**:
1. For each question below, provide a concise answer indicating the targets called by each caller.
2. For each question, list every target as a comma-separated list.
3. Do not include additional explanations or commentary in your answers.
4. Include both explicit and implicit function calls in your answers. An implicit function call is a function that is called as a result of another operation, such as the __init__ method being called when an object is created.
5. If a caller's target is identified through an alias or a reference, list the actual target function that is called after resolving the alias.
6. Example of {language} code, questions, and answers are given below. This example should be used as training data.
 
**Format for Answers**:
- Provide your answer next to each question number, using only one word.
- Do not include the questions in your answer.
- Example:
    1. vc.Class:target
    2. vc.Class:anotherTarget

**Example Java Code**: 
```java
// vc/Class.java
package vc;
import lib.annotations.callgraph.DirectCall;

class Class {

    public void target(){ }

    @DirectCall(name = "target", line = 12, resolvedTargets = "Lvc/Class;")
    public static void main(String[] args){
        Class cls = new Class();
        cls.target();
    }
}
```

**Example Questions**:
1. What are the target function calls made by the caller "vc.Class
(java.lang.String[])" in the file "vc/Class.java"?

**Example Answers**:
1. vc.Class:target()

**{language} Code Provided**:

{code}

**Questions**:
{questions}

**Answers**:
{answers}"""

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
