Concepts
========

Converters
----------

Deduce relies on **converters**, i.e. functions that take a value
(generally a string, although this is not mendatory) and return another value,
raising a `ValueError` in case the input value is invalid.

Example converter:

.. code-block:: python

    def without_x(value):
        if "x" in str(value):
            raise ValueError("Cannot contain 'x'!")
        return value

Using this definition, the Python language actually has many built-in
converters: `int`, `float`, `str`, and others are all functions that take a
value, attempt to convert it and raise a `ValueError` if this process fails.

The power of Deduce lies in building upon these built-in converters while
providing building blocks for custom and/or more complex converters.

Clues
-----

Many Python built-ins naturally map to a type of converter among those defined
above. For example, `str.islower` naturally maps to `Filter(str.islower)`,
and `bool` maps to a `Equiv` that would map `"true"` and `"True"` to `True`
as well as `"false"` and `"False"` to `False`.

For this reason, **clues** make the detective aware about the Python built-ins,
which saves us from annotating parameters using the actual ``Converter``
objects. This makes for a cleaner and more pythonic API.

For example, `None` is a clue for an `Equiv` that makes
the following two snippets equivalent:

.. code-block:: python

    from deduce import deduce, Equiv

    @deduce
    def foo(x: Equiv({("null", "none", "None"): None})):
        pass

.. code-block:: python

    from deduce import deduce

    @deduce
    def foo(x: None):
        pass

You can retrieve the actual `Converter` object from the clue using
`deduce.retrieve`, which returns the clue itself if the detective has no
record for it:

.. code-block:: python

    >>> import deduce
    >>> islower = deduce.retrieve(str.islower)
    >>> assert isinstance(islower, deduce.Filter)
    >>> assert deduce.retrieve("foo") == "foo"

Lastly, you can record your own clues using `deduce.record`:

.. code-block:: python

    import deduce

    def with_foo(value: str) -> str:
        return f"Foo: {value}"

    deduce.record("foo", with_foo)
    assert deduce.retrieve("foo") == with_foo
    assert deduce.retrieve("foo")("bar") == "Foo: bar"

A decorator syntax is also available:

.. code-block:: python

    @deduce.clue("foo")
    def with_foo(value: str) -> str:
        return f"Foo: {value}"

Deduction
---------

**Deduction** is the process of attaching converters to the parameters of
a function. Deduce does this by processing the function's signature,
looking for type annotations declared on its parameters.

When the deducted function is called, each argument is transformed using
the registered converter. If the corresponding parameter was not annotated,
the value is passed unchanged (using the `Identity` converter).

All conversion failures
(caused by one or more converters raising a`ValueError`),
if any, are collected and bundled in a `deduce.ConversionError` and
accessible on its `.errors` attribute.

In practice, you can deduct a function using `deduce.deduce`:

.. code-block:: python

    from deduce import deduce

    @deduce
    def add(x: int, y: int):
        return x + y

In the above example, string values passed for the `x` and `y` arguments
of `add` are converted to integers, which means we can call `add` like so:

.. code-block:: python

    >>> add("1", "2")
    3

If `x` is given a value that cannot be converted to an integer,
a `deduce.ConversionError` is raised:

.. code-block:: python

    >>> add("foo", "2")
    ConversionError: {"x": "invalid literal for int() with base 10: 'foo'"}

Finally, since `deduce` is a decorator, it can also be used as a
regular function:

.. code-block:: python

    from typing import Callable

    from deduce import deduce

    def do_stuff(func: Callable):
        deducted = deduce(func)
        # Do something with the deducted function…
