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

import random
import unittest
import sumpf

try:
    import numpy
except ImportError:
    sumpf.helper.numpydummy


class TestAverage(unittest.TestCase):
    """
    A TestCase for the averaging classes.
    """
    def test_basics(self):
        """
        Tests the basic stuff for all averaging classes.
        """
        for i in [sumpf.helper.average.SumDirectly, sumpf.helper.average.SortedSum, sumpf.helper.average.SumList]:
            avg = i()
            self.assertEqual(avg.GetAverage(), 0.0)                 # an averaging object with no added values should return an average of 0.0
            avg.Add([1.0, 2.0, 3.0])
            avg.Add([3.0, 2.0, 1.0])
            self.assertEqual(avg.GetAverage(), [2.0, 2.0, 2.0])     # averaging lists and adding values with the Add method should work
            avg = i(values=[13, 10])
            avg.Add(13)
            avg.Add(2.0)
            self.assertEqual(avg.GetAverage(), 9.5)                 # averaging over scalars (even integers) and adding values with the constructor should work
            avg.Add(12.0j)
            self.assertAlmostEqual(avg.GetAverage(), 7.6 + 2.4j)    # averaging over complex numbers should work

    @unittest.skipUnless(sumpf.config.get("run_incomplete_tests"), "Incomplete tests are skipped")
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(sumpf.config.get("run_time_variant_tests"), "Tests which are testing random numbers are skipped")
    def test_precision(self):
        """
        Tests if the errors due to limited floating point precision are reduced
        by the more complex averaging algorithms.
        Somehow the SumDirectly algorithm seems to be more precise than the
        slightly more sophisticated SortedSum algorithm. Maybe this is because
        Python can optimize simple algorithms by itself. But since this test
        expects the SortedSum algorithm to be more exact, this test fails almost
        each time it is run, so it is marked as incomplete.
        """
        # create some random values
        values = []
        for i in range(2 ** 10 - 1):
            values.append(random.gauss(0.0, 1.0))
        # initialize some averages with the random values
        avg1 = sumpf.helper.average.SumDirectly(values=values)
        avg2 = sumpf.helper.average.SortedSum(values=values)
        avg3 = sumpf.helper.average.SumList(values=values)
        # calculate a very precise average
        summed = numpy.float128(0.0)
        for v in sorted(values):
            summed += numpy.float128(v)
        average = summed / numpy.float128(len(values))
        # calculate the errors of the averaging algorithms
        e1 = abs(avg1.GetAverage() - average)
        e2 = abs(avg2.GetAverage() - average)
        e3 = abs(avg3.GetAverage() - average)
        # compare their performance
        self.assertGreaterEqual(e1, e2)     # the SortedSum algorithm is expected to be more precise than the SumDirectly algorithm
        self.assertGreaterEqual(e2, e3)     # the SumList algorithm is expected to be more precise than the SortedSum algorithm

