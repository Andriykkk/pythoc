import argparse
from enum import Enum
import ast
import subprocess
import os
from reader import parse_source, read_arguments

class IRNode: pass

class TypeKind(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "str"
    UNKNOWN = "unknown"

class ExprContext(Enum):
    LOAD = "load"
    STORE = "store"
    DEL = "del"

class IRConstant(IRNode):
    def __init__(self, value):
        self.value = value
        self.type = self.infer_type(value)

    def infer_type(self, value):
        if isinstance(value, int):
            return TypeKind.INT
        elif isinstance(value, float):
            return TypeKind.FLOAT
        elif isinstance(value, str):
            return TypeKind.STRING
        return TypeKind.UNKNOWN

    def __repr__(self):
        return f"Const({self.value}:{self.type.value})"


class IRVariable(IRNode):
    def __init__(self, name, var_type=TypeKind.UNKNOWN):
        self.name = name
        self.type = var_type

    def __repr__(self):
        return f"Var({self.name}:{self.type.value})"


class IRAssign(IRNode):
    def __init__(self, target: IRVariable, value: IRNode):
        self.target = target
        self.value = value

    def __repr__(self):
        return f"{self.target} = {self.value}"


class IRBinOp(IRNode):
    def __init__(self, left, op, right, result_type):
        self.left = left
        self.op = op
        self.right = right
        self.type = result_type

    def __repr__(self):
        return f"({self.left} {self.op} {self.right}) : {self.type.value}"


class IRCall(IRNode):
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __repr__(self):
        args_str = ", ".join(repr(a) for a in self.args)
        return f"Call({self.func}, [{args_str}])"
    
class ASTParser:
    def __init__(self, ast_root):
        self.ast_root = ast_root
        self.env = {}  

    def parse_ast(self):
        return [self.parse_node(node) for node in self.ast_root.body]
 
    def parse_node(self, node):
        if isinstance(node, ast.Assign):
            target = node.targets[0]
            var_name = target.id
            value_ir = self.parse_expr(node.value)
            var = IRVariable(var_name, value_ir.type)
            self.env[var_name] = var.type
            return IRAssign(var, value_ir)
        elif isinstance(node, ast.Expr):
            return self.parse_expr(node.value)
        else:
            raise NotImplementedError(f"Unsupported node: {type(node)}")
        
    def parse_expr(self, node):
        if isinstance(node, ast.Constant):
            return IRConstant(node.value)
        
        elif isinstance(node, ast.Name):
            var_name = node.id
            var_type = self.env.get(var_name, TypeKind.UNKNOWN)
            return IRVariable(var_name, var_type)
        
        elif isinstance(node, ast.BinOp):
            left = self.parse_expr(node.left)
            right = self.parse_expr(node.right)

            result_type = self.infer_binop_type(left.type, right.type)
            self.type_check(left, right, node.op)

            return IRBinOp(left, self.op_to_str(node.op), right, result_type)
        
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            args = [self.parse_expr(arg) for arg in node.args]
            return IRCall(func_name, args)
        else:
            raise NotImplementedError(f"Unsupported expr: {type(node)}")
        
    def infer_binop_type(self, left_type, right_type):
        if left_type == right_type:
            return left_type
        
        if left_type == TypeKind.INT and right_type == TypeKind.FLOAT or left_type == TypeKind.FLOAT and right_type == TypeKind.INT:
            return TypeKind.FLOAT
        
        return TypeKind.UNKNOWN
    
    def op_to_str(self, op):
        return {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Mod: "%",
            ast.Pow: "**",
            ast.LShift: "<<",
            ast.RShift: ">>",
            ast.FloorDiv: "//",
            ast.BitOr: "|",
            ast.BitAnd: "&",
            ast.BitXor: "^",
        }.get(type(op), "?")
    
    def type_check(self, left, right, op):
        if left.type == TypeKind.STRING and right.type == TypeKind.STRING:
            return
        
        if TypeKind.STRING in (left.type, right.type) and (left.type == TypeKind.INT or right.type == TypeKind.INT) and isinstance(op, ast.Mult):
            return

        if TypeKind.STRING in (left.type, right.type) and left.type != right.type:
            raise TypeError(f"Cannot perform {self.op_to_str(op)} on strings")
        
    def print_ir(self, node):
        return repr(node)
    
def typeking_to_rust_type(type_kind):
    return {
        TypeKind.INT: "BigInt",
        TypeKind.FLOAT: "f64",
        TypeKind.STRING: "String",
        TypeKind.UNKNOWN: "unknown",
    }.get(type_kind, "unknown")

class IRCompiler:
    def __init__(self, ir_tree):
        self.ir_tree = ir_tree
        self.libraries = {}
        self.code_lines = []

        self.flags = {
            'int': False,
            'cast_to_float': False 
        }

    def compile(self):
        for node in self.ir_tree:
            self.emit_node(node)

    def generate_rust(self):
        code = ""

        if self.flags['int']:
            code += """use num_bigint::BigInt;\n"""
        if self.flags['cast_to_float']:
            code += """use num_traits::cast::ToPrimitive;\n"""
            
        code += "fn main() {\n"

        code += "\n".join(self.code_lines)

        code += "\n}\n"

        self.rust = code

    def create_rust_file(self, logs=True):
        file_path = "pythoc/src/main.rs"

        if os.path.exists(file_path):
            logs and print(f"File '{file_path}' exists. Deleting...")
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error deleting file '{file_path}': {e}")
        
        logs and print(f"Creating file '{file_path}'...")
        try:
            with open(file_path, 'w') as file:
                file.write(self.rust)
            logs and print(f"Successfully wrote to file '{file_path}'.")
        except IOError as e:
            print(f"Error creating or writing to file '{file_path}': {e}")

    def add_test(self, code):
        self.code_lines.append(code)

    def emit_node(self, node):
        if isinstance(node, IRAssign):
            code = self.emit_assign(node)
            self.code_lines.append(code)
        
        elif isinstance(node, IRBinOp):
            cose = self.emit_call(node)
            self.code_lines.append(code)

    def emit_assign(self, node: IRAssign):
        name = node.target.name

        expr_type = node.value.type
        expr_code = self.emit_expr(node.value)

        division_type = self.check_for_division_type(node.value)

        if division_type is not None:
            self.flags['cast_to_float'] = True
            expr_type = division_type

        return f"let {name}: {typeking_to_rust_type(expr_type)} = {expr_code};"

    def check_for_division_type(self, node):
        if isinstance(node, IRBinOp):
            if node.op == '/' and node.left.type == TypeKind.INT and node.right.type == TypeKind.INT:
                return TypeKind.FLOAT

        return None

    def emit_expr(self, node: IRNode, type=None):
        if isinstance(node, IRConstant):
            if node.type == TypeKind.INT:
                self.flags['int'] = True
                return f"BigInt::from({str(node.value)})"
            elif node.type == TypeKind.FLOAT:
                return f"{node.value} as f64"
            elif node.type == TypeKind.STRING:
                return f'"{node.value}"'
        elif isinstance(node, IRVariable):
            if node.type == TypeKind.INT:
                return f"{node.name}"
            elif node.type == TypeKind.FLOAT:
                return f"{node.name}"
        elif isinstance(node, IRBinOp):
            left = self.emit_expr(node.left)
            right = self.emit_expr(node.right)

            if node.op in ["+", "-", "*", "/"]:
                if node.left.type == TypeKind.FLOAT and node.right.type == TypeKind.INT:
                    right = f"({right}).to_f64().unwrap()"
                    self.flags['cast_to_float'] = True
                if node.left.type == TypeKind.INT and node.right.type == TypeKind.FLOAT:
                    left = f"({left}).to_f64().unwrap()"
                    self.flags['cast_to_float'] = True

                if node.op == "/":
                    if node.left.type == TypeKind.INT and node.right.type == TypeKind.INT:
                        left = f"({left}).to_f64().unwrap()"
                        right = f"({right}).to_f64().unwrap()"
                        self.flags['cast_to_float'] = True

                return f"{left} {node.op} {right}"
            elif node.op in ["<<", ">>"]:
                self.flags['cast_to_float'] = True
                if node.left.type == TypeKind.INT and node.right.type == TypeKind.INT:
                    right = f"({right}).to_u32().unwrap()"
                    
                elif node.left.type == TypeKind.FLOAT or node.right.type == TypeKind.FLOAT:
                    raise TypeError(f"Cannot perform {node.op} on floats")
                
                return f"{left} {node.op} {right}"
            elif node.op in ["**"]:
                self.flags['cast_to_float'] = True
                if node.left.type == TypeKind.INT and node.right.type == TypeKind.INT:
                    return f"({left}).pow({right}.to_u32().unwrap())"
                elif node.left.type == TypeKind.FLOAT or node.right.type == TypeKind.FLOAT:
                    if node.left.type == TypeKind.INT:
                        left = f"({left}).to_f64().unwrap()"
                    elif node.left.type == TypeKind.FLOAT:
                        left = f"({left})"

                    if node.right.type == TypeKind.INT:
                        right = f"({right}).to_f64().unwrap()"
                    elif node.right.type == TypeKind.FLOAT:
                        right = f"({right})"

                    return f"{left}.powf({right})"
                
            elif node.op in ["|", "^", "&"]:
                if node.left.type == TypeKind.FLOAT and node.right.type == TypeKind.FLOAT:
                    raise TypeError(f"Cannot perform {node.op} on floats")
                return f"&({left}) {node.op} &({right})"
        
        elif isinstance(node, IRCall):
            args = [self.emit_expr(arg) for arg in node.args]
            return f"{node.func}({', '.join(args)})"
        else:
            raise NotImplementedError(f"Unsupported expr: {type(node)}")

class IRRunner:
    def __init__(self, cargo_path="pythoc"):
        self.cargo_path = cargo_path

    def build_rust_code(self, logs=True, errors=True):
        """
        Builds the Rust code using Cargo.
        """
        try:
            command = ["cargo", "build", "--manifest-path", os.path.join(self.cargo_path, "Cargo.toml")]

            process = subprocess.Popen(command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            logs and print(f"Build Output:\n{stdout.decode()}")
            if stderr:
                errors and print(f"Build Errors:\n{stderr.decode()}")

            if process.returncode != 0:
                raise Exception(f"Cargo build failed with exit code {process.returncode}")
            logs and  print("Rust code built successfully!")
        except Exception as e:
            errors and print(f"Error building Rust code: {e}")
            raise

    def run_rust_code(self, return_output=False, logs=True):
        """
        Runs the built Rust executable.
        """
        try:
            executable_path = os.path.join(self.cargo_path, "target", "debug", "pythoc")
            if not os.path.exists(executable_path):
                executable_path = os.path.join(self.cargo_path, "target", "release", "pythoc")
            command = [executable_path]

            process = subprocess.Popen(command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            logs and print(f"Program Output:\n{stdout.decode()}")
            if stderr:
                print(f"Program Errors:\n{stderr.decode()}")

            if process.returncode != 0:
                raise Exception(f"Program execution failed with exit code {process.returncode}")

            if return_output:
                return stdout.decode()
        except FileNotFoundError:
            print(f"Error: Executable not found at {executable_path}.  Make sure you have built the Rust code.")
            raise
        except Exception as e:
            print(f"Error running Rust code: {e}")
            raise


def main():
    args = read_arguments()

    ast_tree = parse_source(args.filename)
    # print(ast.dump(ast_tree, indent=4))

    parser = ASTParser(ast_tree)
    ir_tree = parser.parse_ast()
    # for node in ir_tree:
    #     print(parser.print_ir(node))
    
    compiler = IRCompiler(ir_tree)
    compiler.compile()
    compiler.add_test('println!("{}", y);')
    compiler.generate_rust()
    # print("###",compiler.rust)
    compiler.create_rust_file()

    runner = IRRunner() 
    runner.build_rust_code()
    runner.run_rust_code()

if __name__ == "__main__":
    main()
 