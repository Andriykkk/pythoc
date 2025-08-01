import unittest
import subprocess
import os, re

class PythocTestCase(unittest.TestCase):
    def assertOutputsMatch(self, test_file_path):
        """
        Runs a test file with both standard Python and the pythoc compiler,
        and asserts that their outputs are identical.
        """
        # 1. Run with standard Python interpreter
        python_result = subprocess.run(
            ['python3', test_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        expected_output = python_result.stdout.strip()

        # 2. Run with pythoc compiler
        # The main script is in the parent directory's `src` folder.
        main_script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'main.py')
        
        # We need to capture the output of the *compiled executable*, not the compiler itself.
        # The current main.py prints a lot of stuff. I will assume for now that the
        # compiled executable's output is the only thing on stdout.
        pythoc_result = subprocess.run(
            ['python3', main_script_path, test_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # The output from the compiler script itself is captured here.
        # If the compiled program's output is also printed to stdout by the script,
        # we need to parse it.
        # For now, let's assume the last line is the program's output.
        # This is brittle and depends on the main.py script's behavior.
        
        # A better approach would be for main.py to *not* print the program's output,
        # but for the buildNrun.sh script to do so.
        # Let's stick to the current plan and adjust if it fails.
        actual_lines = pythoc_result.stdout.strip().splitlines()

        cleaned_lines = [line for line in actual_lines if not re.match(r'^Namespace\(', line)]

        actual_output = '\n'.join(cleaned_lines).strip()

        self.assertEqual(expected_output.strip(), actual_output.strip())

class TestSimpleCases(PythocTestCase):
    def test_simple_addition(self):
        test_file = os.path.join(os.path.dirname(__file__), './scripts/test_addition.py')
        self.assertOutputsMatch(test_file)

if __name__ == '__main__':
    unittest.main()
