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

import math
import unittest
import warnings
import sumpf
import _common as common
try:
    import numpy
except ImportError:
    pass


class TestAlgebra(unittest.TestCase):
    """
    A test case for the algebra modules.
    """
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_signals(self):
        """
        Tests if the calculations yield the expected results with signals.
        """
        # disable some numpy warnings
        warnings.filterwarnings(action="ignore", message="^divide by zero encountered in divide$", category=RuntimeWarning)
        warnings.filterwarnings(action="ignore", message="^divide by zero encountered in true_divide$", category=RuntimeWarning)
        warnings.filterwarnings(action="ignore", message="^divide by zero encountered in power$", category=RuntimeWarning)
        warnings.filterwarnings(action="ignore", message="^invalid value encountered in power$", category=RuntimeWarning)
        # perform the tests
        signal1 = sumpf.Signal(channels=((4.0, -6.0, 9.34), (3.0, 5.0, -8.4)), samplingrate=62.33)
        signal2 = sumpf.Signal(channels=((2.0, 1.0, -14.2), (-3.0, 7.0, 2.1)), samplingrate=62.33)
        empty = sumpf.Signal(samplingrate=62.33)
        wrongchannelcount = sumpf.Signal(channels=((-2.0, 1.0, 14.2),), samplingrate=62.33)
        wrongsamplingrate = sumpf.Signal(channels=((2.0, 1.0, -14.2), (3.0, -7.0, 2.1)), samplingrate=59.78)
        scalar = 4.74
        array = (4.2, -5.5)
        self.__TestComputationsAndExceptions(test_data1=(signal1, empty, wrongchannelcount, wrongsamplingrate, scalar, array, None, 0.0),
                                             test_data2=(signal2, empty, wrongchannelcount, wrongsamplingrate, scalar, array, None, 0))

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_spectrums(self):
        """
        Tests if the calculations yield the expected results with signals.
        """
        spectrum1 = sumpf.Spectrum(channels=((-4.0 + 1.9j, 6.0 + 7.3j, -9.34), (3.0 - 6.6j, -5.0, 8.4 + 9.4j)), resolution=62.33)
        spectrum2 = sumpf.Spectrum(channels=((2.0 - 4.4j, -1.0 + 3.6j, -14.2 - 1.6j), (3.0 + 4.2j, -7.0 - 6.4j, 2.1 - 9.8j)), resolution=62.33)
        empty = sumpf.Spectrum(resolution=62.33)
        wrongchannelcount = sumpf.Spectrum(channels=((-2.0 + 5.3j, 1.0 + 1.1j, 14.2 - 3.6j),), resolution=62.33)
        wrongresolution = sumpf.Spectrum(channels=((2.0 + 6.3j, -1.0 - 4.4j, 14.2 - 2.0j), (-3.0 + 3.1j, 7.0 - 3.8j, 2.1 + 4.7j)), resolution=59.78)
        scalar = 4.74 + 12.5j
        array = (4.2, -5.5)
        self.__TestComputationsAndExceptions(test_data1=(spectrum1, empty, wrongchannelcount, wrongresolution, scalar, array, None),
                                             test_data2=(spectrum2, empty, wrongchannelcount, wrongresolution, scalar, array, 0))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        for m in [sumpf.modules.Add(),
                  sumpf.modules.Subtract(),
                  sumpf.modules.Multiply(),
                  sumpf.modules.Divide(),
                  sumpf.modules.Power()]:
            self.assertEqual(m.SetValue1.GetType(), None)
            self.assertEqual(m.SetValue2.GetType(), None)
            self.assertEqual(m.GetResult.GetType(), None)
            common.test_connection_observers(testcase=self,
                                             inputs=[m.SetValue1, m.SetValue2],
                                             noinputs=[],
                                             output=m.GetResult)

    def __TestComputationsAndExceptions(self, test_data1, test_data2):
        for a in test_data1:
            for b in test_data2:
                # add
                try:
                    c = a + b
                except AttributeError:
                    self.assertRaises(AttributeError, sumpf.modules.Add(value1=a, value2=b).GetResult)
                except TypeError:
                    try:
                        c = numpy.add(a, b)
                    except TypeError:
                        self.assertRaises(TypeError, sumpf.modules.Add(value1=a, value2=b).GetResult)
                    except ValueError:
                        self.assertRaises(ValueError, sumpf.modules.Add(value1=a, value2=b).GetResult)
                    else:
                        self.assertEqual(sum(numpy.subtract(sumpf.modules.Add(value1=a, value2=b).GetResult(), c)), 0.0)
                except ValueError:
                    self.assertRaises(ValueError, sumpf.modules.Add(value1=a, value2=b).GetResult)
                else:
                    self.assertEqual(sumpf.modules.Add(value1=a, value2=b).GetResult(), c)
                # subtract
                try:
                    c = a - b
                except AttributeError:
                    self.assertRaises(AttributeError, sumpf.modules.Subtract(value1=a, value2=b).GetResult)
                except TypeError:
                    try:
                        c = numpy.subtract(a, b)
                    except TypeError:
                        self.assertRaises(TypeError, sumpf.modules.Subtract(value1=a, value2=b).GetResult)
                    except ValueError:
                        self.assertRaises(ValueError, sumpf.modules.Subtract(value1=a, value2=b).GetResult)
                    else:
                        self.assertEqual(sum(numpy.subtract(sumpf.modules.Subtract(value1=a, value2=b).GetResult(), c)), 0.0)
                except ValueError:
                    self.assertRaises(ValueError, sumpf.modules.Subtract(value1=a, value2=b).GetResult)
                else:
                    self.assertEqual(sumpf.modules.Subtract(value1=a, value2=b).GetResult(), c)
                # multiply
                try:
                    c = a * b
                except AttributeError:
                    self.assertRaises(AttributeError, sumpf.modules.Multiply(value1=a, value2=b).GetResult)
                except TypeError:
                    try:
                        c = numpy.multiply(a, b)
                    except TypeError:
                        self.assertRaises(TypeError, sumpf.modules.Multiply(value1=a, value2=b).GetResult)
                    except ValueError:
                        self.assertRaises(ValueError, sumpf.modules.Multiply(value1=a, value2=b).GetResult)
                    else:
                        self.assertEqual(sum(numpy.subtract(sumpf.modules.Multiply(value1=a, value2=b).GetResult(), c)), 0.0)
                except ValueError:
                    self.assertRaises(ValueError, sumpf.modules.Multiply(value1=a, value2=b).GetResult)
                else:
                    self.assertEqual(sumpf.modules.Multiply(value1=a, value2=b).GetResult(), c)
                # divide
                try:
                    c = a / b
                except AttributeError:
                    self.assertRaises(AttributeError, sumpf.modules.Divide(value1=a, value2=b).GetResult)
                except TypeError:
                    try:
                        c = numpy.divide(a, b)
                    except TypeError:
                        self.assertRaises(TypeError, sumpf.modules.Divide(value1=a, value2=b).GetResult)
                    except ValueError:
                        self.assertRaises(ValueError, sumpf.modules.Divide(value1=a, value2=b).GetResult)
                    else:
                        for m, r in zip(sumpf.modules.Divide(value1=a, value2=b).GetResult(), c):
                            if numpy.isnan(r):
                                self.assertTrue(math.isnan(m))
                            else:
                                self.assertEqual(m, r)
                except ValueError:
                    self.assertRaises(ValueError, sumpf.modules.Divide(value1=a, value2=b).GetResult)
                except ZeroDivisionError:
                    self.assertRaises(ZeroDivisionError, sumpf.modules.Divide(value1=a, value2=b).GetResult)
                else:
                    result = sumpf.modules.Divide(value1=a, value2=b).GetResult() == c
                    if isinstance(result, bool):
                        self.assertTrue(result)
                    else:
                        self.assertTrue(result.all())
                # power
                try:
                    c = a ** b
                except AttributeError:
                    self.assertRaises(AttributeError, sumpf.modules.Power(value1=a, value2=b).GetResult)
                except TypeError:
                    try:
                        c = numpy.power(a, b)
                    except TypeError:
                        self.assertRaises(TypeError, sumpf.modules.Power(value1=a, value2=b).GetResult)
                    except ValueError:
                        self.assertRaises(ValueError, sumpf.modules.Power(value1=a, value2=b).GetResult)
                    else:
                        for m, r in zip(sumpf.modules.Power(value1=a, value2=b).GetResult(), c):
                            if numpy.isnan(r):
                                self.assertTrue(math.isnan(m))
                            else:
                                self.assertEqual(m, r)
                except ValueError:
                    self.assertRaises(ValueError, sumpf.modules.Power(value1=a, value2=b).GetResult)
                except ZeroDivisionError:
                    self.assertRaises(ZeroDivisionError, sumpf.modules.Power(value1=a, value2=b).GetResult)
                else:
                    self.assertEqual(sumpf.modules.Power(value1=a, value2=b).GetResult(), c)

