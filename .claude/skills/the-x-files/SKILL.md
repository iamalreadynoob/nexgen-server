---
name: the-x-files
description: Write exactly one Python method from a NAME, RETURNS, ARGS and STEPS spec, with a Google-style docstring, type hints, clear step comments and logging when it is useful. Use when the user invokes /the-x-files or gives a NAME/RETURNS/ARGS/STEPS method spec.
---

# The X Files

Write **one** Python method. Only one. No helper functions, no extra classes, no tests, no example usage, no second method.

## 1. Collect the spec

The method needs these four fields:

| Field   | Meaning                                                                |
| ------- | ---------------------------------------------------------------------- |
| NAME    | The method name. Convert it to `snake_case` if it is not.              |
| RETURNS | The return type, as a Python type (`str`, `list[int]`, `None`, ...).   |
| ARGS    | The arguments. Each one has a name and a Python-like type, and optionally a default and a description. |
| STEPS   | The ordered steps the method does.                                     |

Rules:

- If NAME, RETURNS, ARGS or STEPS is missing or unclear, ask the user for it before you write code. Do not guess. ARGS can be "none".
- Turn loose type names into real Python type hints:
  - `string` → `str`, `integer` → `int`, `float`/`number` → `float`, `boolean` → `bool`
  - `list of X` → `list[X]`, `dict of K to V` → `dict[K, V]`, `optional X` → `X | None` (default `None`)
  - `any` → `Any` (import from `typing`)
- If a step is ambiguous, ask about that step. Do not add steps the user did not give, except input checks and logging that a step clearly needs.
- If the user names a class or a file, write the method there (with `self` if it is an instance method). If the method calls I/O that is already `async` in that file, make it `async`. Otherwise, give the method in one code block in your reply.

## 2. Write the method

### Signature

- Type-hint every argument and the return value.
- Put each argument on its own line with a trailing comma when there is more than one argument.
- Arguments with defaults come after arguments without defaults.

### Docstring (Google style)

Use this layout. Leave out a section only when it has nothing to say (for example, no `Args:` when there are no arguments, no `Raises:` when nothing is raised).

```python
"""# Method Name In Title Case.

One or two sentences that say what the method does and why.

Args:
    arg_name: What the argument is. Say the default if it matters.
    other_arg: What the argument is.

Returns:
    What the return value is and what it holds.

Raises:
    ValueError: When this exception is raised.
"""
```

- The first line is `# <NAME in Title Case>.` to match this repository.
- Every argument in the signature has one line in `Args:`. Do not repeat the type there; the type hint holds it.
- `Raises:` lists every exception that the method raises itself.

### Body

- Write each STEP as one block of code. Put one short comment above each block that says what the step does, in plain imperative words: `# Validate the input.`, `# Fetch the record from the repository.`. The comment says *what* and *why*, not a copy of the code.
- Keep the steps in the order the user gave.
- Pass keyword arguments explicitly in calls, even with one argument. Multi-line calls use a trailing comma.
- Raise a specific exception with a clear message for bad input. Do not use bare `except:` or `except Exception: pass`.
- No `print`. No `assert` for input checks.

### Logging (only when it is needed)

Add logging when the method does I/O, calls an external service, changes state, or can fail in a way someone must debug later. Skip it for small pure functions.

- Use a module-level logger: `logger = logging.getLogger(__name__)`. If the file does not have one yet, say in your reply that the line and `import logging` must be added at module level (or add them, if you are editing the file).
- Use `%`-style arguments, not f-strings: `logger.info("Created actuator %s", name)`.
- Levels: `debug` for details, `info` for a completed action, `warning` for a recoverable problem, `exception` inside an `except` block for an error with its traceback.
- Never log secrets, API keys, passwords or full payloads.

## 3. Check before you answer

- [ ] Exactly one method.
- [ ] Name, return type and arguments match the spec.
- [ ] Every STEP is in the body, in order, with a comment.
- [ ] Google docstring with `Args:`, `Returns:` and `Raises:` where they apply.
- [ ] Logging only if needed, with `%`-style arguments.
- [ ] The code passes the repository's Ruff rules (`uv run ruff check <file>` when you edit a file).

## Example

Spec:

- NAME: `get_active_names`
- RETURNS: list of string
- ARGS: `docs` (list of dict), `prefix` (optional string)
- STEPS: 1. keep only docs where `active` is true. 2. if prefix is given, keep only names that start with it. 3. return the names sorted.

Output:

```python
def get_active_names(
    docs: list[dict[str, Any]],
    prefix: str | None = None,
) -> list[str]:
    """# Get Active Names.

    Collect the names of active documents, optionally filtered by a prefix.

    Args:
        docs: The documents to read. Each one has a `name` and an `active` key.
        prefix: If given, keep only names that start with this text.

    Returns:
        The matching names, sorted in ascending order.
    """
    # Keep only the active documents.
    names = [doc["name"] for doc in docs if doc.get("active") is True]

    # Filter the names by the prefix, if one is given.
    if prefix is not None:
        names = [name for name in names if name.startswith(prefix)]

    # Return the names in sorted order.
    return sorted(names)
```

This example has no logging because it is a small pure function.
