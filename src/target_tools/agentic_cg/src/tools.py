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
    """Flatten an attribute chain (e.g. a.b.c) into a dotted string.

    For chained calls like `a()()`, the outer Call has a Call as its func.
    Returns a `<return_of:X>` sentinel so the LLM knows the return value of X
    is also being invoked and needs to be traced.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value = _get_attribute_chain(node.value)
        return f"{value}.{node.attr}" if value else node.attr
    if isinstance(node, ast.Call):
        inner = _get_attribute_chain(node.func)
        return f"<return_of:{inner}>" if inner else "<return_of:unknown>"
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
    for i, entry in enumerate(entries, start=1):
        qname = entry["qualified_name"]
        filename = Path(resolved).name
        if qname == module_name:
            questions.append(f"{i}. What are the module level function calls in {filename}?")
        else:
            questions.append(
                f"{i}. What are the function calls inside '{qname}' in {filename}?"
            )

    summary = {
        "module": module_name,
        "note": (
            "Answer each question below using read_file for context, then call submit_answers. "
            "raw_calls shows unresolved call expressions — resolve them to fully qualified names. "
            "Decorator applications appear in module raw_calls. "
            "Lambda entries use <lambdaN> naming in source order within their scope. "
            "<return_of:X> in raw_calls means the return value of X is also being called — "
            "trace what X returns and include that as an additional callee."
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


def submit_answers(answers: dict) -> str:
    """
    Submit call graph answers in question-based format.
    answers: dict mapping qualified function names to comma-separated callee strings.
    E.g. {"main": "main.A, main.B", "main.A": "main.helper", "main.B": ""}
    Returns JSON with status and the parsed call_graph for the agent to extract.
    """
    if not isinstance(answers, dict):
        raise ValueError("answers must be a dict")
    call_graph = {}
    for func, callees_str in answers.items():
        if not isinstance(func, str):
            raise ValueError(f"Key {func!r} must be a string")
        if callees_str is None:
            callees_str = ""
        if not isinstance(callees_str, str):
            raise ValueError(f"Answer for {func!r} must be a string, got {type(callees_str)}")
        call_graph[func] = [c.strip() for c in callees_str.split(",") if c.strip()]
    return json.dumps({"status": "accepted", "count": len(call_graph), "call_graph": call_graph})


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
                "document order within their scope. Chained calls like a()() appear as "
                "'<return_of:a>' — a hint to trace the return value of a. "
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
                "Submit your call graph answers in question-based format. This ENDS the agent loop. "
                "For each function returned by get_call_sites, provide the fully qualified callees "
                "as a comma-separated string (empty string if no calls). "
                "Keys are the qualified function names (e.g. 'main', 'main.func', 'main.MyClass.method'). "
                "Values are comma-separated callee strings (e.g. 'main.helper, <builtin>.print'). "
                "Every function from get_call_sites must appear as a key."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "answers": {
                        "type": "object",
                        "description": (
                            "Dict mapping qualified function names to comma-separated callee strings. "
                            "Example: {\"main\": \"main.func\", \"main.func\": \"main.helper, <builtin>.print\", \"main.helper\": \"\"}"
                        ),
                        "additionalProperties": {"type": "string"},
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
