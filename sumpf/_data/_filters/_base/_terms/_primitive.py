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

"""Contains the classes for terms, that operate on the frequency variable ``s``
rather than on other terms."""

import numpy
import sumpf._internal as sumpf_internal
from ._base import Term
from . import _binary as binary
from .. import _functions as functions

__all__ = ("Constant", "Polynomial", "Exp", "Bands")


class Constant(Term):
    """A class for defining a constant transfer function, that does not depend on the frequency."""

    @staticmethod
    def factory(value, *args, **kwargs):    # pylint: disable=arguments-differ,unused-argument; this static method overrides a classmethod and does not need the cls argument
        """A class for defining a constant transfer function, that does not depend on the frequency.

        This is a static factory method.

        :param value: a term
        :param `*args,**kwargs`: neglected parameters, which allow to pass a ``transform``
                                 parameter like in the other term classes
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return Constant(value)

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
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        result = numpy.full(shape=s().shape, fill_value=self.value)
        return functions.copy_to_out(result, out)

    def invert_transform(self):
        """Creates a copy of the term, with the lowpass-to-highpass-transform inverted.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
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
        return f"Filter.{self.__class__.__name__}(value={self.value!r})"

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

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return Constant(1.0 / self.value)

    def __abs__(self):
        """An operator overload for computing the magnitude of a term with the
        built-in function :func:`abs`.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return Constant(abs(self.value))

    def __neg__(self):
        """An operator overload for inverting the phase of a terms with ``-term``.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
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
        """A class for defining a polynomial of the frequency variable ``s``.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._primitive.Polynomial` instance.
        But due to optimizations, it might return an instance of another subclass
        of :class:`~sumpf._data._filters._base._terms._base.Term`, if that is
        simpler and more efficient.

        :param coefficients: a sequence of coefficients for the polynomial, in which
                             the first coefficient is that of the highest power of ``s``.
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
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
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
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
        if isinstance(self.coefficients, numpy.ndarray):
            array = numpy.array2string(self.coefficients,
                                       separator=",",
                                       formatter={"all": repr},
                                       threshold=self.coefficients.size).replace(" ", "")
            coefficients = f"array({array})"
        else:
            coefficients = repr(self.coefficients)
        return f"Filter.{self.__class__.__name__}(coefficients={coefficients}, transform={self.transform})"

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
        """A class for defining an exponential function with the multiplication
        of ``s`` and a coefficient in the exponent: ``exp(c * s)``.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._primitive.Exp` instance. But
        due to optimizations, it might return an instance of another subclass of
        :class:`~sumpf._data._filters._base._terms._base.Term`, if that is simpler
        and more efficient.

        :param coefficient: a value for the coefficient ``c`` in ``exp(c * s)``
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
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
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
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
        return f"Filter.{self.__class__.__name__}(coefficient={self.coefficient!r}, transform={self.transform})"

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

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return Exp(coefficient=-self.coefficient, transform=self.transform)

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Exp",
                "coefficient": self.coefficient,
                "transform": self.transform}


class Bands(Term):
    """A term, for defining a frequency dependent function by supporting points,
    an interpolation function and an extrapolation function.
    """

    @staticmethod
    def factory(xs, ys, interpolation, extrapolation, *args, **kwargs):  # pylint: disable=arguments-differ,unused-argument; this static method overrides a classmethod and does not need the cls argument
        """A term, for defining a frequency dependent function by supporting points,
        an interpolation function and an extrapolation function.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._primitive.Bands` instance. But
        due to optimizations, it might return an instance of another subclass of
        :class:`~sumpf._data._filters._base._terms._base.Term`, if that is simpler
        and more efficient.

        :param xs: a sequence of float frequency values of the supporting points
        :param ys: a sequence of float or complex function values of the supporting points
        :param interpolation: a flag from the :class:`sumpf.Bands.interpolations` enumeration
        :param extrapolation: a flag from the :class:`sumpf.Bands.interpolations` enumeration
        :param `*args,**kwargs`: neglected parameters, which allow to pass a ``transform``
                                 parameter like in the other term classes
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return Bands(xs, ys, interpolation, extrapolation)

    def __init__(self, xs, ys, interpolation, extrapolation, *args, **kwargs):  # pylint: disable=unused-argument
        """
        :param xs: a sequence of float frequency values of the supporting points
        :param ys: a sequence of float or complex function values of the supporting points
        :param interpolation: a flag from the :class:`sumpf.Bands.interpolations` enumeration
        :param extrapolation: a flag from the :class:`sumpf.Bands.interpolations` enumeration
        :param `*args,**kwargs`: neglected parameters, which allow to pass a ``transform``
                                 parameter like in the other term classes
        """
        Term.__init__(self, transform=False)
        self.xs = xs if isinstance(xs, numpy.ndarray) else numpy.array(xs)
        self.ys = ys if isinstance(ys, numpy.ndarray) else numpy.array(ys)
        self.interpolation = sumpf_internal.Interpolations(interpolation)
        extrapolation = sumpf_internal.Interpolations(extrapolation)
        if extrapolation is sumpf_internal.Interpolations.STAIRS_LOG:
            self.extrapolation = sumpf_internal.Interpolations.STAIRS_LIN
        else:
            self.extrapolation = extrapolation

    def _compute(self, s, out=None):
        """Implements the computation of the interpolation of the bands.
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        f = s.frequencies()
        if isinstance(f, float):
            if f < self.xs[0] or self.xs[-1] < f:
                extrapolation = sumpf_internal.interpolation.get(self.extrapolation)
                return extrapolation(x=f, xs=self.xs, ys=self.ys)  # pylint: disable=no-value-for-parameter; this function is modified by a decorator
            else:
                interpolation = sumpf_internal.interpolation.get(self.interpolation)
                return interpolation(x=f, xs=self.xs, ys=self.ys)  # pylint: disable=no-value-for-parameter; this function is modified by a decorator
        else:
            if out is None:
                out = numpy.empty(shape=f.shape, dtype=numpy.complex128)
            if self.xs.size:
                mask = (f < self.xs[0]) | (self.xs[-1] < f)
                extrapolation = sumpf_internal.interpolation.get(self.extrapolation)
                out[mask] = extrapolation(x=f[mask], xs=self.xs, ys=self.ys)  # pylint: disable=no-value-for-parameter; this function is modified by a decorator
                mask = ~mask
                interpolation = sumpf_internal.interpolation.get(self.interpolation)
                out[mask] = interpolation(x=f[mask], xs=self.xs, ys=self.ys)  # pylint: disable=no-value-for-parameter; this function is modified by a decorator
            else:
                out[:] = 0.0
            return out

    def invert_transform(self):
        """Creates a copy of the term, with the lowpass-to-highpass-transform inverted.
        In this case, it does nothing and returns ``self``, since a lowpass-to-highpass-transform
        is not defined for bands spectrums.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return self

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        return len(self.xs) == 0 or (self.ys == 0.0).all()

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        if isinstance(self.xs, numpy.ndarray):
            array = numpy.array2string(self.xs,
                                       separator=",",
                                       formatter={"all": repr},
                                       threshold=self.xs.size).replace(" ", "")
            xs = f"array({array})"
        else:
            xs = repr(self.xs)
        if isinstance(self.ys, numpy.ndarray):
            array = numpy.array2string(self.ys,
                                       separator=",",
                                       formatter={"all": repr},
                                       threshold=self.ys.size).replace(" ", "")
            ys = f"array({array})"
        else:
            ys = repr(self.ys)
        return (f"Filter.{self.__class__.__name__}("
                f"xs={xs}, "
                f"ys={ys}, "
                f"interpolation={self.interpolation}, "
                f"extrapolation={self.extrapolation})")

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if not isinstance(other, Bands):
            return False
        elif (self.interpolation != other.interpolation or
              self.extrapolation != other.extrapolation or
              numpy.not_equal(self.xs, other.xs).any() or
              numpy.not_equal(self.ys, other.ys).any()):
            return False
        return super().__eq__(other)

    def __invert__(self):
        """A repurposed operator overload for inverting a terms with ``~term``.
        The inverse of a term is ``1 / term``.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return Bands(xs=self.xs,
                     ys=1.0 / self.ys,
                     interpolation=self.interpolation,
                     extrapolation=self.extrapolation)

    def __abs__(self):
        """An operator overload for computing the magnitude of a term with the
        built-in function :func:`abs`.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return Bands(xs=self.xs,
                     ys=numpy.abs(self.ys),
                     interpolation=self.interpolation,
                     extrapolation=self.extrapolation)

    def __neg__(self):
        """An operator overload for inverting the phase of a terms with ``-term``.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        non_negative_interpolations = (sumpf_internal.Interpolations.ONE,
                                       sumpf_internal.Interpolations.LOGARITHMIC,
                                       sumpf_internal.Interpolations.LOG_Y)
        if self.interpolation in non_negative_interpolations or self.extrapolation in non_negative_interpolations:
            return binary.Difference(minuend=Constant(0.0),
                                     subtrahend=self)
        else:
            return Bands(xs=self.xs,
                         ys=-self.ys,
                         interpolation=self.interpolation,
                         extrapolation=self.extrapolation)

    def __add__(self, other):
        """An operator overload for adding two terms with ``+``."""
        if isinstance(other, Bands) and \
           numpy.array_equal(self.xs, other.xs) and \
           self.interpolation == other.interpolation and \
           self.extrapolation == other.extrapolation:
            return Bands(xs=self.xs,
                         ys=self.ys + other.ys,
                         interpolation=self.interpolation,
                         extrapolation=self.extrapolation)
        else:
            return super().__add__(other)

    def __sub__(self, other):
        """An operator overload for subtracting two terms with ``-``."""
        if isinstance(other, Bands) and \
           numpy.array_equal(self.xs, other.xs) and \
           self.interpolation == other.interpolation and \
           self.extrapolation == other.extrapolation:
            return Bands(xs=self.xs,
                         ys=self.ys - other.ys,
                         interpolation=self.interpolation,
                         extrapolation=self.extrapolation)
        else:
            return super().__sub__(other)

    def __mul__(self, other):
        """An operator overload for multiplying two terms with ``*``."""
        if isinstance(other, Bands) and \
           numpy.array_equal(self.xs, other.xs) and \
           self.interpolation == other.interpolation and \
           self.extrapolation == other.extrapolation:
            return Bands(xs=self.xs,
                         ys=self.ys * other.ys,
                         interpolation=self.interpolation,
                         extrapolation=self.extrapolation)
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        """An operator overload for dividing two terms with ``/``."""
        if isinstance(other, Bands) and \
           numpy.array_equal(self.xs, other.xs) and \
           self.interpolation == other.interpolation and \
           self.extrapolation == other.extrapolation:
            return Bands(xs=self.xs,
                         ys=self.ys / other.ys,
                         interpolation=self.interpolation,
                         extrapolation=self.extrapolation)
        else:
            return super().__truediv__(other)

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        if self.ys.dtype in (numpy.complex128, numpy.complex256, numpy.complex64):
            ys = {"real": tuple(numpy.real(self.ys)),
                  "imaginary": tuple(numpy.imag(self.ys))}
        else:
            ys = tuple(self.ys)
        return {"type": "Bands",
                "xs": tuple(self.xs),
                "ys": ys,
                "interpolation": int(self.interpolation),
                "extrapolation": int(self.extrapolation)}
