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

import collections
import sumpf


def test_connection_observers(testcase, inputs, noinputs, output):
    """
    A function to test if an OutputConnector is affected by the correct inputs.
    @param testcase: the TestCase instance which shall raise an error if something is not as expected
    @param inputs: the inputs that shall affect the output
    @param noinputs: the inputs that shall not affect the output
    @param output: the output that shall be affected
    """
    try:
        # deep testing of connector dependencies
        class ConnectionTester(object):
            def __init__(self):
                self.triggered = False

            @sumpf.Trigger()
            def Trigger(self):
                self.triggered = True

            def Untrigger(self):
                result = self.triggered
                self.triggered = False
                return result

        def call_input_connector(connector):
            c = connector
            if isinstance(connector, sumpf.internal.ConnectorProxy):
                c = connector.GetConnector()
            if isinstance(c, sumpf.internal.TypedConnector):
                if c.GetType() in [int, float, complex]:
                    try:
                        c(c.GetType()(2.0))                 # try passing an even, non-zero value
                    except ValueError:
                        try:
                            c(c.GetType()(0.7))             # try passing a value between 0.0 and 1.0
                        except ValueError:
                            try:
                                c(c.GetType()(1.0))         # try passing one
                            except ValueError:
                                c(c.GetType()(0.0))         # try passing zero
                elif not issubclass(c.GetType(), str) and issubclass(c.GetType(), collections.Iterable):
                    try:
                        c(c.GetType()([1, 2]))      # pass an iterable with two integers with ascending value to avoid raising errors
                    except IndexError:
                        c(c.GetType()([0]))         # if an IndexError is raised, pass an iterable with the index that most likely exists
                else:
                    try:
                        c(c.GetType()())
                    except ValueError:
                        raise TypeError("Skip to shallow testing")
            else:
                c()

        ct = ConnectionTester()
        sumpf.connect(output, ct.Trigger)
        for i in inputs:
            call_input_connector(i)
            testcase.assertTrue(ct.Untrigger())
        for i in noinputs:
            call_input_connector(i)
            testcase.assertFalse(ct.Untrigger())
        sumpf.disconnect_all(ct)

    except TypeError:
        # shallow testing of connector dependencies, when automatic creation of
        # test parameters fails
        o = output
        if isinstance(output, sumpf.internal.ConnectorProxy):
            o = output.GetConnector()
        for i in inputs:
            testcase.assertIn(o, i.GetObservers())
        for i in noinputs:
            testcase.assertNotIn(o, i.GetObservers())

