.. Limier documentation master file, created by
   sphinx-quickstart on Sun Feb 10 16:25:00 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Limier
======

.. code-block:: python

    from limier import deduce, chain

    # Custom converter: validate that the input value is positive.
    def positive(value: int) -> int:
        if value < 0:
            raise ValueError("Expected positive value")
        return value

    # Building custom converters is easy!
    # Here, we chain two converters together.
    positive_int = chain(int, positive)

    @deduce
    def compute(x: int, times: positive_int) -> float:
        return x * times

    result = compute("2", times="2.5")
    assert result == 5

.. toctree::
    :maxdepth: 2

    concepts.rst
    api.rst
