# passtest: AI-Powered Test Driven Development

AI-Powered Test Driven Development (AI-TDD) improves the test-driven development process by using GPT to generate Python function implementations that pass specified unit tests. The tool uses GPT-4 to generate code, and the Python standard library `unittest` to test the AI-generated implementations.

## Features

- Takes a Python script containing `unittest` test cases as input
- Accepts a type-annotated function signature
- Uses GPT-4 to generate a function implementation that passes the provided tests
- Continuously iterates and improves the function implementation based on test results, until all tests pass or a specified maximum number of attempts is reached

## Installation

This project uses [Poetry](https://python-poetry.org/) as its package manager. To install and run the project, follow these steps:

1. Clone the repository:

```bash
git clone git@github.com:jordan-dimov/passtest.git
cd passtest
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Set the Python path correctly (this allows importing modules from `src/`):

```bash
export PYTHONPATH=.
```

## Usage

### Basic Usage

To run the AI-TDD tool, execute the following command:

```bash
poetry run python src/passtest.py FILE_PATH
```

Replace `FILE_PATH` with the path to your Python script containing type-annotated function signature and `unittest` test cases.

### Customized Usage

By default, the tool attempts up to 3 iterations. You can override this default with the `--max-iterations INTEGER` option: 

```bash
poetry run python src/passtest.py FILE_PATH --max-iterations 5
```

## Example

Suppose you have the unit tests in a file called `test_oddeven.py`. The first line of the file should contain a type-annotated function signature, and the rest of the file should contain the test cases:

```python
# def is_even(n: int) -> bool:
import unittest
from implementation import is_even

class TestOddEven(unittest.TestCase):
    def test_even_numbers(self):
        self.assertTrue(is_even(2))
        self.assertTrue(is_even(4))
        self.assertTrue(is_even(0))

    def test_odd_numbers(self):
        self.assertFalse(is_even(1))
        self.assertFalse(is_even(3))
        self.assertFalse(is_even(5))

if __name__ == "__main__":
    unittest.main()
```

Place the test file in your project directory, and then run the AI-TDD tool with the following command:

```bash
poetry run python src/passtest.py test_oddeven.py
```

The tool will generate an implementation for the `is_even()` function that passes all provided tests and save the implementation to a file `implementation.py`.
