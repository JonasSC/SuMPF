# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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

from .exampleclass import ExampleClass


class TestConnectors(unittest.TestCase):
	"""
	A TestCase for the connections and the related functions.
	"""
	def setUp(self):
		self.obj1 = ExampleClass()
		self.obj2 = ExampleClass()

	def test_setter_and_getter(self):
		"""
		Tests if the getter and setter methods work as expected.
		"""
		self.obj1.SetValue(1)
		self.assertEqual(self.obj1.GetValue(), 1)
		self.assertTrue(isinstance(self.obj1.GetValue(), int))
		self.obj1.SetValueNoUpdate(2)
		self.assertEqual(self.obj1.GetValue(), 2)

	def test_make_valid_connections(self):
		"""
		Makes and brakes some valid connections and tests if the values are passed correctly through the connections.
		"""
		self.obj1.SetValue(1)
		self.obj2.SetValue(2)
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
		self.assertEqual(self.obj2.GetValue(), 1)				# by making the connection, the value should have been passed automatically
		self.obj1.SetValue(3)
		self.assertEqual(self.obj2.GetValue(), 3)				# the value should have been passed through the connection automatically
		sumpf.disconnect(self.obj1.GetValue, self.obj2.SetValue)
		self.obj1.SetValue(4)
		self.assertEqual(self.obj2.GetValue(), 3)				# after disconnection the passing should have stopped
		sumpf.connect(self.obj2.SetValue, self.obj1.GetValue)
		self.obj1.SetValue(5)
		self.assertEqual(self.obj2.GetValue(), 5)				# changing the order of arguments in the connect-call should have worked aswell
		self.obj1.SetValueNoUpdate(6)
		self.assertEqual(self.obj2.GetValue(), 5)				# a decorator with no automatic passing should be possible aswell
		sumpf.disconnect(self.obj2.SetValue, self.obj1.GetValue)
		self.obj1.SetValue(7)
		self.assertEqual(self.obj2.GetValue(), 5)				# changing the order of arguments in the disconnect-call should have worked aswell
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
		sumpf.connect(self.obj1.GetText, self.obj2.SetText)
		self.obj1.ComputeValueAndText(8)
		self.assertEqual(self.obj2.GetValue(), 8)				# ComputeValueAndText should have triggered both connections. GetValue...
		self.assertEqual(self.obj2.GetText(), "8")				# ... and GetText
		self.obj2.triggered = False
		sumpf.connect(self.obj1.GetText, self.obj2.Trigger)		# multiple connections from an output should be possible
		sumpf.connect(self.obj1.GetValue, self.obj2.Trigger)	# multiple connections to a Trigger should be possible
		self.assertFalse(self.obj2.triggered)					# Triggers should not be triggered on connection
		self.obj1.SetValue(9)
		self.assertTrue(self.obj2.triggered)					# Triggers should work as well
		self.obj1.SetText(text="Hallo Welt")					# Keyword arguments should be possible
		sumpf.connect(self.obj1.GetFloat, self.obj2.SetValue2)	# This Input shall be connectable to both floats...
		sumpf.disconnect(self.obj1.GetFloat, self.obj2.SetValue2)
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue2)	# ... and integers.

	def test_multi_input(self):
		"""
		Testing every aspect of a MultiInput is more complex, so it is done in this separate method.
		"""
		id0 = self.obj2.AddItem(0)
		id1 = self.obj2.AddItem(1)
		self.assertEqual(set(self.obj2.GetItems()), set([0, 1]))		# adding items manually should work
		self.obj1.SetValue(2)
		sumpf.connect(self.obj1.GetValue, self.obj2.AddItem)
		self.assertEqual(set(self.obj2.GetItems()), set([0, 1, 2]))		# adding items through connections should work
		self.obj1.SetValue(3)
		self.assertEqual(set(self.obj2.GetItems()), set([0, 1, 3]))		# a connection should only update its own value
		sumpf.connect(self.obj1.GetValue2, self.obj2.AddItem)
		self.assertEqual(set(self.obj2.GetItems()), set([0, 1, 3, 6]))	# multiple connections must be possible
		sumpf.connect(self.obj2.GetItems, self.obj1.Trigger)
		self.obj1.triggered = False
		sumpf.disconnect(self.obj1.GetValue, self.obj2.AddItem)
		self.assertTrue(self.obj1.triggered)							# disconnecting should have triggered the Trigger
		self.assertEqual(set(self.obj2.GetItems()), set([0, 1, 6]))		# disconnecting should remove the item from the list
		self.obj2.RemoveItem(id1)
		self.assertEqual(set(self.obj2.GetItems()), set([0, 6]))		# removing items manually should work as well
		self.obj1.SetValue2(2)
		self.assertEqual(set(self.obj2.GetItems()), set([0, 4]))		# the connection should still work, even after many changes

	def test_make_invalid_connections(self):
		"""
		Tries to make and brake some invalid connections and tests if the mistakes are correctly detected.
		"""
		self.assertRaises(TypeError, sumpf.connect, *(self.obj1.GetText, self.obj2.SetValue2))				# connecting should fail if the types of the connectors are different
		self.assertRaises(TypeError, sumpf.connect, *(self.obj1.GetValue, self.obj2.GetValue))				# connecting should fail if both connectors are outputs
		self.assertRaises(TypeError, sumpf.connect, *(self.obj1.SetValue, self.obj2.SetValue))				# connecting should fail if both connectors are inputs
		self.assertRaises(ValueError, sumpf.connect, *(self.obj1.GetValue, self.obj1.SetValue))				# connecting should fail if the output is connected to an input that updates the output automatically, because that would cause an infinite loop
		sumpf.connect(self.obj1.GetValue, self.obj1.SetValueNoUpdate)
		self.assertRaises(ValueError, sumpf.connect, *(self.obj1.GetValue, self.obj1.SetValueNoUpdate))		# connecting should fail if the connection already exists
		self.assertRaises(ValueError, sumpf.connect, *(self.obj1.GetValue2, self.obj1.SetValueNoUpdate))	# connecting should fail if input is already connected
		self.assertRaises(ValueError, sumpf.disconnect, *(self.obj1.GetValue, self.obj2.SetValue))			# disconnecting should fail if connection does not exist
		sumpf.disconnect(self.obj1.GetValue, self.obj1.SetValueNoUpdate)
		self.assertRaises(ValueError, sumpf.disconnect, *(self.obj1.GetValue, self.obj1.SetValueNoUpdate))	# disconnecting should fail if connection does not exist. Even if it has existed before

	def test_order(self):
		"""
		Tests if connections are updated in the correct order.
		"""
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue2)
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValueNoUpdate)
		self.obj2.order = []
		self.obj1.SetValue(1)
		self.assertEqual(self.obj2.order, ["SetValue", "SetValue2", "SetValueNoUpdate"])	# All items should appear in the correct order
		sumpf.disconnect(self.obj1.GetValue, self.obj2.SetValue2)
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue2)
		self.obj2.order = []
		self.obj1.SetValue(2)
		self.assertEqual(self.obj2.order, ["SetValue", "SetValueNoUpdate", "SetValue2"])	# All items should appear in the correct order

	def test_caching(self):
		"""
		Tests if the caching of values is working.
		"""
		self.assertEqual(type(self.obj1.GetValue2).__name__, "CachingOutputConnector")	# GetValue should always cache
		self.assertEqual(type(self.obj1.GetText).__name__, "NotCachingOutputConnector")	# GetText should never cache
		self.obj1.SetValue2(1)
		self.assertEqual(self.obj1.GetValue2(), 2)										# setter with observers should work normally
		self.obj1.SetValueNoUpdate(2)
		self.assertEqual(self.obj1.GetValue2(), 2)										# setter without observers should not trigger recalculation of cached values

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
		self.assertFalse(self.obj2.triggered)							# disconnect_all should have removed all connections to GetTriggered
		sumpf.connect(self.obj1.GetValue, self.obj2.Trigger)
		sumpf.connect(self.obj1.GetText, self.obj2.Trigger)
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
		sumpf.connect(self.obj1.GetValue2, self.obj2.SetValueNoUpdate)
		sumpf.connect(self.obj2.GetValue, self.obj1.SetValueNoUpdate)
		sumpf.connect(self.obj1.GetValue, self.obj2.AddItem)
		sumpf.connect(self.obj1.GetValue2, self.obj2.AddItem)
		sumpf.disconnect_all(self.obj2)
		self.obj2.SetValue(3)
		self.assertEqual(self.obj1.GetValue(), 2)						# disconnect_all should have removed the connection from obj2.GetValue to obj1.SetValueNoUpdate
		self.obj2.SetText("3")
		self.obj2.triggered = False
		self.obj1.SetValue(2)
		self.obj1.SetText("2")
		self.assertEqual(self.obj2.GetValue(), 3)						# disconnect_all should have removed all connections to obj2
		self.assertEqual(self.obj2.GetText(), "3")						# disconnect_all should have removed all connections to obj2
		self.assertFalse(self.obj2.triggered)							# disconnect_all should have removed all connections to obj2
		self.assertEqual(set(self.obj2.GetItems()), set())				# disconnect_all should have removed all connections to obj2

	def test_deactivate_output(self):
		"""
		Tests if deactivating and reactivating outputs works.
		"""
		self.obj1.SetValue(0)
		self.obj2.SetValue(1)
		sumpf.deactivate_output(self.obj1.GetValue)
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
		self.assertEqual(self.obj2.GetValue(), 1)				# A deactivated output shall not be passed while creating a connection
		sumpf.activate_output(self.obj1.GetValue)
		sumpf.connect(self.obj1.GetText, self.obj2.SetText)
		self.obj1.ComputeValueAndText(2)
		sumpf.deactivate_output(self.obj1)
		sumpf.deactivate_output(self.obj1)						# Deactivating already deactivated outputs should not fail
		self.obj1.ComputeValueAndText(3)
		self.assertEqual(self.obj2.GetValue(), 2)				# No value should be passed through deactivated outputs
		sumpf.activate_output(self.obj1.GetValue)
		self.assertEqual(self.obj2.GetValue(), 3)				# Value should have been passed through reactivated output
		self.assertEqual(self.obj2.GetText(), "2")				# Text output should have remained deactivated
		sumpf.activate_output(self.obj1)
		self.assertEqual(self.obj2.GetText(), "3")				# Text should have been passed while globally enabling outputs

	def test_duplicate_calculation(self):
		"""
		Tests if duplicate calculation in forked chains is avoided.
		"""
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue2)
		sumpf.connect(self.obj2.GetValue, self.obj1.SetValueNoUpdate)
		self.obj2.history = []
		self.obj1.SetValue(1)
		self.assertEqual(self.obj2.history, [1])						# the value should have been calculated only once
		sumpf.deactivate_output(self.obj1)
		self.obj2.history = []
		self.obj1.SetValue(2)
		sumpf.activate_output(self.obj1)
		self.assertEqual(self.obj2.history, [2])						# the value should have been calculated only once after reactivating outputs
		sumpf.disconnect_all(self.obj1)
		sumpf.connect(self.obj1.GetValue, self.obj2.AddItem)
		sumpf.connect(self.obj1.GetValue2, self.obj2.AddItem)
		sumpf.connect(self.obj2.GetItems, self.obj1.TakeList)
		self.obj2.history = []
		self.obj1.SetValue2(3)
		self.assertEqual(self.obj2.history, [[3, 6]])					# the list should have been calculated only once

	def test_docstrings(self):
		"""
		Checks that the docstrings of the decorated methods remain the same
		"""
		self.assertEqual(self.obj1.GetValue.__doc__, "\n\t\tOutput with data_type int\n\t\t")					# The Output decorator should not modify the docstring of the method
		self.assertEqual(self.obj1.SetValue.__doc__, "\n\t\tInput with data_type int and one observer\n\t\t")	# The Input decorator should not modify the docstring of the method
		self.assertEqual(self.obj1.Trigger.__doc__, "\n\t\tA trigger with observer\n\t\t")						# The Trigger decorator should not modify the docstring of the method
		self.assertEqual(self.obj1.AddItem.__doc__, "\n\t\tA MultiInput\n\t\t")									# The MultiInput decorator should not modify the docstring of the method
		self.assertEqual(self.obj1.RemoveItem.__doc__, "\n\t\tEvery MultiInput needs a remove-method\n\t\t")	# The MultiInput decorator should not modify the docstring of its remove method

	def test_object_deletion(self):
		"""
		Checks that Connectors do not inhibit clean object deletion.
		"""
		sumpf.connect(self.obj1.GetValue, self.obj2.SetValue)
		sumpf.connect(self.obj2.GetText, self.obj1.SetText)
		sumpf.disconnect_all(self.obj1)
		gc.collect()
		current_instance_count = ExampleClass.instance_count
		del self.obj1
		gc.collect()
		if ExampleClass.instance_count != current_instance_count - 1:
			for o in gc.garbage:
				if isinstance(o, ExampleClass):
					sumpf.collect_garbage()
					self.assertEqual(gc.garbage, [])					# garbage collection should have removed all garbage
					return
			self.fail("The object has neither been deleted, nor has it been marked as garbage")

