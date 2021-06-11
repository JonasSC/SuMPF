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

"""Contains the base class for terms with which the transfer functions of filters can be constructed."""

__all__ = ("Term",)


class Term:
    """A base class for mathematical terms, from which transfer functions can be constructed.
    All classes, that are derived from Term must implement at least the methods
    :meth:`~sumpf._data._filters._base._terms._base.Term._compute` ,
    :meth:`~sumpf._data._filters._base._terms._base.Term.__repr__` and most likely
    :meth:`~sumpf._data._filters._base._terms._base.Term.__eq__`. Overriding other
    methods is recommended, if the modeled operation allows optimizations of these
    methods.
    """

    @classmethod
    def factory(cls, *args, **kwargs):
        """A static factory method, that can be overridden to perform optimizations,
        which the constructor of the given class cannot do.

        :param `*args,**kwargs`: the constructor parameters of the given class
        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        return cls(*args, **kwargs)

    def __init__(self, transform):
        """
        :param transform: if True, a transformation s => 1/s will be performed
                          (e.g. for lowpass-to-highpass conversion).
        """
        self.transform = transform

    def __call__(self, s, out=None):
        """Samples the transfer function by evaluating the term for the given values of ``s``.

        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        if self.transform:
            s = s.transform()
        result = self._compute(s, out=out)
        return s.fix(result)

    def _compute(self, s, out):
        """An abstract method, in which sub-classes can implement their computations.

        :param s: an :class:`sumpf._data._filters._base._s.S` instance
        :param out: an optional array of complex values, in which the result shall
                    be stored (in order to save memory allocations)
        :returns: the computed transfer function as an array of complex values
        """
        raise NotImplementedError("This method has to be implemented in a derived class")

    def is_zero(self):  # pylint: disable=no-self-use; the overrides in derived classes do use self
        """Returns, whether this term evaluates to zero for all frequencies.
        For this check, the term is not evaluated. Instead, the parameters are
        analyzed statically, so maybe not all conditions, where the term evaluates
        to zero are covered.

        :returns: True, if the term evaluates to zero, False otherwise
        """
        return False

    def invert_transform(self):
        """Creates a copy of the term, with the lowpass-to-highpass-transform inverted.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        kwargs = self.__dict__.copy()
        kwargs["transform"] = not self.transform
        return self.__class__.factory(**kwargs)

    def as_dict(self):
        """Returns a dictionary serialization of this term, that can be passed to
        the static method :func:`~sumpf._internal._persistence._filter_readers.term_from_dict`
        to create a replica of this term. This dictionary has the class name stored
        under the "type" key, while the rest of the values are the keyword arguments
        of the constructor. If any of these arguments are :class:`~sumpf._data._filters._base._terms._base.Term` s
        themselves, they are also serialized as a dictionary.

        :returns: a dictionary
        """
        raise NotImplementedError("This method must be implemented by derived classes")

    def __repr__(self):
        """Makes sure, that all derived classes implement the overload for the
        built-in function :func:`repr`, which generates a string from which the
        given term can be reproduced with :func:`eval`. This is required for the
        implementation of :class:`~sumpf.Filter`.\ ``__repr__``.
        """
        raise NotImplementedError("This method must be implemented by derived classes")

    def __eq__(self, other):
        """An operator overload for comparing two terms with ``==``."""
        return self.transform == other.transform

    def __invert__(self):
        """A repurposed operator overload for inverting a terms with ``~term``.
        The inverse of a term is ``1 / term``.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        from ._primitive import Constant  # pylint: disable=cyclic-import,import-outside-toplevel
        from ._binary import Quotient     # pylint: disable=cyclic-import,import-outside-toplevel
        return Quotient(numerator=Constant(1.0), denominator=self)

    def __abs__(self):
        """An operator overload for computing the magnitude of a term with the
        built-in function :func:`abs`.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        from ._unary import Absolute      # pylint: disable=cyclic-import,import-outside-toplevel
        return Absolute(self)

    def __neg__(self):
        """An operator overload for inverting the phase of a terms with ``-term``.

        :returns: an instance of a subclass of :class:`~sumpf._data._filters._base._terms._base.Term`
        """
        from ._unary import Negative      # pylint: disable=cyclic-import,import-outside-toplevel
        return Negative(self)

    def __add__(self, other):
        """An operator overload for adding two terms with ``+``."""
        from ._binary import Sum          # pylint: disable=cyclic-import,import-outside-toplevel
        return Sum((self, other))

    def __sub__(self, other):
        """An operator overload for subtracting two terms with ``-``."""
        from ._binary import Difference   # pylint: disable=cyclic-import,import-outside-toplevel
        return Difference(self, other)

    def __mul__(self, other):
        """An operator overload for multiplying two terms with ``*``."""
        from ._binary import Product      # pylint: disable=cyclic-import,import-outside-toplevel
        return Product((self, other))

    def __truediv__(self, other):
        """An operator overload for dividing two terms with ``/``."""
        from ._binary import Quotient     # pylint: disable=cyclic-import,import-outside-toplevel
        return Quotient(self, other)
