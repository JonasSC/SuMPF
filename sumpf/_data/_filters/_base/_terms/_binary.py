# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
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

"""Contains the classes for terms, that are composed of multiple other terms."""

import warnings
import numpy
from ._base import Term
from ._primitive import Constant
from .. import _functions as functions

__all__ = ("Sum", "Difference", "Product", "Quotient")


class Sum(Term):
    """A class for summing up a sequence of terms."""

    @staticmethod
    def factory(summands, transform=False):     # pylint: disable=arguments-differ; this static method overrides a classmethod and does not need the cls argument
        """A class for summing up a sequence of terms.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._binary.Sum` instance. But due
        to optimizations, it might return an instance of another subclass of
        :class:`~sumpf._data._filters._base._terms._base.Term`, if that is simpler
        and more efficient.

        :param summands: a sequence of terms, that shall be summed up
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        summands = tuple(s for s in summands if not s.is_zero())
        if len(summands) == 0:                                      # pylint: disable=len-as-condition; the length is also compared to other values
            return Constant(0.0)
        elif len(summands) == 1:
            if transform:
                return summands[0].invert_transform()
            else:
                return summands[0]
        elif len(summands) == 2:
            if transform:
                return summands[0].invert_transform() + summands[1].invert_transform()
            else:
                return summands[0] + summands[1]
        else:
            return Sum(summands, transform)

    def __init__(self, summands, transform=False):
        """
        :param summands: a sequence of terms, that shall be summed up
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        """
        Term.__init__(self, transform=transform)
        self.summands = tuple(summands)

    def _compute(self, s, out=None):
        """Implements the summation.
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        if self.summands:
            result = self.summands[0](s, out=out)
            for a in self.summands[1:]:
                result = numpy.add(result, a(s), out=out)
            return result
        else:
            result = numpy.zeros(numpy.shape(s()))
            return functions.copy_to_out(result, out)

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        for s in self.summands:
            if not s.is_zero():
                return False
        return True

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return "Filter.{class_}(summands={summands!r}, transform={transform})".format(class_=self.__class__.__name__,
                                                                                      summands=self.summands,
                                                                                      transform=self.transform)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if not isinstance(other, Sum):
            return False
        elif len(self.summands) != len(other.summands):
            return False
        for s1, s2 in zip(self.summands, other.summands):
            if s1 != s2:
                return False
        return super().__eq__(other)

    def __add__(self, other):
        """An operator overload for adding two terms with ``+``."""
        if self.summands:
            if self.transform == other.transform and isinstance(other, Sum):
                return Sum(summands=self.summands + other.summands, transform=self.transform)
            if self.transform:
                summands = tuple(s.invert_transform() for s in self.summands)
            else:
                summands = self.summands
            return Sum(summands=summands + (other,))
        else:
            return other

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Sum",
                "summands": [s.as_dict() for s in self.summands],
                "transform": self.transform}


class Difference(Term):
    """A class for subtracting two terms from each other."""

    @staticmethod
    def factory(minuend, subtrahend, transform=False):  # pylint: disable=arguments-differ; this static method overrides a classmethod and does not need the cls argument
        """A class for subtracting two terms from each other.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._binary.Difference` instance.
        But due to optimizations, it might return an instance of another subclass
        of :class:`~sumpf._data._filters._base._terms._base.Term`, if that is
        simpler and more efficient.

        :param minuend: a term, from which the subtrahend shall be subtracted
        :param subtrahend: a term, which the shall be subtracted from the minuend
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        if subtrahend.is_zero():
            if minuend.is_zero():
                return Constant(0.0)
            elif transform:
                return minuend.invert_transform()
            else:
                return minuend
        elif minuend.is_zero():
            return -subtrahend
        elif minuend == subtrahend:
            return Constant(0.0)
        else:
            return Difference(minuend, subtrahend, transform)

    def __init__(self, minuend, subtrahend, transform=False):
        """
        :param minuend: a term, from which the subtrahend shall be subtracted
        :param subtrahend: a term, which the shall be subtracted from the minuend
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        """
        Term.__init__(self, transform=transform)
        self.minuend = minuend
        self.subtrahend = subtrahend

    def _compute(self, s, out=None):
        """Implements the subtraction.
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        return numpy.subtract(self.minuend(s),
                              self.subtrahend(s),
                              out=out)

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        if self.minuend == self.subtrahend:
            return True
        elif self.minuend.is_zero() and self.subtrahend.is_zero():
            return True
        return False

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return ("Filter.{class_}(minuend={minuend!r}, "
                "subtrahend={subtrahend!r}, "
                "transform={transform})").format(class_=self.__class__.__name__,
                                                 minuend=self.minuend,
                                                 subtrahend=self.subtrahend,
                                                 transform=self.transform)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if not isinstance(other, Difference):
            return False
        elif self.minuend != other.minuend:
            return False
        elif self.subtrahend != other.subtrahend:
            return False
        return super().__eq__(other)

    def __neg__(self):
        """An operator overload for inverting the phase of a terms with ``-term``.

        :returns: an instance of a subclass of Term
        """
        return Difference(minuend=self.subtrahend,
                          subtrahend=self.minuend,
                          transform=self.transform)

    def __add__(self, other):
        """An operator overload for adding two terms with ``+``."""
        if self.transform:
            other = other.invert_transform()
        return Difference(minuend=self.minuend + other,
                          subtrahend=self.subtrahend,
                          transform=self.transform)

    def __sub__(self, other):
        """An operator overload for subtracting two terms with ``-``."""
        if self.transform:
            other = other.invert_transform()
        return Difference(minuend=self.minuend,
                          subtrahend=self.subtrahend + other,
                          transform=self.transform)

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Difference",
                "minuend": self.minuend.as_dict(),
                "subtrahend": self.subtrahend.as_dict(),
                "transform": self.transform}


class Product(Term):
    """A class for multiplying all terms from a sequence of terms."""

    @staticmethod
    def factory(factors, transform=False):  # pylint: disable=arguments-differ; this static method overrides a classmethod and does not need the cls argument
        """A class for multiplying all terms from a sequence of terms.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._binary.Product` instance. But
        due to optimizations, it might return an instance of another subclass of
        :class:`~sumpf._data._filters._base._terms._base.Term`, if that is simpler
        and more efficient.

        :param factors: a sequence of terms, that shall be multiplied
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        if len(factors) == 0 or any(f.is_zero() for f in factors):  # pylint: disable=len-as-condition; the length is also compared to other values
            return Constant(0.0)
        elif len(factors) == 1:
            if transform:
                return factors[0].invert_transform()
            else:
                return factors[0]
        elif len(factors) == 2:
            if transform:
                return factors[0].invert_transform() * factors[1].invert_transform()
            else:
                return factors[0] * factors[1]
        else:
            return Product(factors, transform)

    def __init__(self, factors, transform=False):
        """
        :param factors: a sequence of terms, that shall be multiplied
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        """
        Term.__init__(self, transform=transform)
        self.factors = tuple(factors)

    def _compute(self, s, out=None):
        """Implements the multiplication.
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        if self.factors:
            result = self.factors[0](s, out=out)
            for f in self.factors[1:]:
                result = numpy.multiply(result, f(s), out=out)
            return result
        else:
            result = numpy.zeros(numpy.shape(s()))
            return functions.copy_to_out(result, out)

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        if self.factors:
            for f in self.factors:
                if f.is_zero():
                    return True
            return False
        else:
            return True

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return "Filter.{class_}(factors={factors!r}, transform={transform})".format(class_=self.__class__.__name__,
                                                                                    factors=self.factors,
                                                                                    transform=self.transform)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if not isinstance(other, Product):
            return False
        elif len(self.factors) != len(other.factors):
            return False
        for f1, f2 in zip(self.factors, other.factors):
            if f1 != f2:
                return False
        return super().__eq__(other)

    def __mul__(self, other):
        """An operator overload for multiplying two terms with ``*``."""
        if self.factors and not other.is_zero():
            if isinstance(other, Product):
                if self.transform == other.transform:
                    return Product(factors=self.factors + other.factors,
                                   transform=self.transform)
                else:
                    return Product(factors=self.factors + tuple(f.invert_transform() for f in other.factors),
                                   transform=self.transform)
            if self.transform:
                factors = tuple(f.invert_transform() for f in self.factors)
            else:
                factors = self.factors
            return Product(factors=factors + (other,))
        else:
            return Constant(0.0)

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Product",
                "factors": [f.as_dict() for f in self.factors],
                "transform": self.transform}


class Quotient(Term):
    """A class for dividing two terms by each other."""

    @staticmethod
    def factory(numerator, denominator, transform=False):   # pylint: disable=arguments-differ; this static method overrides a classmethod and does not need the cls argument
        """A class for dividing two terms by each other.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._binary.Quotient` instance.
        But due to optimizations, it might return an instance of another subclass
        of :class:`~sumpf._data._filters._base._terms._base.Term`, if that is simpler
        and more efficient.

        :param numerator: a term, that shall be divided by the denominator
        :param denominator: a term, by which the numerator shall be divided
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        if numerator.is_zero():
            return Constant(0.0)
        elif numerator == denominator:
            return Constant(1.0)
        else:
            return Quotient(numerator, denominator, transform)

    def __init__(self, numerator, denominator, transform=False):
        """
        :param numerator: a term, that shall be divided by the denominator
        :param denominator: a term, by which the numerator shall be divided
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        """
        Term.__init__(self, transform=transform)
        self.numerator = numerator
        self.denominator = denominator

    def _compute(self, s, out=None):
        """Implements the division.
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=RuntimeWarning)
            return numpy.divide(self.numerator(s),
                                self.denominator(s),
                                out=out)

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        return self.numerator.is_zero()

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return ("Filter.{class_}(numerator={numerator!r}, "
                "denominator={denominator!r}, "
                "transform={transform})").format(class_=self.__class__.__name__,
                                                 numerator=self.numerator,
                                                 denominator=self.denominator,
                                                 transform=self.transform)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``"""
        if not isinstance(other, Quotient):
            return False
        elif self.numerator != other.numerator:
            return False
        elif self.denominator != other.denominator:
            return False
        return super().__eq__(other)

    def __invert__(self):
        """A repurposed operator overload for inverting a terms with ``~term``.
        The inverse of a term is ``1 / term``.

        :returns: an instance of a subclass of Term
        """
        return Quotient(numerator=self.denominator,
                        denominator=self.numerator,
                        transform=self.transform)

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Quotient",
                "numerator": self.numerator.as_dict(),
                "denominator": self.denominator.as_dict(),
                "transform": self.transform}
