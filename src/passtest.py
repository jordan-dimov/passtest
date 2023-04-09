import typer
import unittest
import io
from contextlib import redirect_stdout

app = typer.Typer()


def load_tests_and_signature(file_path: str):
    with open(file_path, "r") as f:
        code = f.read()

    # Assume that the first line is the commented-out function signature
    # and the rest of the code contains the unit tests.

    code_lines = code.splitlines()
    # Extract the function signature

    test_signature = code_lines[0].lstrip("#").strip()

    # Extract the unit tests
    test_code = "\n".join(code_lines[1:])

    return test_signature, test_code


def generate_function_implementation(system_msg: str, prompt: str):
    # Call the AI function to generate the implementation
    implementation = "def odd_even():\n    return 'odd'"

    return implementation


def run_pytest_and_process_results(test_module: str, implementation: str):
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
    test_signature, pytest_code = load_tests_and_signature(file_path)

    iteration_count = 0
    all_tests_passed = False

    while not all_tests_passed and iteration_count < max_iterations:
        iteration_count += 1

        system_msg = "Act as an experienced Python developer and implement a function that passes the provided tests. Output ONLY the implementation of the function, including the function signature but NO other text."
        prompt = f"Implement a concise Python function {test_signature} that passes the following tests: {pytest_code}"
        if iteration_count > 1:
            prompt += f" Here's the information about the failed test cases: {failed_tests_info}"

        implementation = generate_function_implementation(system_msg, prompt)
        with open("implementation.py", "w") as f:
            f.write(implementation)

        # Integrate implementation with initial code
        # Save the updated code to a .py file

        test_module = file_path.split("/")[-1].replace(".py", "")
        passed_tests, failed_tests_info = run_pytest_and_process_results(
            test_module, implementation
        )

        if passed_tests:
            all_tests_passed = True

    if all_tests_passed:
        typer.echo("The AI-generated implementation passed all tests!")
    else:
        typer.echo("Max iterations reached without passing all tests: ")
        typer.echo(failed_tests_info)


if __name__ == "__main__":
    app()
