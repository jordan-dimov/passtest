import io
import subprocess
import unittest
from contextlib import redirect_stdout

import typer

from src.gpt_utils import ChatMem, gpt_chat

app = typer.Typer()


def load_tests_and_signature(file_path: str):
    with open(file_path) as f:
        code = f.read()

    # Assume that the first line is the commented-out function signature
    # and the rest of the code contains the unit tests.

    code_lines = code.splitlines()
    # Extract the function signature

    test_signature = code_lines[0].lstrip("#").strip()

    # Extract the unit tests
    test_code = "\n".join(code_lines[1:])

    return test_signature, test_code


def run_pytest_and_process_results(test_module: str):
    # Run Pytest tests and capture the output
    # Parse the output to determine if any tests failed
    # Return test status and failed tests info

    passed_tests = True

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=".", pattern=f"{test_module}.py")
    test_runner = unittest.TextTestRunner(stream=io.StringIO(), verbosity=2)

    with redirect_stdout(io.StringIO()) as output:
        result = test_runner.run(suite)

    # Parse Pytest output to check for errors or failures
    failed_tests = {}

    if result.failures or result.errors:
        passed_tests = False
        for failure, traceback_text in result.failures + result.errors:
            test_name = f"{failure.__class__.__name__}.{failure._testMethodName}"
            failed_tests[test_name] = traceback_text

    return passed_tests, failed_tests


@app.command()
def main(file_path: str, max_iterations: int = 3):
    system_msg = "Act as an experienced Python developer and implement a function that passes the provided tests. Use clean, modern and Pythonic code optimised for Python 3.10 or newer. Do your best to use only built-in Python functionality or imports from Python's Standard Library if needed. IMPORTANT: Output ONLY the implementation of the function, including the function signature but NO other text."
    mem = ChatMem(system_msg=system_msg)

    test_signature, pytest_code = load_tests_and_signature(file_path)

    iteration_count = 0
    all_tests_passed = False
    failed_tests_info = ""

    test_module = file_path.split("/")[-1].replace(".py", "")

    while (not all_tests_passed) and (iteration_count < max_iterations):
        iteration_count += 1

        prompt = f"Implement a concise Python 3.10 function {test_signature} which passes the following tests: \n\n {pytest_code}"
        if iteration_count > 1:
            prompt = (
                f" Here are the failed test cases of the previous attempt. Make sure to fix these: {failed_tests_info}"
            )

        with open("convo.log", "a") as lf:
            mem.add("user", prompt)
            lf.write(prompt + "\n\n")

        implementation = gpt_chat(mem.get())

        typer.echo(implementation)

        with open("implementation.py", "w") as f:
            f.write(implementation + "\n")

        passed_tests, failed_tests_info = run_pytest_and_process_results(test_module)

        if passed_tests:
            all_tests_passed = True
        else:
            typer.echo(f"Failed tests: {failed_tests_info}\n")

    if all_tests_passed:
        typer.echo(f"The AI-generated implementation passed all tests (in {iteration_count} iterations)")
        typer.echo("Formatting the implementation code...")
        subprocess.run(["ruff", "format", "implementation.py"], check=False)

        typer.echo("Linting the implementation code...")
        subprocess.run(["ruff", "--fix", "implementation.py"], check=False)
    else:
        typer.echo("Max iterations reached without passing all tests: ")
        typer.echo(failed_tests_info)


if __name__ == "__main__":
    app()
