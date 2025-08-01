import argparse
import ast
import os

def parse_source(source_code: str):
    try:
        with open(source_code, "r") as file:
            tree = ast.parse(file.read(), mode="exec")

            return tree
    except SyntaxError as e:
        raise e
    except Exception as e:
        raise e

def check_source_file(file_path: str):
    if file_path.endswith(".py") and os.path.isfile(file_path):
        return file_path
    elif os.path.isfile(file_path + ".py"):
        return file_path + ".py"

    script_dir = os.path.dirname(__file__)
    candidate = os.path.join(script_dir, file_path)
    if candidate.endswith(".py") and os.path.isfile(candidate):
        return candidate
    elif os.path.isfile(candidate + ".py"):
        return candidate + ".py"

    return None

def read_arguments():
    parser = argparse.ArgumentParser(
        description="Process a file name provided either as a positional argument or with -f/--file."
    )

    parser.add_argument("filename", nargs="?", help="Name of the file")
    parser.add_argument("-f", "--file", dest="file_arg",
                        help="Name of the file (alternative to positional)")

    args = parser.parse_args()
    file_name = args.filename or args.file_arg
    if not file_name:
        print("Error: No file name provided.")
        return
    
    resolved_file = check_source_file(file_name)
    if not resolved_file:
        raise FileNotFoundError(f"File {file_name} does not exist or is not a Python file.")

    args.filename = resolved_file
    
    return args 