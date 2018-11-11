# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import cmath
import collections
python_abs = abs

####################
# helper functions #
####################

def get_iterable_depth(container):
    """
    a helper function to find out of how many layers of iterables the container consists.
    """
    if isinstance(container, collections.Iterable):
        return 1 + get_iterable_depth(container[0])
    else:
        return 0

def algebra_base(a, b, function):
    """
    a base function, that manages the recursion of algebra functions for arrays.
    """
    result = []
    da = get_iterable_depth(a)
    db = get_iterable_depth(b)
    if da == 0 and db == 0:
        result = function(a, b)
    elif da < db:
        for i in b:
            result.append(algebra_base(a, i, function))
        return result
    elif da > db:
        for i in a:
            result.append(algebra_base(i, b, function))
        return result
    else:
        for i in range(max(len(a), len(b))):
            result.append(algebra_base(a[i % len(a)], b[i % len(b)], function))
    return result


################
# number types #
################

float32 = float
float64 = float
float128 = float

def complex_(x):
    """
    an alternative for numpy.complex_, which casts arrays to contain complex values.
    """
    if isinstance(x, collections.Iterable):
        result = []
        for i in x:
            result.append(complex_(i))
        return result
    else:
        return complex(x)


##########################################
# array generators and related functions #
##########################################

def zeros(shape, dtype=float):
    """
    an alternative for numpy.zeros
    """
    if len(shape) == 0:
        return dtype(0.0)
    else:
        result = []
        for _ in range(shape[0]):
            result.append(zeros(shape=shape[1:], dtype=dtype))
        return result

def shape(a):
    """
    an alternative to numpy.shape
    """
    if isinstance(a, collections.Iterable):
        if len(a) == 0:
            return (0,)
        else:
            return (len(a),) + shape(a[0])
    else:
        return ()


#####################
# algebra functions #
#####################

def add(a, b):
    """
    an alternative for numpy.add
    """
    return algebra_base(a, b, function=lambda c, d: c + d)

def subtract(a, b):
    """
    an alternative for numpy.subtract
    """
    return algebra_base(a, b, function=lambda c, d: c - d)

def multiply(a, b):
    """
    an alternative for numpy.multiply
    """
    return algebra_base(a, b, function=lambda c, d: c * d)

def divide(a, b):
    """
    an alternative for numpy.divide
    """
    return algebra_base(a, b, function=lambda c, d: c / d)

def true_divide(a, b):
    """
    an alternative for numpy.true_divide
    """
    def function(c, d):
        if isinstance(c, int):
            c = float(c)
        return c / d
    return algebra_base(a, b, function)

def mod(a, b):
    """
    an alternative for numpy.mod
    """
    return algebra_base(a, b, function=lambda c, d: c % d)

def power(a, b):
    """
    an alternative for numpy.power
    """
    return algebra_base(a, b, function=lambda c, d: c ** d)


########################
# monadic computations #
########################

def abs(x):
    """
    an alternative for numpy.abs
    """
    if isinstance(x, collections.Iterable):
        result = []
        for i in x:
            result.append(abs(i))
        return result
    else:
        return python_abs(x)

def angle(x):
    """
    an alternative for numpy.angle
    """
    if isinstance(x, collections.Iterable):
        result = []
        for i in x:
            result.append(angle(i))
        return result
    else:
        return cmath.phase(x)

def real(x):
    """
    an alternative for numpy.real
    this does not model numpy's behaviour, that real returns an array for a scalar
    input.
    """
    if isinstance(x, collections.Iterable):
        result = []
        for i in x:
            result.append(real(i))
        return result
    elif isinstance(x, complex):
        return x.real
    else:
        return x

def imag(x):
    """
    an alternative for numpy.imag
    this does not model numpy's behaviour, that imag returns an array for a scalar
    input.
    """
    if isinstance(x, collections.Iterable):
        result = []
        for i in x:
            result.append(imag(i))
        return result
    elif isinstance(x, complex):
        return x.imag
    else:
        return 0.0

def conjugate(x):
    """
    an alternative for numpy.conjugate
    """
    if isinstance(x, collections.Iterable):
        result = []
        for i in x:
            if isinstance(i, complex):
                result.append(i.conjugate())
            else:
                result.append(i)
        return result
    else:
        if isinstance(x, complex):
            return x.conjugate()
        else:
            return x

def transpose(a):
    """
    an alternative for numpy.transpose
    this only works for one- and twodimensional arrays as expected.
    """
    if not isinstance(a, collections.Iterable):
        return a
    elif isinstance(a[0], collections.Iterable):
        return tuple(zip(*a))
    else:
        return a

########################################
# array functions with a scalar result #
########################################

def min(*args):
    """
    an alternative to numpy.min
    """
    if len(args) == 1:
        a = args[0]
    else:
        a = args
    if isinstance(a, collections.Iterable):
        if len(a) == 0:
            raise ValueError("zero-size array to reduction operation minimum which has no identity")
        minimum = min(a[0])
        for b in a[1:]:
            m = min(b)
            if m < minimum:
                minimum = m
        return minimum
    else:
        return a

def max(*args):
    """
    an alternative to numpy.max
    """
    if len(args) == 1:
        a = args[0]
    else:
        a = args
    if isinstance(a, collections.Iterable):
        if len(a) == 0:
            raise ValueError("zero-size array to reduction operation maximum which has no identity")
        maximum = max(a[0])
        for b in a[1:]:
            m = max(b)
            if maximum < m:
                maximum = m
        return maximum
    else:
        return a

def sum(a):
    """
    an alternative to numpy.sum
    """
    if isinstance(a, collections.Iterable):
        result = 0.0
        for b in a:
            result += sum(b)
        return result
    else:
        return a

def prod(a):
    """
    an alternative to numpy.prod
    """
    if isinstance(a, collections.Iterable):
        result = 1.0
        for b in a:
            result *= prod(b)
        return result
    else:
        return a

def mean(a):
    """
    A simplified alternative to numpy.mean.
    Other than numpy.mean, this function only takes one dimensional arrays.
    """
    return sum(a) / float(len(a))

def var(a):
    """
    A simplified alternative to numpy.var.
    Other than numpy.mean, this function only takes one dimensional arrays.
    Furthermore, it does not calculate the variance of complex values correctly.
    So please use it for real valued arrays only.
    """
    squared = multiply(a, a)
    return mean(squared) - mean(a) ** 2


########################
# evaluation functions #
########################

def equal(a, b):
    """
    an alternative for numpy.equal
    """
    return algebra_base(a, b, function=lambda c, d: c == d)

def nonzero(a):
    """
    an alternative to numpy.nonzero
    """
    if isinstance(a, collections.Iterable):
        if len(a) == 0:
            return ((),)
        else:
            def recursion(array, path):
                result = []
                for i, b in enumerate(array):
                    if isinstance(b, collections.Iterable):
                        result.extend(recursion(b, path=path + (i,)))
                    elif b != 0.0:
                        result.append(path + (i,))
                return tuple(result)
            return tuple(zip(*recursion(a, ())))
    else:
        if a != 0:
            return ((0,),)
        else:
            return ((),)

