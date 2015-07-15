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



class SetMultipleValuesTestClass(object):
    def __init__(self, testcase):
        self.testcase = testcase
        self.progress_indicator = None
        self.state = 0
        self.value1 = None
        self.value2 = None
        self.value3 = 0
        self.value4 = sumpf.helper.MultiInputData()
        self.data_ids = []
        self.do_assertions = False

    def Start(self):
        self.do_assertions = True

    def SetProgressIndicator(self, progress_indicator):
        self.progress_indicator = progress_indicator

    @sumpf.Input(float, ("GetValue1", "GetState"))
    def SetValue1(self, value):
        self.testcase.assertEqual(self.state, 0)
        if self.progress_indicator is not None:
            progress = self.progress_indicator.GetProgressAsTuple()
            self.testcase.assertEqual(progress[0], 5)
            self.testcase.assertEqual(progress[1], self.state)
        self.state += 1
        self.value1 = value

    @sumpf.Input(str, ("GetValue1", "GetState"))
    def SetValue2(self, value):
        self.testcase.assertEqual(self.state, 1)
        if self.progress_indicator is not None:
            progress = self.progress_indicator.GetProgressAsTuple()
            self.testcase.assertEqual(progress[0], 5)
            self.testcase.assertEqual(progress[1], self.state)
        self.testcase.assertLess(self.state, 3)
        self.state += 1
        self.value2 = value

    @sumpf.Trigger(("GetValue1", "GetState"))
    def TriggerValue3(self):
        self.testcase.assertEqual(self.state, 2)
        if self.progress_indicator is not None:
            progress = self.progress_indicator.GetProgressAsTuple()
            self.testcase.assertEqual(progress[0], 5)
            self.testcase.assertEqual(progress[1], self.state)
        self.state += 1
        self.value3 += 1

    @sumpf.MultiInput(int, remove_method="RemoveValue4", observers=("GetValue4", "GetState"), replace_method="ReplaceValue4")
    def AddValue4(self, value):
        self.testcase.assertEqual(self.state, 3 + len(self.value4.GetData()))
        data_id = self.value4.Add(value)
        self.data_ids.append(data_id)
        self.state += 1
        return data_id

    def RemoveValue4(self, data_id):
        self.data_ids.remove(data_id)
        self.value4.Remove(data_id)

    def ReplaceValue4(self, data_id, value):
        self.value4.Replace(data_id, value)

    @sumpf.Output(int)
    def GetState(self):
        if self.do_assertions:
            self.testcase.assertNotIn(len(self.value4.GetData()), [1, 2])
            self.testcase.assertEqual(self.state, 3 + len(self.value4.GetData()))
        return self.state

    @sumpf.Output(float)
    def GetValue1(self):
        return self.value1

    @sumpf.Output(str)
    def GetValue2(self):
        return self.value2

    @sumpf.Output(int)
    def GetValue3(self):
        return self.value3

    @sumpf.Output(int)
    def GetValue4(self):
        return self.value4



class ProgressTester(object):
    def __init__(self, progress, testcase, count_inputs=True, count_nonobserved_inputs=False, count_outputs=True):
        self.progress = progress
        self.testcase = testcase
        self.progress_indicator = None
        self.count_inputs = count_inputs
        self.count_nonobserved_inputs = count_nonobserved_inputs
        self.count_outputs = count_outputs

    def __Test(self):
        if self.progress[0] >= self.progress[1]:
            self.testcase.assertEqual(self.progress_indicator.GetProgressAsTuple(), self.progress)
            self.testcase.assertAlmostEqual(self.progress_indicator.GetProgressAsFloat(), float(self.progress[1]) / float(self.progress[0]))
            self.testcase.assertEqual(self.progress_indicator.GetProgressAsPercentage(), int(round(100.0 * float(self.progress[1]) / float(self.progress[0]))))

    def SetProgressIndicator(self, indicator):
        self.progress_indicator = indicator

    def SetProgress(self, progress):
        self.progress = progress

    @sumpf.Input(int, ["CachingOutput", "NonCachingOutput"])
    def Input(self, value):
        if self.progress_indicator is not None:
            self.__Test()
            if self.count_inputs:
                self.progress = (self.progress[0], self.progress[1] + 1, self.progress[2])

    @sumpf.Input(int)
    def InputNoObserver(self, value):
        if self.progress_indicator is not None:
            self.__Test()
            if self.count_inputs or self.count_nonobserved_inputs:
                self.progress = (self.progress[0], self.progress[1] + 1, self.progress[2])

    @sumpf.Trigger(["CachingOutput", "NonCachingOutput"])
    def Trigger(self, value=None):
        if self.progress_indicator is not None:
            self.__Test()
            if self.count_inputs:
                self.progress = (self.progress[0], self.progress[1] + 1, self.progress[2])

    @sumpf.MultiInput(int, "Remove", ["CachingOutput", "NonCachingOutput"])
    def MultiInput(self, value):
        if self.progress_indicator is not None:
            self.__Test()
            if self.count_inputs:
                self.progress = (self.progress[0], self.progress[1] + 1, self.progress[2])
        return 1

    def Remove(self, data_id):
        if self.progress_indicator is not None:
            self.__Test()

    @sumpf.Output(int, caching=True)
    def CachingOutput(self):
        if self.progress_indicator is not None:
            self.__Test()
            if self.count_outputs:
                self.progress = (self.progress[0], self.progress[1] + 1, self.progress[2])

    @sumpf.Output(int, caching=False)
    def NonCachingOutput(self):
        if self.progress_indicator is not None:
            self.__Test()
            if self.count_outputs:
                self.progress = (self.progress[0], self.progress[1] + 1, self.progress[2])

