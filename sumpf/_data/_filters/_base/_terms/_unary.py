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

"""Contains the classes for terms, that wrap other terms."""

import numpy
from ._base import Term

__all__ = ("Absolute", "Negative")


class Absolute(Term):
    """A class for computing the absolute (magnitude) of another term."""

    @staticmethod
    def factory(value, transform=False):    # pylint: disable=arguments-differ; this static method overrides a classmethod and does not need the cls argument
        """A class for computing the absolute (magnitude) of another term.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._unary.Absolute` instance. But
        due to optimizations, it might return an instance of another subclass of
        :class:`~sumpf._data._filters._base._terms._base.Term`, if that is simpler
        and more efficient.

        :param value: a term
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        if transform:
            return abs(value.invert_transform())
        else:
            return abs(value)

    def __init__(self, value, transform=False):
        """
        :param value: a term
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        """
        Term.__init__(self, transform=transform)
        self.value = value

    def _compute(self, s, out=None):
        """Implements the computation of the magnitude.
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        return numpy.absolute(self.value(s, out=out), out=out)

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        return self.value.is_zero()

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return "Filter.{class_}(value={value!r}, transform={transform})".format(class_=self.__class__.__name__,
                                                                                value=self.value,
                                                                                transform=self.transform)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if not isinstance(other, Absolute):
            return False
        elif self.value != other.value:
            return False
        return super().__eq__(other)

    def __abs__(self):
        """An operator overload for computing the magnitude of a term with the
        built-in function :func:`abs`.

        :returns: an instance of a subclass of Term
        """
        return self

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Absolute",
                "value": self.value.as_dict(),
                "transform": self.transform}


class Negative(Term):
    """A class for computing the negative (invert the phase) of another term."""

    @staticmethod
    def factory(value, transform=False):    # pylint: disable=arguments-differ; this static method overrides a classmethod and does not need the cls argument
        """A class for computing the negative (invert the phase) of another term.

        This is a static factory method, that is meant to instantiate a
        :class:`~sumpf._data._filters._base._terms._unary.Negative` instance. But
        due to optimizations, it might return an instance of another subclass of
        :class:`~sumpf._data._filters._base._terms._base.Term`, if that is simpler
        and more efficient.

        :param value: a term
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        if transform:
            return -value.invert_transform()
        else:
            return -value

    def __init__(self, value, transform=False):
        """
        :param value: a term
        :param transform: True, if a lowpass-to-highpass-transformation shall be
                          performed, False otherwise
        """
        Term.__init__(self, transform=transform)
        self.value = value

    def _compute(self, s, out=None):
        """Implements the inversion of the phase.
        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        return numpy.negative(self.value(s, out=out), out=out)

    def is_zero(self):
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        return self.value.is_zero()

    def __repr__(self):
        """Operator overload for using the built-in function :func:`repr` to generate
        a string representation of the term, that can be evaluated with :func:`eval`.

        :returns: a potentially very long string
        """
        return "Filter.{class_}(value={value!r}, transform={transform})".format(class_=self.__class__.__name__,
                                                                                value=self.value,
                                                                                transform=self.transform)

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        if not isinstance(other, Negative):
            return False
        elif self.value != other.value:
            return False
        return super().__eq__(other)

    def __neg__(self):
        """An operator overload for inverting the phase of a terms with ``-term``.

        :returns: an instance of a subclass of Term
        """
        if self.transform:
            return self.value.invert_transform()
        else:
            return self.value

    def as_dict(self):
        """Returns a dictionary serialization of this term."""
        return {"type": "Negative",
                "value": self.value.as_dict(),
                "transform": self.transform}
