# AI Usage Disclosure

## Tools used

- ChatGPT (OpenAI; GPT-6, as displayed in this conversation).

## Conversation links

- https://chatgpt.com/share/6afafc24-ee20-83ed-a0dd-efb24f6c58d0

## What I used them for

- Understanding the lab specification and planning the implementation.
- Python validation, CSV parsing, query filtering, command-line arguments, JSON, and logging.
- Implementing and debugging the required functions against the university-provided public tests.

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How |
| --- | --- | --- |
| `validator.py` | `load_airports`, `validate_row`, `to_record` | Implemented with AI assistance |
| `csv_loader.py` | `parse_files` | Edited with AI assistance |
| `query.py` | `run_query`, `run_queries` | Drafted with AI assistance |
| `flight_parser.py` | `main` and JSON/logging helpers | Edited with AI assistance |


## Key prompts

1. "How does the exception handling works?"
2. "What are regular expressions?"
3. "CSV parsing"

## What I changed or verified myself

- I reviewed the code, run `python tests/run_public_tests.py`, and make sure I can explain and defend the implementation before submitting.
