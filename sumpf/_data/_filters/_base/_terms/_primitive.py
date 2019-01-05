# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2019 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains the classes for terms, that operate on the frequency variable ``s``
rather than on other terms."""

import numpy
from ._base import Term
from .. import _functions as functions

__all__ = ("Constant", "Polynomial", "Exp")


class Constant(Term):
    """A class for defining a constant transfer function, that does not depend on
    the frequency.
    """

    def __init__(self, value, *args, **kwargs):     # pylint: disable=unused-argument
        """
        :param value: the constant value
        :param `*args,**kwargs`: neglected parameters, which allow to pass a ``transform``
                                 parameter like in the other term classes
        """
        Term.__init__(self, transform=False)
        self.value = value

    def _compute(self, s, out=None):
        """Generates an array and fills it with the constant value.
        :param s: an S instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        result = numpy.full(shape=s().shape, fill_value=self.value)
        return functions.copy_to_out(result, out)

    def invert_transform(self):
        """Creates a copy of the term, with the lowpass-to-highpass-transform inverted.

        :returns: an instance of a subclass of Term
        """
        return self

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        return self.value == 0.0

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return "Filter.{class_}(value={value!r})".format(class_=self.__class__.__name__, value=self.value)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if self.value == 0.0 and other.is_zero():
            return True
        elif not isinstance(other, Constant):
            return False
        elif self.value != other.value:
            return False
        return super().__eq__(other)

    def __invert__(self):
        """A repurposed operator overload for inverting a terms with ``~term``.
        The inverse of a term is ``1 / term``.

        :returns: an instance of a subclass of Term
        """
        return Constant(1.0 / self.value)

    def __abs__(self):
        """An operator overload for computing the magnitude of a term with the
        built-in function :func:`abs`.

        :returns: an instance of a subclass of Term
        """
        return Constant(abs(self.value))

    def __neg__(self):
        """An operator overload for inverting the phase of a terms with ``-term``.

        :returns: an instance of a subclass of Term
        """
        return Constant(-self.value)

    def __add__(self, other):
        """An operator overload for adding two terms with ``+``."""
        if self.value == 0.0:
            return other
        elif isinstance(other, Constant):
            return Constant(self.value + other.value)
        else:
            return super().__add__(other)

    def __sub__(self, other):
        """An operator overload for subtracting two terms with ``-``."""
        if self.value == 0.0:
            return -other
        elif isinstance(other, Constant):
            return Constant(self.value - other.value)
        else:
            return super().__sub__(other)

    def __mul__(self, other):
        """An operator overload for multiplying two terms with ``*``."""
        if self.value == 0.0:
            return self
        elif self.value == 1.0:
            return other
        elif self.value == -1.0:
            return -other
        elif isinstance(other, Constant):
            return Constant(self.value * other.value)
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        """An operator overload for dividing two terms with ``/``."""
        if self.value == 0.0:
            return self
        elif isinstance(other, Constant):
            return Constant(self.value / other.value)
        else:
            return super().__truediv__(other)

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Constant",
                "value": self.value}


class Polynomial(Term):
    """A class for defining a polynomial of the frequency variable ``s``."""

    @staticmethod
    def factory(coefficients, transform=False):     # pylint: disable=arguments-differ; this static method overrides a classmethod and does not need the cls argument
        """A static factory method, that performs some optimizations, which the
        constructor of this class cannot do.

        :param coefficients: a sequence of coefficients for the polynomial, in which
                             the first coefficient is that of the highest power of ``s``.
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of Term
        """
        if len(coefficients):                           # pylint: disable=len-as-condition; coefficients might be a NumPy array, where __nonzero__ is not equivalent to len(.)
            non_zero = numpy.nonzero(coefficients)[0]
            if len(non_zero):                           # pylint: disable=len-as-condition; non_zero is a NumPy array, where __nonzero__ is not equivalent to len(.)
                coefficients = coefficients[min(non_zero):]
                if len(coefficients) == 1:
                    return Constant(coefficients[0])
                else:
                    return Polynomial(coefficients, transform)
            else:
                return Constant(0.0)
        else:
            return Constant(0.0)

    def __init__(self, coefficients, transform=False):
        """
        :param coefficients: a sequence of coefficients for the polynomial, in which
                             the first coefficient is that of the highest power of ``s``.
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        """
        Term.__init__(self, transform=transform)
        self.coefficients = coefficients

    def _compute(self, s, out=None):
        """Implements the computation of the polynomial.
        :param s: an S instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        result = numpy.polyval(self.coefficients, s())
        return functions.copy_to_out(result, out)

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        if numpy.count_nonzero(self.coefficients):
            return False
        else:
            return True

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        mask = "Filter.{class_}(coefficients={coefficients!r}, transform={transform})"
        return mask.format(class_=self.__class__.__name__,
                           coefficients=self.coefficients,
                           transform=self.transform)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if not isinstance(other, Polynomial):
            return False
        elif numpy.shape(self.coefficients) != numpy.shape(other.coefficients):
            return False
        elif numpy.not_equal(self.coefficients, other.coefficients).any():
            return False
        return super().__eq__(other)

    def __add__(self, other):
        """An operator overload for adding two terms with ``+``."""
        if isinstance(other, Polynomial) and self.transform == other.transform:
            return Polynomial(coefficients=numpy.polyadd(self.coefficients, other.coefficients),
                              transform=self.transform)
        elif isinstance(other, Constant):
            if len(self.coefficients):  # pylint: disable=len-as-condition; coefficients might be a NumPy array, where __nonzero__ is not equivalent to len(.)
                coefficients = list(self.coefficients)
                coefficients[-1] += other.value
                return Polynomial(coefficients=coefficients, transform=self.transform)
            else:
                return -other
        else:
            return super().__add__(other)

    def __sub__(self, other):
        """An operator overload for subtracting two terms with ``-``."""
        if isinstance(other, Polynomial) and self.transform == other.transform:
            return Polynomial(coefficients=numpy.polysub(self.coefficients, other.coefficients),
                              transform=self.transform)
        elif isinstance(other, Constant):
            if len(self.coefficients):  # pylint: disable=len-as-condition; coefficients might be a NumPy array, where __nonzero__ is not equivalent to len(.)
                coefficients = list(self.coefficients)
                coefficients[-1] -= other.value
                return Polynomial(coefficients=coefficients, transform=self.transform)
            else:
                return -other
        else:
            return super().__sub__(other)

    def __mul__(self, other):
        """An operator overload for multiplying two terms with ``*``."""
        if isinstance(other, Constant):
            return Polynomial(coefficients=numpy.multiply(self.coefficients, other.value),
                              transform=self.transform)
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        """An operator overload for dividing two terms with ``/``."""
        if isinstance(other, Constant):
            return Polynomial(coefficients=numpy.divide(self.coefficients, other.value),
                              transform=self.transform)
        else:
            return super().__truediv__(other)

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Polynomial",
                "coefficients": tuple(self.coefficients),
                "transform": self.transform}


class Exp(Term):
    """A class for defining an exponential function with the multiplication of
    ``s`` and a coefficient in the exponent: ``exp(c * s)``.
    """

    @staticmethod
    def factory(coefficient, transform=False):  # pylint: disable=arguments-differ; this static method overrides a classmethod and does not need the cls argument
        """A static factory method, that performs some optimizations, which the
        constructor of this class cannot do.

        :param coefficient: a value for the coefficient ``c`` in ``exp(c * s)``
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of Term
        """
        if coefficient == 0.0:
            return Constant(1.0)
        else:
            return Exp(coefficient, transform)

    def __init__(self, coefficient, transform=False):
        """
        :param coefficient: a value for the coefficient ``k`` in ``exp(k * s)``
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        """
        Term.__init__(self, transform=transform)
        self.coefficient = coefficient

    def _compute(self, s, out=None):
        """Implements the computation of the exponential function.
        :param s: an S instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        exponent = numpy.multiply(self.coefficient, s(), out=out)
        return numpy.exp(exponent, out=out)

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        mask = "Filter.{class_}(coefficient={coefficient!r}, transform={transform})"
        return mask.format(class_=self.__class__.__name__,
                           coefficient=self.coefficient,
                           transform=self.transform)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if not isinstance(other, Exp):
            return False
        elif self.coefficient != other.coefficient:
            return False
        return super().__eq__(other)

    def __invert__(self):
        """A repurposed operator overload for inverting a terms with ``~term``.
        The inverse of a term is ``1 / term``.

        :returns: an instance of a subclass of Term
        """
        return Exp(coefficient=-self.coefficient, transform=self.transform)

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Exp",
                "coefficient": self.coefficient,
                "transform": self.transform}
