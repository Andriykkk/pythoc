import ast
from enum import Enum

class ExprContext(Enum):
    LOAD = 1
    STORE = 2
    DEL = 3

    def __str__(self):
        return self.name

class BinOperator(Enum):
    ADD = 1
    SUB = 2
    MUL = 3
    MAT_MULT = 4
    DIV = 5
    MOD = 6
    POW = 7
    LSHIFT = 8
    RSHIFT = 9
    BIT_OR = 10
    BIT_XOR = 11
    BIT_AND = 12
    FLOOR_DIV = 13

    def __str__(self):
        return self.name

def getBinOperator(op):
    return {
        ast.Add: BinOperator.ADD,
        ast.Sub: BinOperator.SUB,
        ast.Mult: BinOperator.MUL,
        ast.MatMult: BinOperator.MAT_MULT,
        ast.Div: BinOperator.DIV,
        ast.Mod: BinOperator.MOD,
        ast.Pow: BinOperator.POW,
        ast.LShift: BinOperator.LSHIFT,
        ast.RShift: BinOperator.RSHIFT,
        ast.BitOr: BinOperator.BIT_OR,
        ast.BitXor: BinOperator.BIT_XOR,
        ast.BitAnd: BinOperator.BIT_AND,
        ast.FloorDiv: BinOperator.FLOOR_DIV,
    }.get(type(op), None)

def getExprContext(ctx):
    if isinstance(ctx, ast.Load):
        return ExprContext.LOAD
    if isinstance(ctx, ast.Store):
        return ExprContext.STORE
    if isinstance(ctx, ast.Del):
        return ExprContext.DEL

def traverseExpression(node):
    if isinstance(node, ast.Name):
        return NodeName(node.id, getExprContext(node.ctx))

    if isinstance(node, ast.Tuple):
        return NodeTuple(node.elts)

    if isinstance(node, ast.Constant):
        return NodeConstant(node.value)

    if isinstance(node, ast.BinOp):
        left = traverseExpression(node.left)
        right = traverseExpression(node.right)
        return NodeBinOp(left, node.op, right)

    if isinstance(node, ast.Expr):
        return traverseExpression(node.value)

    if isinstance(node, ast.Call):
        return NodeCall(node.func.id, node.func.ctx, node.args)

    raise NotImplementedError(f"Node type not implemented in traverseExpression: {type(node).__name__}")

def traverseModule(node, indent=0):
    # print("  " * indent + type(node).__name__ + " " + str(node.__dir__()))
    return NodeModule([traverse(child, indent + 1) for child in node.body])

def traverseImport(node, indent=0):
    return NodeImport(node.names)

def traverseImportFrom(node, indent=0):
    return NodeImportFrom(node.module, node.names)

def traverse(node, indent=0):
    try:
        if isinstance(node, ast.Module):
            return traverseModule(node, indent)

        if isinstance(node, ast.Import):
            return traverseImport(node, indent)

        if isinstance(node, ast.ImportFrom):
            return traverseImportFrom(node, indent)

        if isinstance(node, ast.Assign):
            return NodeAssign(node.targets, node.value)

        if isinstance(node, ast.Expr):
            return NodeExpr(node.value)

        raise NotImplementedError(f"Node type not implemented: {type(node).__name__}")           
        
    except Exception as e:
        print(e)
        return

class NodeExpr():
    def __init__(self, expr):
        self.expr = traverseExpression(expr)

    def _repr(self, indent=0, skip_first_indent=False):
        if skip_first_indent:
            return f"Expr(expr={self.expr._repr(indent+1, True)})\n"
        return ("   " * indent) + f"Expr(expr={self.expr._repr(indent+1, True)}" + ("   " * indent) + ")\n"

class NodeAssign():
    def __init__(self, targets, values):
        self.setTargets(targets)

        self.setValue(values)

    def setValue(self, values):
        self.value = traverseExpression(values)

    def setTargets(self, targets):
        targets_list = []
        for target in targets:
            if isinstance(target, ast.Name):
                targets_list.append(NodeName(target.id, getExprContext(target.ctx)))

            if isinstance(target, ast.Tuple):
                targets_list.append(NodeTuple(target.elts))

        self.targets = targets_list

    def _repr(self, indent=0):
        targets_repr = ',\n'.join(("   " * (indent + 1)) + "   " + stmt._repr(1) for stmt in self.targets)
        spaces = ("   " * indent) + "   "
        return ("   " * indent) + f"Assign(\n{spaces}targets=[\n{targets_repr}\n{spaces}],\n{spaces}value={self.value._repr(indent+1, True)}\n" + ("   " * indent) + ")\n"
class NodeModule:
    def __init__(self, body):
        self.body = body

    def _repr(self, indent=0):
        body_repr = ""
        for stmt in self.body:
            if not hasattr(stmt, "_repr"):
                continue
            body_repr += stmt._repr(indent+1)
        return f"Module(\n{body_repr})" 

class NodeImport():
    def __init__(self, module):
        modules = [m.name for m in module]
        self.modules = modules

    def _repr(self, indent=0):
        names = ', '.join(f"'{name}'" for name in self.modules)
        return  ("   " * indent) + f"Import(modules=[{names}])\n"

class NodeImportFrom():
    def __init__(self, module, names):
        names = [m.name for m in names]
        self.module = module
        self.names = names

    def _repr(self, indent=0):
        names = ', '.join(f"'{name}'" for name in self.names)
        return ("   " * indent) + f"ImportFrom(module='{self.module}', names=[{names}])\n"

class NodeTuple():
    def __init__(self, items):
        self.items = [traverseExpression(item) for item in items]

    def _repr(self, indent=0, skip_first_indent=False):
        body_repr = ""
        for stmt in self.items:
            if not hasattr(stmt, "_repr"):
                continue
            body_repr += stmt._repr(indent+3) + ",\n"

        if skip_first_indent:
            return f"Tuple(items=[\n{body_repr}" + ("   " * (indent+2)) + "])"
        return ("   " * (indent - 1)) + f"Tuple(items=[\n{body_repr}" + ("   " * (indent+2)) + "])"

class NodeName():
    def __init__(self, name, ctx):
        self.name = name
        self.ctx = ctx

    def _repr(self, indent=0, skip_first_indent=False):
        if skip_first_indent:
            return f"Name(name='{self.name}', ctx={self.ctx})"
        return ("   " * indent) + f"Name(name='{self.name}', ctx={self.ctx})"

class NodeBinOp():
    def __init__(self, left, op, right):
        self.left = left
        self.op = getBinOperator(op)
        self.right = right

    def _repr(self, indent=0, skip_first_indent=False):
        if skip_first_indent:
            return "BinOp(\n" + ("   " * (indent + 1)) + f"left={self.left._repr(indent+1, True)},\n" + ("   " * (indent + 1)) + f"op={self.op},\n" + ("   " * (indent + 1)) + f"right={self.right._repr(indent+1, True)}\n" + ("   " * indent) + ")"
        return "BinOp(\n" + ("   " * (indent + 1)) + f"left={self.left._repr(indent+1, True)},\n" + ("   " * (indent + 1)) + f"op={self.op},\n" + ("   " * (indent + 1)) + f"right={self.right._repr(indent+1, True)}\n" + ("   " * indent) + ")"

class NodeConstant():
    def __init__(self, value):
        self.value = value

    def _repr(self, indent=0, skip_first_indent=False):
        if skip_first_indent:
            return f"Constant(value={self.value})"
        return "  " * indent + f"Constant(value={self.value})"

class NodeCall():
    def __init__(self, func_id, ctx, args):
        self.func_id = func_id
        self.ctx = getExprContext(ctx)
        self.args = [traverseExpression(arg) for arg in args]

    def _repr(self, indent=0, skip_first_indent=False):
        body_args = "[\n"
        for arg in self.args:
            if not hasattr(arg, "_repr"):
                continue
            body_args += arg._repr(indent+2) + ",\n"
        body_args += ("   " * (indent + 1)) + "]"

        if skip_first_indent:
            return f"Call(\n" + ("   " * (indent + 1)) + f"func_id='{self.func_id}',\n" + ("   " * (indent + 1)) + f"ctx={self.ctx},\n" + ("   " * (indent + 1)) + f"args={body_args}" + ")\n"
        return "  " * indent + f"Call(\n" + ("   " * (indent + 1)) + f"func_id='{self.func_id}',\n" + ("   " * (indent + 1)) + f"ctx={self.ctx},\n" + ("   " * (indent + 1)) + f"args={body_args} \n" + ("   " * indent) + ")\n"
