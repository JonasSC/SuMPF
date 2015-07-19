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

import gc
import unittest

import sumpf

import _common as common
from .exampleclasses import ExampleClass, SetMultipleValuesTestClass


class TestConnectors(unittest.TestCase):
    """
    A TestCase for the connections and the related functions.
    """
    def setUp(self):
        self.obj1 = ExampleClass()
        self.obj2 = ExampleClass()

    def tearDown(self):
        sumpf.collect_garbage()

    def test_setter_and_getter(self):
        """
        Tests if the getter and setter methods work as expected.
        """
        self.obj1.SetValue(1)
        self.assertEqual(self.obj1.GetValue(), 1)
        self.assertTrue(isinstance(self.obj1.GetValue(), int))
        self.obj1.SetValueNoUpdate(2)
        self.assertEqual(self.obj1.GetValue(), 2)

    def test_get_type(self):
        """
        Tests the GetType() method of the decorators and the connectors.
        """
        v = vars(ExampleClass)  # somehow expressions like ExampleClass.GetValue.GetType() do not work
        self.assertEqual(v["GetValue"].GetType(), self.obj1.GetValue.GetType())
        self.assertEqual(v["GetValue2"].GetType(), self.obj1.GetValue2.GetType())
        self.assertEqual(v["SetValue"].GetType(), self.obj1.SetValue.GetType())
        self.assertEqual(v["SetValue2"].GetType(), self.obj1.SetValue2.GetType())
        self.assertEqual(v["SetValueNoUpdate"].GetType(), self.obj1.SetValueNoUpdate.GetType())
        self.assertEqual(v["GetFloat"].GetType(), self.obj1.GetFloat.GetType())
        self.assertEqual(v["GetText"].GetType(), self.obj1.GetText.GetType())
        self.assertEqual(v["SetText"].GetType(), self.obj1.SetText.GetType())
        self.assertEqual(v["ComputeValueAndText"].GetType(), self.obj1.ComputeValueAndText.GetType())
        self.assertRaises(AttributeError, getattr, v["Trigger"], "GetType")
        self.assertEqual(v["GetItems"].GetType(), self.obj1.GetItems.GetType())
        self.assertEqual(v["AddItemNoReplace"].GetType(), self.obj1.AddItemNoReplace.GetType())
        self.assertEqual(v["AddItemReplace"].GetType(), self.obj1.AddItemReplace.GetType())
        self.assertEqual(v["TakeList"].GetType(), self.obj1.TakeList.GetType())

    def test_make_valid_connections(self):
        """
        Makes and brakes some valid connections and tests if the values are passed correctly through the connections.
        """
        self.obj1.SetValue(1)
        self.obj2.SetValue(2)
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
        self.assertEqual(self.obj2.GetValue(), 1)               # by making the connection, the value should have been passed automatically
        self.obj1.SetValue(3)
        self.assertEqual(self.obj2.GetValue(), 3)               # the value should have been passed through the connection automatically
        sumpf.disconnect(self.obj1.GetValue, self.obj2.SetValue)
        self.obj1.SetValue(4)
        self.assertEqual(self.obj2.GetValue(), 3)               # after disconnection the passing should have stopped
        sumpf.connect(self.obj2.SetValue, self.obj1.GetValue)
        self.obj1.SetValue(5)
        self.assertEqual(self.obj2.GetValue(), 5)               # changing the order of arguments in the connect-call should have worked aswell
        self.obj1.SetValueNoUpdate(6)
        self.assertEqual(self.obj2.GetValue(), 5)               # a decorator with no automatic passing should be possible aswell
        sumpf.disconnect(self.obj2.SetValue, self.obj1.GetValue)
        self.obj1.SetValue(7)
        self.assertEqual(self.obj2.GetValue(), 5)               # changing the order of arguments in the disconnect-call should have worked aswell
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
        sumpf.connect(self.obj1.GetText, self.obj2.SetText)
        self.obj1.ComputeValueAndText(8)
        self.assertEqual(self.obj2.GetValue(), 8)               # ComputeValueAndText should have triggered both connections. GetValue...
        self.assertEqual(self.obj2.GetText(), "8")              # ... and GetText
        self.obj2.triggered = False
        sumpf.connect(self.obj1.GetText, self.obj2.Trigger)     # multiple connections from an output should be possible
        sumpf.connect(self.obj1.GetValue, self.obj2.Trigger)    # multiple connections to a Trigger should be possible
        self.assertFalse(self.obj2.triggered)                   # Triggers should not be triggered on connection
        self.obj1.SetValue(9)
        self.assertTrue(self.obj2.triggered)                    # Triggers should work as well
        self.obj1.SetText(text="Hallo Welt")                    # Keyword arguments should be possible
        sumpf.connect(self.obj1.GetFloat, self.obj2.SetValue2)  # This Input shall be connectable to both floats...
        sumpf.disconnect(self.obj1.GetFloat, self.obj2.SetValue2)
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue2)  # ... and integers.

    def test_non_replacing_multi_input(self):
        """
        Testing every aspect of a MultiInput is more complex, so it is done in
        separately in this and the next method.
        This method tests the MultiInput that replaces updated data by removing
        the old data and adding the new one. This will destroy the order of the
        output data.
        """
        id0 = self.obj2.AddItemNoReplace(0)
        id1 = self.obj2.AddItemNoReplace(1)
        self.assertEqual(self.obj2.GetItems(), [0, 1])                  # adding items manually should work
        self.obj1.SetValue(2)
        sumpf.connect(self.obj1.GetValue, self.obj2.AddItemNoReplace)
        self.assertEqual(self.obj2.GetItems(), [0, 1, 2])               # adding items through connections should work
        self.obj1.SetValue(3)
        self.assertEqual(self.obj2.GetItems(), [0, 1, 3])               # a connection should only update its own value
        sumpf.connect(self.obj1.GetValue2, self.obj2.AddItemNoReplace)
        self.assertEqual(self.obj2.GetItems(), [0, 1, 3, 6])            # multiple connections must be possible
        sumpf.connect(self.obj2.GetItems, self.obj1.Trigger)
        self.obj1.triggered = False
        sumpf.disconnect(self.obj1.GetValue, self.obj2.AddItemNoReplace)
        self.assertTrue(self.obj1.triggered)                            # disconnecting should have triggered the Trigger
        self.assertEqual(self.obj2.GetItems(), [0, 1, 6])               # disconnecting should remove the item from the list
        self.obj2.RemoveItem(id1)
        self.assertEqual(self.obj2.GetItems(), [0, 6])                  # removing items manually should work as well
        self.obj2.AddItemNoReplace(7)
        self.obj1.SetValue2(2)
        self.assertEqual(self.obj2.GetItems(), [0, 7, 4])               # the connection should still work, even after many changes

    def test_replacing_multi_input(self):
        """
        Testing every aspect of a MultiInput is more complex, so it is done in
        separately in this and the next method.
        This method tests the MultiInput that replace updated data with a proper
        replacing method. This should maintain the order of the output data.
        """
        id0 = self.obj2.AddItemReplace(0)
        id1 = self.obj2.AddItemReplace(1)
        self.assertEqual(self.obj2.GetItems(), [0, 1])                  # adding items manually should work
        self.obj1.SetValue(2)
        sumpf.connect(self.obj1.GetValue, self.obj2.AddItemReplace)
        self.assertEqual(self.obj2.GetItems(), [0, 1, 2])               # adding items through connections should work
        self.obj1.SetValue(3)
        self.assertEqual(self.obj2.GetItems(), [0, 1, 3])               # a connection should only update its own value
        sumpf.connect(self.obj1.GetValue2, self.obj2.AddItemReplace)
        self.assertEqual(self.obj2.GetItems(), [0, 1, 3, 6])            # multiple connections must be possible
        sumpf.connect(self.obj2.GetItems, self.obj1.Trigger)
        self.obj1.triggered = False
        sumpf.disconnect(self.obj1.GetValue, self.obj2.AddItemReplace)
        self.assertTrue(self.obj1.triggered)                            # disconnecting should have triggered the Trigger
        self.assertEqual(self.obj2.GetItems(), [0, 1, 6])               # disconnecting should remove the item from the list
        self.obj2.RemoveItem(id1)
        self.assertEqual(self.obj2.GetItems(), [0, 6])                  # removing items manually should work as well
        self.obj2.AddItemReplace(7)
        self.obj1.SetValue2(2)
        self.assertEqual(self.obj2.GetItems(), [0, 4, 7])               # the connection should still work, even after many changes

    def test_multiinput_method_override(self):
        """
        Tests if the remove and replace methods are overridden as expected.
        """
        self.obj1.AddItemReplace(4)     # trigger the replacement of the methods
        self.obj1.AddItemNoReplace(1)   #
        self.obj1.ThirdMultiInput(9)    #
        self.assertIsInstance(self.obj1.RemoveItem, sumpf.internal.Connector)               # the RemoveItem method should have been overridden with a Connector instance
        self.assertIsInstance(self.obj1.ReplaceItem, sumpf.internal.Connector)              # the ReplaceItem method should have been overridden with a Connector instance
        self.assertNotIsInstance(self.obj1.RemoveItem._method, sumpf.internal.Connector)    # the RemoveItem method should not have been overridden multiple times by the many MultiInputs
        self.assertNotIsInstance(self.obj1.ReplaceItem._method, sumpf.internal.Connector)   # the ReplaceItem method should not have been overridden multiple times by the many MultiInputs

    def test_make_invalid_connections(self):
        """
        Tries to make and brake some invalid connections and tests if the mistakes are correctly detected.
        """
        self.assertRaises(TypeError, sumpf.connect, *(self.obj1.GetText, self.obj2.SetValue2))              # connecting should fail if the types of the connectors are different
        self.assertRaises(TypeError, sumpf.connect, *(self.obj1.GetValue, self.obj2.GetValue))              # connecting should fail if both connectors are outputs
        self.assertRaises(TypeError, sumpf.connect, *(self.obj1.SetValue, self.obj2.SetValue))              # connecting should fail if both connectors are inputs
        self.assertRaises(ValueError, sumpf.connect, *(self.obj1.GetValue, self.obj1.SetValue))             # connecting should fail if the output is connected to an input that updates the output automatically, because that would cause an infinite loop
        sumpf.connect(self.obj1.GetValue, self.obj1.SetValueNoUpdate)
        self.assertRaises(ValueError, sumpf.connect, *(self.obj1.GetValue, self.obj1.SetValueNoUpdate))     # connecting should fail if the connection already exists
        self.assertRaises(ValueError, sumpf.connect, *(self.obj1.GetValue2, self.obj1.SetValueNoUpdate))    # connecting should fail if input is already connected
        self.assertRaises(ValueError, sumpf.disconnect, *(self.obj1.GetValue, self.obj2.SetValue))          # disconnecting should fail if connection does not exist
        sumpf.disconnect(self.obj1.GetValue, self.obj1.SetValueNoUpdate)
        self.assertRaises(ValueError, sumpf.disconnect, *(self.obj1.GetValue, self.obj1.SetValueNoUpdate))  # disconnecting should fail if connection does not exist. Even if it has existed before

    def test_order(self):
        """
        Tests if connections are updated in the correct order.
        """
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue2)
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValueNoUpdate)
        self.obj2.order = []
        self.obj1.SetValue(1)
        self.assertEqual(self.obj2.order, ["SetValue", "SetValue2", "SetValueNoUpdate"])    # All items should appear in the correct order
        sumpf.disconnect(self.obj1.GetValue, self.obj2.SetValue2)
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue2)
        self.obj2.order = []
        self.obj1.SetValue(2)
        self.assertEqual(self.obj2.order, ["SetValue", "SetValueNoUpdate", "SetValue2"])    # All items should appear in the correct order

    def test_caching(self):
        """
        Tests if the caching of values is working.
        """
        self.assertEqual(type(self.obj1.GetValue2.GetConnector()).__name__, "CachingOutputConnector")   # GetValue should always cache
        self.assertEqual(type(self.obj1.GetText.GetConnector()).__name__, "NotCachingOutputConnector")  # GetText should never cache
        self.obj1.SetValue2(1)
        self.assertEqual(self.obj1.GetValue2(), 2)                                       # setter with observers should work normally
        self.obj1.SetValueNoUpdate(2)
        self.assertEqual(self.obj1.GetValue2(), 2)                                       # setter without observers should not trigger recalculation of cached values

    def test_disconnect_all(self):
        """
        Tests if the disconnect_all function works as expected.
        """
        sumpf.connect(self.obj1.GetValue, self.obj2.Trigger)
        sumpf.connect(self.obj1.GetText, self.obj2.Trigger)
        sumpf.disconnect_all(self.obj2.Trigger)
        self.obj2.triggered = False
        self.obj1.SetValue(1)
        self.obj1.SetText("1")
        self.assertFalse(self.obj2.triggered)                           # disconnect_all should have removed all connections to GetTriggered
        sumpf.connect(self.obj1.GetValue, self.obj2.Trigger)
        sumpf.connect(self.obj1.GetText, self.obj2.Trigger)
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
        sumpf.connect(self.obj1.GetValue2, self.obj2.SetValueNoUpdate)
        sumpf.connect(self.obj2.GetValue, self.obj1.SetValueNoUpdate)
        sumpf.connect(self.obj1.GetValue, self.obj2.AddItemNoReplace)
        sumpf.connect(self.obj1.GetValue2, self.obj2.AddItemNoReplace)
        sumpf.disconnect_all(self.obj2)
        self.obj2.SetValue(3)
        self.assertEqual(self.obj1.GetValue(), 2)                       # disconnect_all should have removed the connection from obj2.GetValue to obj1.SetValueNoUpdate
        self.obj2.SetText("3")
        self.obj2.triggered = False
        self.obj1.SetValue(2)
        self.obj1.SetText("2")
        self.assertEqual(self.obj2.GetValue(), 3)                       # disconnect_all should have removed all connections to obj2
        self.assertEqual(self.obj2.GetText(), "3")                      # disconnect_all should have removed all connections to obj2
        self.assertFalse(self.obj2.triggered)                           # disconnect_all should have removed all connections to obj2
        self.assertEqual(set(self.obj2.GetItems()), set())              # disconnect_all should have removed all connections to obj2

    def test_deactivate_output(self):
        """
        Tests if deactivating and reactivating outputs works.
        """
        self.obj1.SetValue(0)
        self.obj2.SetValue(1)
        sumpf.deactivate_output(self.obj1.GetValue)
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
        self.assertEqual(self.obj2.GetValue(), 1)               # A deactivated output shall not be passed while creating a connection
        sumpf.activate_output(self.obj1.GetValue)
        sumpf.connect(self.obj1.GetText, self.obj2.SetText)
        self.obj1.ComputeValueAndText(2)
        sumpf.deactivate_output(self.obj1)
        sumpf.deactivate_output(self.obj1)                      # Deactivating already deactivated outputs should not fail
        self.obj1.ComputeValueAndText(3)
        self.assertEqual(self.obj2.GetValue(), 2)               # No value should be passed through deactivated outputs
        sumpf.activate_output(self.obj1.GetValue)
        self.assertEqual(self.obj2.GetValue(), 3)               # Value should have been passed through reactivated output
        self.assertEqual(self.obj2.GetText(), "2")              # Text output should have remained deactivated
        sumpf.activate_output(self.obj1)
        self.assertEqual(self.obj2.GetText(), "3")              # Text should have been passed while globally enabling outputs

    def test_set_multiple_values(self):
        """
        Tests the set_multiple_values function.
        Most assertions will be don in the SetMultipleValuesTestClass class.
        """
        # test with single Inputs
        testobject = SetMultipleValuesTestClass(testcase=self)
        sumpf.connect(testobject.GetState, self.obj1.SetValue)
        testobject.Start()
        sumpf.set_multiple_values(pairs=[(testobject.SetValue1, 37.9),
                                         (testobject.SetValue2, "Broccoli"),
                                         (testobject.TriggerValue3,)])
        self.assertEqual(testobject.GetValue1(), 37.9)
        self.assertEqual(testobject.GetValue2(), "Broccoli")
        self.assertEqual(testobject.GetValue3(), True)
        # test with a MultiInput
        sumpf.set_multiple_values(pairs=[(testobject.AddValue4, 1),
                                         (testobject.AddValue4, 2),
                                         (testobject.AddValue4, 3)])
        self.assertEqual(testobject.GetValue4().GetData(), [1, 2, 3])

    def test_duplicate_calculation(self):
        """
        Tests if duplicate calculation in forked chains is avoided.
        """
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue2)
        sumpf.connect(self.obj2.GetValue, self.obj1.SetValueNoUpdate)
        self.obj2.history = []
        self.obj1.SetValue(1)
        self.assertEqual(self.obj2.history, [1])                        # the value should have been calculated only once
        sumpf.deactivate_output(self.obj1)
        self.obj2.history = []
        self.obj1.SetValue(2)
        sumpf.activate_output(self.obj1)
        self.assertEqual(self.obj2.history, [2])                        # the value should have been calculated only once after reactivating outputs
        sumpf.disconnect_all(self.obj1)
        sumpf.connect(self.obj1.GetValue, self.obj2.AddItemNoReplace)
        sumpf.connect(self.obj1.GetValue2, self.obj2.AddItemNoReplace)
        sumpf.connect(self.obj2.GetItems, self.obj1.TakeList)
        self.obj2.history = []
        self.obj1.SetValue2(3)
        self.assertEqual(self.obj2.history, [[3, 6]])                   # the list should have been calculated only once

    def test_docstrings(self):
        """
        Checks that the docstrings of the decorated methods remain the same.
        """
        self.assertEqual(self.obj1.GetValue.__doc__, "\n        Output with data_type int\n        ")                   # The Output decorator should not modify the docstring of the method
        self.assertEqual(self.obj1.SetValue.__doc__, "\n        Input with data_type int and one observer\n        ")   # The Input decorator should not modify the docstring of the method
        self.assertEqual(self.obj1.Trigger.__doc__, "\n        A trigger with observer\n        ")                      # The Trigger decorator should not modify the docstring of the method
        self.assertEqual(self.obj1.AddItemNoReplace.__doc__, "\n        A MultiInput\n        ")                        # The MultiInput decorator should not modify the docstring of the method
        self.assertEqual(self.obj1.RemoveItem.__doc__, "\n        Every MultiInput needs a remove-method\n        ")    # The MultiInput decorator should not modify the docstring of its remove method

    def test_connector_names(self):
        """
        Tests the GetName method of the connectors.
        """
        self.assertEqual(self.obj1.GetValue.GetName(), "ExampleClass.GetValue")
        self.assertEqual(self.obj1.GetValue2.GetName(), "ExampleClass.GetValue2")
        self.assertEqual(self.obj1.SetValue.GetName(), "ExampleClass.SetValue")
        self.assertEqual(self.obj1.SetValue2.GetName(), "ExampleClass.SetValue2")
        self.assertEqual(self.obj1.SetValueNoUpdate.GetName(), "ExampleClass.SetValueNoUpdate")
        self.assertEqual(self.obj1.GetFloat.GetName(), "ExampleClass.GetFloat")
        self.assertEqual(self.obj1.GetText.GetName(), "ExampleClass.GetText")
        self.assertEqual(self.obj1.SetText.GetName(), "ExampleClass.SetText")
        self.assertEqual(self.obj1.ComputeValueAndText.GetName(), "ExampleClass.ComputeValueAndText")
        self.assertEqual(self.obj1.Trigger.GetName(), "ExampleClass.Trigger")
        self.assertEqual(self.obj1.GetItems.GetName(), "ExampleClass.GetItems")
        self.assertEqual(self.obj1.AddItemNoReplace.GetName(), "ExampleClass.AddItemNoReplace")
        self.assertEqual(self.obj1.AddItemReplace.GetName(), "ExampleClass.AddItemReplace")
        self.assertEqual(self.obj1.RemoveItem.GetName(), "ExampleClass.RemoveItem")
        self.assertEqual(self.obj1.ReplaceItem.GetName(), "ExampleClass.ReplaceItem")
        self.assertEqual(self.obj1.TakeList.GetName(), "ExampleClass.TakeList")

    def test_object_deletion(self):
        """
        Checks that Connectors do not inhibit clean object deletion.
        """
        # deletion without explicit garbage collection
        gc.collect()
        rel = sumpf.modules.RelabelSignal()
        rel.SetInput(sumpf.Signal())
        del rel
        self.assertEqual(gc.collect(), 0)
        # sumpf.collect_garbage
        sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
        sumpf.connect(self.obj2.GetText, self.obj1.SetText)
        sumpf.disconnect_all(self.obj1)
        gc.collect()
        current_instance_count = ExampleClass.instance_count
        sumpf.destroy_connectors(self.obj1)
        del self.obj1
        gc.collect()
        if ExampleClass.instance_count != current_instance_count - 1:
            for o in gc.garbage:
                if isinstance(o, ExampleClass):
                    collected = sumpf.collect_garbage()
                    self.assertIsInstance(collected, int)  # sumpf.collect_garbage shall return the integer number of collected items
                    self.assertEqual(gc.garbage, [])       # garbage collection should have removed all garbage
                    return
            self.fail("The object has neither been deleted, nor has it been marked as garbage")

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_example(self):
        """
        Test an example signal processing chain that has not worked in a previous,
        buggy version of SuMPF.
        """
        properties = sumpf.modules.ChannelDataProperties(samplingrate=48000)
        generator = sumpf.modules.SweepGenerator()
        sumpf.connect(properties.GetSamplingRate, generator.SetSamplingRate)
        fade_sweep = sumpf.modules.WindowGenerator()
        sumpf.connect(properties.GetSamplingRate, fade_sweep.SetSamplingRate)
        apply_fade = sumpf.modules.MultiplySignals()
        sumpf.connect(generator.GetSignal, apply_fade.SetInput1)
        sumpf.connect(fade_sweep.GetSignal, apply_fade.SetInput2)
        amplify = sumpf.modules.AmplifySignal(factor=0.9)
        sumpf.connect(apply_fade.GetOutput, amplify.SetInput)
        propertiesX = sumpf.modules.ChannelDataProperties(samplingrate=44100)
        sumpf.connect(propertiesX.GetSamplingRate, properties.SetSamplingRate)

