# Agent Brief

<!-- Replace everything below with your own task description. -->
<!-- The agent reads this file at the start of every run. -->

## What to build

A Python CLI utility called `wordcount` that:

1. Accepts one or more file paths as positional arguments.
2. Prints a table showing lines, words, and characters for each file.
3. Prints a total row when more than one file is given.
4. Exits with code 1 and a helpful message if a file does not exist.

## Location

- Main script: `tools/wordcount.py`
- Tests: `tools/tests/test_wordcount.py`

## Constraints

- Standard library only (no third-party dependencies).
- Tests must use `pytest`.
- The script must be runnable as `python tools/wordcount.py file1.txt file2.txt`.

## Example output

```
file1.txt    10    42   301
file2.txt     5    20   150
total        15    62   451
```
