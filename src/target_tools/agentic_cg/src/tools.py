import ast
import json
import os
from pathlib import Path

# Configurable via env var for local development; defaults to Docker path
ALLOWED_BASE = os.environ.get("SWARM_CG_BENCHMARK_PATH", "/tmp/benchmarks")


def _validate_path(path: str) -> str:
    resolved = str(Path(path).resolve())
    if not resolved.startswith(ALLOWED_BASE):
        raise PermissionError(f"Path outside benchmark directory: {path}")
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"Path does not exist: {path}")
    return resolved


def read_file(path: str) -> str:
    """Read the contents of a Python source file."""
    resolved = _validate_path(path)
    with open(resolved, "r", encoding="utf-8") as f:
        return f.read()


def list_directory(path: str) -> str:
    """List files and subdirectories at the given path."""
    resolved = _validate_path(path)
    if not os.path.isdir(resolved):
        raise NotADirectoryError(f"Not a directory: {path}")
    entries = sorted(os.listdir(resolved))
    return "\n".join(entries) if entries else "(empty directory)"


def _get_attribute_chain(node: ast.expr) -> str:
    """Flatten an attribute chain (e.g. a.b.c) into a dotted string."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value = _get_attribute_chain(node.value)
        return f"{value}.{node.attr}" if value else node.attr
    return ""


def _collect_calls_in_node(node: ast.AST) -> list[str]:
    """Collect all direct ast.Call expressions within a node (non-recursive into nested defs)."""
    calls = []
    for child in ast.walk(node):
        # Don't descend into nested function/class definitions
        if child is not node and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(child, ast.Call):
            name = _get_attribute_chain(child.func)
            if name:
                calls.append(name)
    return calls


class _ScopeVisitor(ast.NodeVisitor):
    """Walk module-level AST and record function scopes with their call sites."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.entries: list[dict] = []
        self._class_stack: list[str] = []

    def _qualified(self, func_name: str) -> str:
        if self._class_stack:
            return f"{self.module_name}.{'.'.join(self._class_stack)}.{func_name}"
        return f"{self.module_name}.{func_name}"

    def visit_ClassDef(self, node: ast.ClassDef):
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def _visit_func(self, node):
        qname = self._qualified(node.name)
        # Collect calls inside this function body, not descending into nested defs
        calls = []
        for child in node.body:
            for sub in ast.walk(child):
                if sub is not child and isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if isinstance(sub, ast.Call):
                    name = _get_attribute_chain(sub.func)
                    if name:
                        calls.append(name)
        self.entries.append({"qualified_name": qname, "raw_calls": calls})
        # Recurse for nested functions
        old_stack = list(self._class_stack)
        self._class_stack.append(node.name)
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._visit_func(child)
            elif isinstance(child, ast.ClassDef):
                self.visit_ClassDef(child)
        self._class_stack = old_stack

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_func(node)


def _collect_lambdas(tree: ast.Module, module_name: str) -> list[dict]:
    """Collect lambda expressions as separate function entries with <lambdaN> naming.

    Lambdas are numbered in source order within their containing scope.
    A lambda assigned to `x` at module level becomes `main.<lambda1>`, not `main.x`.
    """
    entries: list[dict] = []
    counters: dict[str, int] = {}

    def walk(node, scope_stack: list):
        if isinstance(node, ast.Lambda):
            scope_key = ".".join(
                [module_name]
                + [
                    n.name
                    for n in scope_stack
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                ]
            )
            counters[scope_key] = counters.get(scope_key, 0) + 1
            qname = f"{scope_key}.<lambda{counters[scope_key]}>"
            # Collect raw calls inside this lambda body, not descending into nested lambdas
            lambda_calls: list[str] = []
            for child in ast.walk(node.body):
                if child is not node.body and isinstance(child, ast.Lambda):
                    continue
                if isinstance(child, ast.Call):
                    name = _get_attribute_chain(child.func)
                    if name:
                        lambda_calls.append(name)
            entries.append({"qualified_name": qname, "raw_calls": lambda_calls})
            # Descend into the lambda body for nested lambdas
            scope_stack.append(node)
            for child in ast.iter_child_nodes(node):
                walk(child, scope_stack)
            scope_stack.pop()
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            scope_stack.append(node)
            for child in ast.iter_child_nodes(node):
                walk(child, scope_stack)
            scope_stack.pop()
        else:
            for child in ast.iter_child_nodes(node):
                walk(child, scope_stack)

    walk(tree, [])
    return entries


def get_call_sites(path: str) -> str:
    """
    Parse a Python file and return a JSON summary of function definitions
    with their call sites. Qualified names use module.func or module.Class.method
    format matching the SWARM-CG callgraph.json ground truth convention.

    Also includes:
    - Module-level call sites under the key equal to the module name
    - Decorator applications as implicit module-level calls
    - Lambda expressions as separate entries with <lambdaN> naming
    - Chained calls (a()()) represented as <return_of:X> sentinels
    """
    resolved = _validate_path(path)
    with open(resolved, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return json.dumps({"error": f"SyntaxError: {e}"})

    module_name = Path(resolved).stem  # e.g. "main" from "main.py"

    # Collect module-level calls (top-level body, not inside any function/class)
    module_calls = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                name = _get_attribute_chain(sub.func)
                if name:
                    module_calls.append(name)

    # Also collect decorator applications from module-level function/class definitions.
    # Applying @dec to a function is an implicit call to dec at module level.
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for decorator in node.decorator_list:
            found_call = False
            for sub in ast.walk(decorator):
                if isinstance(sub, ast.Call):
                    name = _get_attribute_chain(sub.func)
                    if name:
                        module_calls.append(name)
                    found_call = True
                    break
            if not found_call:
                # Bare @dec (no call parens): the decorator itself is called
                name = _get_attribute_chain(decorator)
                if name:
                    module_calls.append(name)

    entries = [{"qualified_name": module_name, "raw_calls": module_calls}]

    visitor = _ScopeVisitor(module_name)
    visitor.visit(tree)
    entries.extend(visitor.entries)

    # Add lambda entries (numbered in source order within their containing scope)
    entries.extend(_collect_lambdas(tree, module_name))

    # Generate one question per function entry (matches questions_based prompting style)
    questions = []
    question_to_func = {}  # Map question number to qualified function name
    for i, entry in enumerate(entries, start=1):
        qname = entry["qualified_name"]
        filename = Path(resolved).name
        question_to_func[i] = qname
        if qname == module_name:
            questions.append(f"{i}. What are the module level function calls in {filename}?")
        else:
            questions.append(
                f"{i}. What are the function calls inside '{qname}' in {filename}?"
            )

    # Save mapping for submit_answers to use when parsing numbered string format.
    # Always overwrite so the mapping stays consistent with the question numbers
    # returned in this response (ordering may differ from a pre-existing GT mapping).
    mapping_file = Path(resolved).parent / ".swarmcg_mapping.json"
    with open(mapping_file, "w") as f:
        json.dump({"question_to_func": question_to_func, "module": module_name}, f)

    summary = {
        "module": module_name,
        "note": (
            "Answer each question below using read_file for context, then call submit_answers. "
            "raw_calls shows unresolved call expressions — resolve them to fully qualified names. "
            "Decorator applications appear in module raw_calls. "
            "Lambda entries use <lambdaN> naming in source order within their scope."
        ),
        "questions": questions,
        "functions": entries,
    }
    return json.dumps(summary, indent=2)


def submit_call_graph(call_graph: dict) -> str:
    """
    Validate and accept the final call graph result. This ENDS the agent loop.
    call_graph must be a dict mapping function qualified names (str) to lists of callee names (list[str]).
    """
    if not isinstance(call_graph, dict):
        raise ValueError("call_graph must be a dict")
    for key, value in call_graph.items():
        if not isinstance(key, str):
            raise ValueError(f"Key {key!r} must be a string")
        if not isinstance(value, list):
            raise ValueError(f"Value for key {key!r} must be a list, got {type(value)}")
        for i, callee in enumerate(value):
            if not isinstance(callee, str):
                raise ValueError(f"Callee {i} in key {key!r} must be a string, got {type(callee)}")
    return json.dumps({"status": "accepted", "count": len(call_graph)})


def submit_answers(answers: str, _benchmark_dir: str = None) -> str:
    """
    Submit call graph answers in numbered string format.
    Format: "1. answer1\n2. answer2\n3. answer3"
    Each answer is a comma-separated list of fully qualified callee names.
    Returns JSON with status and the parsed call_graph for the agent to extract.
    """
    if not isinstance(answers, str):
        raise ValueError("answers must be a string with numbered responses")

    # Find the mapping file written by get_call_sites for this benchmark.
    # _benchmark_dir is injected by the agent runner (not exposed to the LLM schema)
    # to avoid picking up a different benchmark's mapping file during parallel execution.
    mapping_file = None
    if _benchmark_dir:
        candidate = Path(_benchmark_dir) / ".swarmcg_mapping.json"
        if candidate.exists():
            mapping_file = candidate

    if mapping_file is None:
        # Fallback: search the benchmark tree (not safe for parallel runs)
        for root, dirs, files in os.walk(ALLOWED_BASE):
            if ".swarmcg_mapping.json" in files:
                mapping_file = Path(root) / ".swarmcg_mapping.json"
                break

    if not mapping_file or not mapping_file.exists():
        raise ValueError(
            "String format requires get_call_sites to be called first. "
            "Mapping file not found."
        )
    
    with open(mapping_file, "r") as f:
        mapping_data = json.load(f)
    question_to_func = {int(k): v for k, v in mapping_data["question_to_func"].items()}
    
    # Parse numbered answers from string
    # Format: "1. answer1\n2. answer2\n3. answer3"
    import re
    answers_dict = {}
    # Match lines like "1. some.function, other.function" or "1." (empty answer)
    pattern = r"^(\d+)\.\s*(.*)$"
    for line in answers.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        match = re.match(pattern, line)
        if match:
            qnum = int(match.group(1))
            answer = match.group(2).strip()
            if qnum in question_to_func:
                answers_dict[question_to_func[qnum]] = answer
            else:
                raise ValueError(f"Question number {qnum} not found in mapping")
    
    # Convert to call graph format
    call_graph = {}
    for func, callees_str in answers_dict.items():
        if callees_str is None:
            callees_str = ""
        call_graph[func] = [c.strip() for c in callees_str.split(",") if c.strip()]
    
    return json.dumps({"status": "accepted", "count": len(call_graph), "call_graph": call_graph})


def _generate_questions_from_gt(callgraph: dict, module_name: str, filename: str) -> dict:
    """Generate a get_call_sites-style summary from a ground truth call graph dict.

    Used in 'ground_truth' questions mode to produce perfect question coverage without
    relying on AST analysis. raw_calls are left empty — the agent reads source files to
    resolve callees.
    """
    func_names = list(callgraph.keys())
    entries = [{"qualified_name": qname, "raw_calls": []} for qname in func_names]
    questions = []
    for i, qname in enumerate(func_names, start=1):
        if qname == module_name:
            questions.append(f"{i}. What are the module level function calls in {filename}?")
        else:
            questions.append(f"{i}. What are the function calls inside '{qname}' in {filename}?")
    return {
        "module": module_name,
        "note": (
            "Answer each question below using read_file for context, then call submit_answers. "
            "These questions were generated from ground truth — all function names are exact."
        ),
        "questions": questions,
        "functions": entries,
    }


def _dispatch_submit_call_graph(args: dict) -> str:
    # Models sometimes pass the call graph dict directly as keyword args instead of
    # wrapping it in {"call_graph": {...}}. Accept both forms.
    if "call_graph" in args:
        return submit_call_graph(args["call_graph"])
    return submit_call_graph(args)


TOOL_DISPATCH = {
    "read_file": lambda args: read_file(**args),
    "list_directory": lambda args: list_directory(**args),
    "get_call_sites": lambda args: get_call_sites(**args),
    "submit_answers": lambda args: submit_answers(args.get("answers", args)),
    "submit_call_graph": _dispatch_submit_call_graph,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the full source of a Python file inside the benchmark directory. "
                "Use this to understand code logic and resolve import/call targets."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file inside the container.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": (
                "List files and subdirectories at the given path. "
                "Use this to discover helper modules imported by main.py."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the directory.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_call_sites",
            "description": (
                "Parse a Python file and return a structured JSON summary of all function "
                "definitions with their raw call sites. Each entry has a 'qualified_name' "
                "(e.g. 'main.func', 'main.MyClass.method', 'main.<lambda1>') and 'raw_calls' "
                "listing call expressions as written in source. Module-level code is listed "
                "under the module name (e.g. 'main'). Decorator applications (@dec) are "
                "included as implicit calls in the enclosing scope's raw_calls. Lambda "
                "expressions are listed as separate entries with '<lambdaN>' names in "
                "document order within their scope. "
                "Use read_file to resolve imports and determine the true qualified callee names."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the Python file.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_answers",
            "description": (
                "Submit your call graph answers in numbered string format. This ENDS the agent loop. "
                "Format: \"1. main.func\\n2. main.helper, <builtin>.print\\n3.\" "
                "where numbers match the question numbers from get_call_sites output. "
                "For each question, provide fully qualified callees as a comma-separated list "
                "(empty if no calls). Every question from get_call_sites must be answered."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "answers": {
                        "type": "string",
                        "description": (
                            "String with numbered answers like '1. main.func\\n2. main.helper\\n3.' "
                            "where numbers match the questions from get_call_sites. "
                            "Each line: '<number>. <comma-separated callees>' or '<number>.' for empty."
                        ),
                    }
                },
                "required": ["answers"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_call_graph",
            "description": (
                "Submit your final call graph result. This ENDS the agent loop. "
                "call_graph must be a JSON object where each key is a fully qualified "
                "function name (e.g. 'main', 'main.func', 'main.MyClass.method') and "
                "each value is a list of fully qualified callee names. "
                "Every function defined in the benchmark must appear as a key. "
                "Use empty list [] for functions that make no calls."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "call_graph": {
                        "type": "object",
                        "description": (
                            "Dict mapping qualified function names to lists of qualified callee names."
                        ),
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    }
                },
                "required": ["call_graph"],
            },
        },
    },
]
