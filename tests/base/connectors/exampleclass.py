# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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

import sumpf


class ExampleClass(object):
	"""
	An example class to test the connections package
	"""

	instance_count = 0

	def __init__(self):
		self.value = 0
		self.text = ""
		self.triggered = False
		self.order = []
		self.items = sumpf.helper.MultiInputData()
		self.history = []
		ExampleClass.instance_count += 1

	def __del__(self):
		ExampleClass.instance_count -= 1

	@sumpf.Output(int, caching=False)
	def GetValue(self):
		"""
		Output with data_type int
		"""
		self.history.append(self.value)
		return self.value

	@sumpf.Output(int, caching=True)
	def GetValue2(self):
		"""
		Output with data_type int and caching
		"""
		return 2 * self.value

	@sumpf.Input(int, "GetValue")
	def SetValue(self, value):
		"""
		Input with data_type int and one observer
		"""
		self.value = value
		self.order.append("SetValue")

	@sumpf.Input((int, float), ["GetValue", "GetValue2"])
	def SetValue2(self, value):
		"""
		Input with data_type int and two observers
		"""
		self.value = value
		self.order.append("SetValue2")

	@sumpf.Input(int)
	def SetValueNoUpdate(self, value):
		"""
		Input with data_type int and no observers
		"""
		self.value = value
		self.order.append("SetValueNoUpdate")

	@sumpf.Output(float)
	def GetFloat(self):
		"""
		An Output with data_type float
		"""
		return 13.37

	@sumpf.Output(str, caching=False)
	def GetText(self):
		"""
		Output with data_type str and without caching
		"""
		return self.text

	@sumpf.Input(str)
	def SetText(self, text):
		"""
		Input with data_type str
		"""
		self.text = text

	@sumpf.Input(int, ["GetValue", "GetText"])
	def ComputeValueAndText(self, value):
		"""
		Input with a list of observers
		"""
		self.value = value
		self.text = str(self.value)

	@sumpf.Trigger()
	def Trigger(self):
		"""
		A trigger with observer
		"""
		self.triggered = True

	@sumpf.Output(list)
	def GetItems(self):
		result = self.items.GetData()
		self.history.append(result)
		return result

	@sumpf.MultiInput(int, "RemoveItem", "GetItems")
	def AddItemNoReplace(self, item):
		"""
		A MultiInput
		"""
		return self.items.Add(item)

	@sumpf.MultiInput(int, "RemoveItem", "GetItems", replace_method="ReplaceItem")
	def AddItemReplace(self, item):
		"""
		A MultiInput
		"""
		return self.items.Add(item)

	@sumpf.MultiInput(int, "RemoveItem", "GetItems", replace_method="ReplaceItem")
	def ThirdMultiInput(self, item):
		"""
		Yet another MultiInput
		"""
		return self.items.Add(item)

	def RemoveItem(self, item_id):
		"""
		Every MultiInput needs a remove-method
		"""
		self.items.Remove(item_id)

	def ReplaceItem(self, item_id, item):
		self.items.Replace(item_id, item)

	@sumpf.Input(list)
	def TakeList(self, itemlist):
		"""
		Something to connect GetItems to.
		"""
		pass

