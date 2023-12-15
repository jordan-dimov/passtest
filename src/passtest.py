import os
import subprocess

import pytest
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
    # Remove any junit.xml file that may exist from a previous run
    try:
        os.remove("junit.xml")
    except FileNotFoundError:
        pass
    return pytest.main(["-qq", "--tb=short", "--junit-xml", "junit.xml", test_module + ".py"])


@app.command()
def main(file_path: str, max_iterations: int = 3):
    system_msg = "Act as an experienced Python developer and implement a function that passes the provided tests. Use clean, modern and Pythonic code optimised for Python 3.10 or newer. Do your best to use only built-in Python functionality or imports from Python's Standard Library if needed - but make sure to include any required imports. Keep the function signature as close as possible to the one in the request. Try to keep code clean and minimal.  IMPORTANT: Output ONLY the implementation of the function, including the function signature but NO other text."
    mem = ChatMem(system_msg=system_msg)

    test_signature, pytest_code = load_tests_and_signature(file_path)

    iteration_count = 0
    all_tests_passed = False

    test_module = file_path.split("/")[-1].replace(".py", "")

    while (not all_tests_passed) and (iteration_count < max_iterations):
        iteration_count += 1

        prompt = f"Implement a concise Python 3.10 function {test_signature} which passes the following tests: \n\n {pytest_code}"
        if iteration_count > 1:
            # load the entire junit.xml file
            with open("junit.xml") as f:
                junit_xml = f.read()
            prompt = f" Here is the junit XML of the previous failed run. Make sure all errors are fixed: {junit_xml}"

        with open("convo.log", "a") as lf:
            mem.add("user", prompt)
            lf.write(prompt + "\n\n")

        implementation = gpt_chat(mem.get())

        typer.echo(implementation)

        with open("implementation.py", "w") as f:
            f.write(implementation + "\n")

        exit_code = run_pytest_and_process_results(test_module)

        if not exit_code:
            all_tests_passed = True
        else:
            typer.echo("Failed tests logged in junit.xml")

    if all_tests_passed:
        typer.echo(f"The AI-generated implementation passed all tests (in {iteration_count} iterations)")
        typer.echo("Formatting the implementation code...")
        subprocess.run(["ruff", "format", "implementation.py"], check=False)

        typer.echo("Linting the implementation code...")
        subprocess.run(["ruff", "--fix", "implementation.py"], check=False)
    else:
        typer.echo("Max iterations reached without passing all tests. See junit.xml. ")


if __name__ == "__main__":
    app()
