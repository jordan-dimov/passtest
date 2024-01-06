import contextlib
import subprocess
from pathlib import Path
from typing import Optional

import typer

from src.gpt_utils import ChatMem, gpt_chat

app = typer.Typer()


def load_tests_and_signature(file_path: str):
    with Path(file_path).open() as f:
        code = f.read()

    # Assume that the first line is the commented-out function signature
    # and the rest of the code contains the unit tests.

    code_lines = code.splitlines()
    # Extract the function signature

    test_signature = code_lines[0].lstrip("#").strip()

    # Extract the unit tests
    test_code = "\n".join(code_lines[1:])

    return test_signature, test_code


def load_code_and_linting_output(file_path: str):
    # Step 1: Load the code

    with Path(file_path).open() as f:
        code = f.read()

    # Step 2: Run the `ruff` linter on file_path and capture the output

    linting_output = subprocess.run(["ruff", file_path], capture_output=True, text=True, check=False).stdout

    return code, linting_output.strip()


def run_pytest_and_process_results(test_module: str):
    # Remove any junit.xml file that may exist from a previous run
    with contextlib.suppress(FileNotFoundError):
        Path.unlink(Path("junit.xml"))

    return subprocess.run(
        ["pytest", "-p", "no:cacheprovider", "--tb=no", "--junit-xml=junit.xml", test_module], check=False
    ).returncode


@app.command()
def implement(file_path: str, max_iterations: int = 3, header: Optional[str] = None):
    system_msg = "Act as a brilliant Python developer (top coder) and implement a function that passes the provided tests. Use clean, modern and Pythonic code optimised for Python 3.11 or newer. Do your best to use only built-in Python functionality or imports from Python's Standard Library if needed - but make sure to include any required imports. Keep the function signature as close as possible to the one in the request. Try to keep code clean and minimal.  IMPORTANT: Output ONLY the implementation of the function, including the function signature but NO other text."
    mem = ChatMem(system_msg=system_msg)

    test_signature, pytest_code = load_tests_and_signature(file_path)

    iteration_count = 0
    all_tests_passed = False

    prompt = f"Implement a concise Python 3.10 function {test_signature} which passes the following tests. Make sure to output only clean Python code that will compile - NO OTHER TEXT! Here are the tests: \n\n {pytest_code}"
    if header:
        # Load the header from the file and add it to the prompt
        with Path(header).open() as f:
            header_text = f.read()
            prompt += f"\n\n Assume the following code is already implemented: \n\n{header_text}\n"

    while (not all_tests_passed) and (iteration_count < max_iterations):
        iteration_count += 1

        if iteration_count > 1:
            # load the entire junit.xml file
            with Path("junit.xml").open() as f:
                junit_xml = f.read()
            prompt = f" Here is the junit XML of the previous failed run. Focus only on the relevant parts of the code when making fixes for the failing tests. What do you think caused this? What's your best plan for fixing the failing tests (or finding an alternative approach)? \n {junit_xml}"
            mem.add("user", prompt)
            fix_suggestions = gpt_chat(mem.get())
            typer.echo(fix_suggestions)
            prompt = (
                "Ok, let's give it another try. Remember to output clean Python code ONLY - no other text or markup!"
            )

        mem.add("user", prompt)

        implementation = gpt_chat(mem.get())
        if "```" in implementation:
            # HACK: Despite best attempts in the prompt to avoid this, GPT still sometimes outputs a code block
            # Extract only the lines between '```python` and '```'
            implementation = implementation.split("```python")[1].split("```")[0].strip()

        if header:
            implementation = header_text + "\n\n# AI-implemented code: \n\n" + implementation

        typer.echo(implementation)

        with Path("implementation.py").open("w") as f:
            f.write(implementation + "\n")

        exit_code = run_pytest_and_process_results(file_path)

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


@app.command()
def lint(file_path: str, max_iterations: int = 3):
    system_msg = "Act as an experienced Python developer and fix all linting issues reported for the provided code. Use clean, modern and Pythonic code optimised for Python 3.10 or newer. Try to keep code clean and minimal. IMPORTANT: Output ONLY the fixed implementation of the function and NO other text."
    mem = ChatMem(system_msg=system_msg)

    impl_path = "implementation.py"

    attempts = 0
    while True:
        implementation_code, linting_output = load_code_and_linting_output(impl_path)
        attempts += 1

        if attempts > max_iterations:
            typer.echo(f"Max iterations reached without fixing all linting issues. See {impl_path}.")
            return

        # check if there are any linting issues
        if not linting_output:
            typer.echo(f"No linting issues remaining in: {impl_path}")

            typer.echo("Formatting the implementation code...")
            subprocess.run(["ruff", "format", impl_path], check=False)

            typer.echo("Ensuring the implementation code still passes all tests...")
            exit_code = run_pytest_and_process_results(file_path)
            if exit_code:
                typer.echo("The implementation code no longer passes all tests! See junit.xml.")
            else:
                typer.echo("The implementation code still passes all tests.")
                Path(impl_path).rename("implementation.py")
            return

        prompt = f"Fix all of these linting issues:  \n\n {linting_output} \n\n Here is the original code: \n\n {implementation_code}"
        mem.add("user", prompt)

        implementation = gpt_chat(mem.get())

        typer.echo(implementation)

        impl_path = "linted_implementation.py"

        with Path(impl_path).open("w") as f:
            f.write(implementation + "\n")

        typer.echo("Linting the implementation code...")
        subprocess.run(["ruff", "--fix", impl_path], check=False)


@app.command()
def describe(file_path: str):
    system_msg = "Act as an experienced Python developer and write a concise yet comprehensive technical specification for the implementation of a function which can pass all of the provided steps. Do your best to analyse all test cases in order to formulate a full description of what the function should do. "
    mem = ChatMem(system_msg=system_msg)

    test_signature, pytest_code = load_tests_and_signature(file_path)

    prompt = f"Write a technical specification for the implementation of a function `{test_signature}` which passes the following tests: \n\n {pytest_code}"

    mem.add("user", prompt)

    specification = gpt_chat(mem.get())

    typer.echo(specification)


if __name__ == "__main__":
    app()
