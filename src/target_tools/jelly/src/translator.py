import logging
import os
import esprima
from collections import defaultdict

logger = logging.getLogger("jelly_runner")


def generate_ast_from_js_file(file_path):
    """
    Generates the AST of the given JavaScript file using Esprima.

    Args:
    - file_path (str): The path to the JavaScript file.

    Returns:
    - ast (dict): The generated AST as a dictionary.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as js_file:
            js_code = js_file.read()
        ast = esprima.parseScript(js_code, {"tolerant": True, "loc": True})
        return ast
    except Exception as e:
        print(f"An error occurred generating AST: {e}")
        return None


def parse_func_name_from_ast(ast, start_line, arrow_fun_count=0):
    function_name = None
    try:
        if ast:
            if ast.body:
                for node in ast.body:
                    if isinstance(node, esprima.nodes.FunctionDeclaration):
                        function_name = node.id.name
                        node_start = node.id.loc.start.line
                        if int(node_start) == int(start_line):
                            return function_name
                        if isinstance(node.body, esprima.nodes.BlockStatement):
                            for stmt in node.body.body:
                                if isinstance(stmt, esprima.nodes.ReturnStatement):
                                    if isinstance(
                                        stmt.argument,
                                        esprima.nodes.ArrowFunctionExpression,
                                    ):
                                        function_name = f"<arrow{arrow_fun_count+1}>"
                                        arrow_function_start_line = (
                                            stmt.argument.loc.start.line
                                        )
                                        if int(arrow_function_start_line) == int(
                                            start_line
                                        ):
                                            return function_name
                    elif isinstance(node, esprima.nodes.FunctionExpression):
                        function_name = node.id.name
                        node_start = node.id.loc.start.line
                        if int(node_start) == int(start_line):
                            return function_name
                    elif isinstance(node, esprima.nodes.ClassDeclaration):
                        # If it's a class, look for methods (MethodDefinition)
                        class_name = node.id.name
                        class_start_line = node.loc.start.line
                        if int(class_start_line) == int(start_line):
                            function_name = f"{class_name}.constructor"
                            return function_name
                        for method in node.body.body:
                            if isinstance(method, esprima.nodes.MethodDefinition):
                                method_name = method.key.name
                                method_start = method.key.loc.start.line
                                if int(method_start) == int(start_line):
                                    function_name = f"{class_name}.{method_name}"
                                    return function_name
                                if isinstance(
                                    method.value, esprima.nodes.FunctionExpression
                                ):
                                    if isinstance(
                                        method.value.body, esprima.nodes.BlockStatement
                                    ):
                                        for stmt in method.value.body.body:
                                            if isinstance(
                                                stmt, esprima.nodes.VariableDeclaration
                                            ):
                                                for decl in stmt.declarations:
                                                    if isinstance(
                                                        decl.init,
                                                        esprima.nodes.ArrowFunctionExpression,
                                                    ):
                                                        variable_name = decl.id.name
                                                        arrow_function_start_line = (
                                                            decl.init.loc.start.line
                                                        )
                                                        if int(
                                                            arrow_function_start_line
                                                        ) == int(start_line):
                                                            function_name = f"{class_name}.{method_name}.{variable_name}"
                                                            return function_name
                    elif isinstance(node, esprima.nodes.ExportNamedDeclaration):
                        if isinstance(
                            node.declaration, esprima.nodes.FunctionDeclaration
                        ):
                            function_name = node.declaration.id.name
                            node_start = node.declaration.id.loc.start.line
                            if int(node_start) == int(start_line):
                                return function_name
                        elif isinstance(
                            node.declaration, esprima.nodes.ClassDeclaration
                        ):
                            class_name = node.declaration.id.name
                            class_start_line = node.declaration.id.loc.start.line
                            if int(class_start_line) == int(start_line):
                                function_name = f"{class_name}.constructor"
                                return function_name
                            for method in node.declaration.body.body:
                                if isinstance(method, esprima.nodes.MethodDefinition):
                                    method_name = method.key.name
                                    method_start = method.key.loc.start.line
                                    if int(method_start) == int(start_line):
                                        function_name = f"{class_name}.{method_name}"
                                        return function_name
                    elif isinstance(node, esprima.nodes.VariableDeclaration):
                        for decl in node.declarations:
                            if isinstance(decl.init, esprima.nodes.CallExpression):
                                if isinstance(
                                    decl.init.callee, esprima.nodes.MemberExpression
                                ):
                                    # It's a method call like Array.from or filter
                                    member_start = decl.init.callee.loc.start.line
                                    if int(member_start) == int(start_line):
                                        if isinstance(
                                            decl.init.callee.object.callee,
                                            esprima.nodes.MemberExpression,
                                        ):
                                            function_name = f"{decl.init.callee.object.callee.object.name}.{decl.init.callee.object.callee.property.name}"
                                            return function_name
                            elif isinstance(
                                decl.init, esprima.nodes.ArrowFunctionExpression
                            ):
                                function_name = f"<arrow{arrow_fun_count+1}>"
                                node_start = decl.id.loc.start.line
                                if int(node_start) == int(start_line):
                                    return function_name
                    elif isinstance(node, esprima.nodes.ExpressionStatement):
                        if isinstance(node.expression, esprima.nodes.CallExpression):
                            # Arrow function as an argument
                            for arg in node.expression.arguments:
                                if isinstance(
                                    arg, esprima.nodes.ArrowFunctionExpression
                                ):
                                    function_name = f"<arrow{arrow_fun_count+1}>"
                                    arrow_function_start_line = arg.loc.start.line
                                    if int(arrow_function_start_line) == int(
                                        start_line
                                    ):
                                        return function_name
    except Exception:
        raise


def convert_jelly_to_swarm(test_folder, jelly_json):
    """
    :param test_folder: Current test folder.
    :param jelly_json: Jelly generated cg json.
    :return: Swarm format json.
    """
    try:
        swarm_json = defaultdict(list)

        files = jelly_json.get("files", [])
        functions = jelly_json.get("functions", {})
        fun2fun = jelly_json.get("fun2fun", [])
        arrow_fun_count = 0

        # 1. Generate ASTs for all files
        ast_cache = {
            file_path: generate_ast_from_js_file(os.path.join(test_folder, file_path))
            for file_path in files
        }

        # 2. Map function IDs to SWARM format function names
        function_names = {}
        for func_id, location in functions.items():
            file_index, start_line, col_start, end_line, col_end = map(
                int, location.split(":")
            )
            file_path = files[file_index]
            file_name = os.path.splitext(file_path.replace(os.sep, "."))[0]

            # Check for the module-level function (eg. main, to_import)
            ast = ast_cache.get(file_path)
            function_name = None
            if isinstance(ast, esprima.nodes.Script) and ast.loc and ast.body:
                if (
                    int(start_line) == ast.loc.start.line
                    and int(end_line) == ast.loc.end.line
                    and int(col_start) == int(ast.loc.start.column) + 1
                    and int(col_end) == int(ast.loc.end.column) + 1
                ):
                    function_name = file_name
                else:
                    function_name = parse_func_name_from_ast(
                        ast, start_line, arrow_fun_count
                    )
                    function_name = (
                        f"{file_name}.{function_name}"
                        if function_name
                        else f"{file_name}.AnonymousFunction"
                    )
                if function_name and "arrow" in function_name:
                    arrow_fun_count += 1
            function_names[func_id] = function_name

        # Step 3: Build the SWARM format json
        swarm_json = {name: [] for name in function_names.values() if name is not None}

        # Step 4: Add caller-callee relationships
        for caller_id, callee_id in fun2fun:
            caller_name = function_names.get(str(caller_id))
            callee_name = function_names.get(str(callee_id))
            if caller_name and callee_name:
                swarm_json[caller_name].append(callee_name)

        # Step 5: Verify module-level keys are listed
        for file_path in files:
            file_name = os.path.splitext(file_path.replace(os.sep, "."))[0]
            if file_name not in swarm_json:
                swarm_json[file_name] = []
        return swarm_json
    except Exception as e:
        print(
            f"An error occurred during translation from Jelly to SWARM in test folder {test_folder}: {e}"
        )
        return {}
