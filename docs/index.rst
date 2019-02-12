.. Deduce documentation master file, created by
   sphinx-quickstart on Sun Feb 10 16:25:00 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Deduce
=======

.. code-block:: python

    from deduce import punctuate, chain

    # Custom converter: validate that the input value is positive
    def positive(value: int) -> int:
        if value < 0:
            raise ValueError("Expected positive value")
        return value

    # Building custom converters is easy!
    # Here, we chain two converters together.
    positive_int = chain(int, positive)

    # Punctuated function: converts inputs using the type annotation.
    @punctuate
    def compute(x: int, times: positive_int) -> float:
        return x * times

    result = compute("2", times="2.5")
    assert result == 5

.. toctree::
    :maxdepth: 2

    concepts.rst
    api.rst
