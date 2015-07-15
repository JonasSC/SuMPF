# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
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
float32 = float
float64 = float
float128 = float

def get_iterable_depth(container):
    """
    a little helper function to find out of how many layers of iterables the
    container consists.
    """
    if isinstance(container, collections.Iterable):
        return 1 + get_iterable_depth(container[0])
    else:
        return 0

def add(a, b):
    """
    an alternative for numpy.add
    """
    result = []
    da = get_iterable_depth(a)
    db = get_iterable_depth(b)
    if da == 0 and db == 0:
        result = a + b
    elif da < db:
        for i in b:
            result.append(add(a, i))
        return result
    elif da > db:
        for i in a:
            result.append(add(i, b))
        return result
    else:
        for i in range(min(len(a), len(b))):
            result.append(add(a[i], b[i]))
    return result

def subtract(a, b):
    """
    an alternative for numpy.subtract
    """
    result = []
    da = get_iterable_depth(a)
    db = get_iterable_depth(b)
    if da == 0 and db == 0:
        result = a - b
    elif da < db:
        for i in b:
            result.append(subtract(a, i))
        return result
    elif da > db:
        for i in a:
            result.append(subtract(i, b))
        return result
    else:
        for i in range(min(len(a), len(b))):
            result.append(subtract(a[i], b[i]))
    return result

def multiply(a, b):
    """
    an alternative for numpy.multiply
    """
    result = []
    da = get_iterable_depth(a)
    db = get_iterable_depth(b)
    if da == 0 and db == 0:
        result = a * b
    elif da < db:
        for i in b:
            result.append(multiply(a, i))
        return result
    elif da > db:
        for i in a:
            result.append(multiply(i, b))
        return result
    else:
        for i in range(min(len(a), len(b))):
            result.append(multiply(a[i], b[i]))
    return result

def divide(a, b):
    """
    an alternative for numpy.divide
    """
    result = []
    da = get_iterable_depth(a)
    db = get_iterable_depth(b)
    if da == 0 and db == 0:
        result = a / b
    elif da < db:
        for i in b:
            result.append(divide(a, i))
        return result
    elif da > db:
        for i in a:
            result.append(divide(i, b))
        return result
    else:
        for i in range(min(len(a), len(b))):
            result.append(divide(a[i], b[i]))
    return result

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

def zeros(shape, dtype=float):
    """
    an alternative for numpy.zeros
    """
    if len(shape) == 0:
        return dtype(0.0)
    else:
        result = []
        for l in range(shape[0]):
            result.append(zeros(shape=shape[1:], dtype=dtype))
        return result

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

