from traverser import BinOperator, NodeAssign, NodeBinOp, NodeCall, NodeConstant, NodeExpr, NodeModule, NodeName

class Compiler:
    def __init__(self):
        self.code = []
        self.variables = set()

    def compile(self, node):
        self.visit(node)
        return self.generate_cpp_code()

    def generate_cpp_code(self):
        main_code = "\n".join(self.code)
        return f"""#include "pyclib.h"

int main() {{
{main_code}
    return 0;
}}
"""

    def visit(self, node):
        if isinstance(node, NodeModule):
            return self.visit_Module(node)
        elif isinstance(node, NodeAssign):
            return self.visit_Assign(node)
        elif isinstance(node, NodeConstant):
            return self.visit_Constant(node)
        elif isinstance(node, NodeName):
            return self.visit_Name(node)
        elif isinstance(node, NodeBinOp):
            return self.visit_BinOp(node)
        elif isinstance(node, NodeExpr):
            return self.visit_Expr(node)
        elif isinstance(node, NodeCall):
            return self.visit_Call(node)
        else:
            raise NotImplementedError(f"Unsupported node type: {type(node)}")

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise NotImplementedError("Only single assignment is supported")
        
        target = node.targets[0]
        if not isinstance(target, NodeName):
            raise NotImplementedError("Only assignment to variables is supported")

        var_name = target.name
        if var_name not in self.variables:
            self.variables.add(var_name)
            self.code.append(f"    PyObject {var_name} = {self.visit(node.value)};")
        else:
            self.code.append(f"    {var_name} = {self.visit(node.value)};")

    def visit_Constant(self, node):
        if isinstance(node.value, int):
            return f"PyObject::from_int({node.value})"
        elif isinstance(node.value, float):
            return f"PyObject::from_float({node.value})"
        elif isinstance(node.value, str):
            return f'PyObject::from_string("{node.value}")'
        elif isinstance(node.value, bool):
            return f"PyObject::from_bool({'true' if node.value else 'false'})"
        else:
            raise NotImplementedError(f"Unsupported constant type: {type(node.value)}")

    def visit_Name(self, node):
        return node.name

    def visit_BinOp(self, node):
        op_map = {
            BinOperator.ADD: "py_add",
            BinOperator.MUL: "py_mul",
        }
        if node.op not in op_map:
            raise NotImplementedError(f"Unsupported binary operator: {node.op}")

        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"{op_map[node.op]}({left}, {right})"

    def visit_Expr(self, node):
        self.code.append(f"    {self.visit(node.expr)};")

    def visit_Call(self, node):
        if node.func_id == 'print':
            if len(node.args) != 1:
                raise NotImplementedError("print() takes exactly one argument")
            arg = self.visit(node.args[0])
            return f"py_print({arg}); \n std::cout << \"\\n\";"
        else:
            raise NotImplementedError(f"Unsupported function call: {node.func_id}")

def compile_to_cpp(tree):
    compiler = Compiler()
    return compiler.compile(tree)
