import argparse
from enum import Enum
import ast
import subprocess
import os
from reader import read_arguments, parse_source
from nodes import *

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

def main():
    args = read_arguments()

    ast_tree = parse_source(args.filename)

    tree = traverse(ast_tree)
    
    print(ast.dump(ast_tree, indent=4))
    print(tree._repr())
 
if __name__ == "__main__":
    main()