Concepts
========

Converters
----------

Colon relies on **converters**, i.e. functions that take a value
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

The power of Colon lies in building upon these built-in converters while
providing building blocks for custom and/or more complex converters.

Aliases
-------

Many Python built-ins naturally map to a type of converter among those defined
above. For example, `str.islower` naturally maps to `Filter(str.islower)`,
and `bool` maps to a `Equiv` that would map `"true"` and `"True"` to `True`
as well as `"false"` and `"False"` to `False`.

For this reason, Colon has a notion of **converter alias** which allows to use
the Python built-in instead of the actual `Converter` object. This makes for a
cleaner, more transparent and more pythonic API.

For example, `None` is aliased an `Equiv` that makes the following two snippets
equivalent:

.. code-block:: python

    from colon import punctuate, Equiv

    @punctuate
    def foo(x: Equiv({("null", "none", "None"): None})):
        pass

.. code-block:: python

    from colon import punctuate

    @punctuate
    def foo(x: None):
        pass

You can retrieve the actual `Converter` object from the alias using
`colon.get`, which returns the alias itself if not converter was found:

.. code-block:: python

    >>> import colon
    >>> islower = colon.get(str.islower)
    >>> assert isinstance(islower, colon.Filter)
    >>> assert colon.get("foo") == "foo"

Lastly, you can define your own aliases using `colon.alias`:

.. code-block:: python

    import colon

    def with_foo(value: str) -> str:
        return f"Foo: {value}"

    colon.alias("foo", with_foo)
    assert colon.get("foo") == with_foo
    assert colon.get("foo")("bar") == "Foo: bar"

A decorator syntax is also available:

.. code-block:: python

    @colon.alias("foo")
    def with_foo(value: str) -> str:
        return f"Foo: {value}"

Punctuation
-----------

**Punctuation** is the process of attaching converters to the parameters of
a function. Colon does this by processing the function's signature,
looking for type annotations declared on its parameters.

When the punctuated function is called, each argument is transformed using
the registered converter. If the corresponding parameter was not annotated,
the value is passed unchanged (using the `Identity` converter).

All conversion failures
(caused by one or more converters raising a`ValueError`),
if any, are collected and bundled in a `colon.ConversionError` and
accessible on its `.errors` attribute.

In practice, you can punctuate a function using `colon.punctuate`:

.. code-block:: python

    from colon import punctuate

    @punctuate
    def add(x: int, y: int):
        return x + y

In the above example, string values passed for the `x` and `y` arguments
of `add` are converted to integers, which means we can call `add` like so:

.. code-block:: python

    >>> add("1", "2")
    3

If `x` is given a value that cannot be converted to an integer,
a `colon.ConversionError` is raised:

.. code-block:: python

    >>> add("foo", "2")
    ConversionError: {"x": "invalid literal for int() with base 10: 'foo'"}

Finally, since `punctuate` is a decorator, it can also be used as a
regular function:

.. code-block:: python

    from typing import Callable

    from colon import punctuate

    def do_stuff(func: Callable):
        punctuated = punctuate(func)
        # Do something with the punctuated function…
