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


import threading
import unittest
import wx
import sumpf

class TestQuestionnaire(sumpf.gui.Window):
    """
    This class is for showing a GUI-Element that shall be tested in a window and
    asking the user short yes-or-no-questions about the displayed element.
    This is a way of formalized testing of GUI elements that are otherwise hard
    to test.
    The questionnaire window does not require the element under test for its
    initialization. This way, the window can be created first and then be passed
    to the element as a parent. The element under test must then be added to the
    window by using the SetMainElement method.

    A common way to use this in a unit test function would look like this:

    questionnaire = TestQuestionnaire()                                     # initialize the questionnaire object
    tested_gui_element = MyFancyGUIElement(parent=questionnaire)            # initialize the element under test
    questionnaire.SetMainElement(tested_gui_element)                        # add the element under test to the questionnaire
    questionnaire.Show()                                                    # show the window
    try:                                                                    # this try-finally-block makes sure that the window is closed even when the unit test fails
        questionnaire.AssertYes("Does it work?", testcase)                  # ask a question to the user. "testcase" is a unittest.TestCase instance that shall raise an AssertionError, when the question is answered with no.
        tested_gui_element.ChangeSomething()                                # modify the element under test
        questionnaire.AssertNo("Does it still look the same?", testcase)    # ask another question, to which the expected answer is "no"
    finally:
        questionnaire.Close()                                               # close the window
    """
    def __init__(self, title="Questionnaire", size=(800, 600)):
        """
        All parameters are optional.
        @param title: the text in the title bar of the questionnaire window
        @param size: a tuple (width, height) that defines the size of the window
        """
        # GUI initialization
        sumpf.gui.Window.__init__(self, parent=None, title=title, size=size)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)
        self.__mainelement = None
        questionbox = wx.StaticBox(parent=self, label="")
        self.__questionsizer = wx.StaticBoxSizer(box=questionbox, orient=wx.VERTICAL)
        self.__questiontext = wx.StaticText(parent=self, label="", style=wx.ST_NO_AUTORESIZE)
        self.__questionsizer.Add(self.__questiontext, 0, wx.EXPAND)
        self.__questionsizer.AddStretchSpacer()
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__questionsizer.Add(buttonsizer, 0, wx.EXPAND)
        buttonsizer.AddStretchSpacer()
        self.__yesbutton = wx.Button(parent=self, label="yes")
        self.__yesbutton.Bind(wx.EVT_BUTTON, self.__OnYes)
        buttonsizer.Add(self.__yesbutton)
        self.__nobutton = wx.Button(parent=self, label="no")
        self.__nobutton.Bind(wx.EVT_BUTTON, self.__OnNo)
        buttonsizer.Add(self.__nobutton)
        # state variables
        self.__active = False
        self.__lock = threading.Event()
        self.__answer = None
        # other stuff
        self.AddObserverOnClose(self.__OnClose)
        self.__DisableQuestion()


    def Close(self):
        """
        Tries to avoid a deadlock when the questionnaire is closed. Sadly, this
        does not work.
        """
        if self.__active:
            sumpf.gui.Window.Close(self)

    def SetMainElement(self, element):
        """
        Sets the main GUI element. This should contain the GUI element that shall
        be tested.
        @param element: a wx object that can be displayed in the window
        """
        self.__mainelement = element

    def Show(self):
        """
        Shows the window in a non-blocking manner.
        """
        self.__active = True
        if self.__mainelement is None:
            self.__sizer.AddStretchSpacer()
        else:
            self.__sizer.Add(self.__mainelement, 1, wx.EXPAND)
        self.__sizer.Add(self.__questionsizer, 0, wx.EXPAND)
        self.Layout()
        sumpf.gui.Window.Show(self)

    def Ask(self, question):
        """
        Asks the user a question, blocks until she/he has answered and returns
        the answer.
        @param question: the text of the question
        @retval : True if the user has answered "Yes", False if the user has answered "No", and None if the window has been closed
        """
        if self.__active:
            self.__questiontext.SetLabel(question)
            self.__questiontext.Wrap(self.GetSize()[0])
            self.__EnableQuestion()
            self.Layout()
            self.__lock.wait()
            self.__lock.clear()
            return self.__answer
        else:
            return None

    def AssertYes(self, question, testcase):
        """
        Asks the user a question and passes the answer to the given testcase's
        assertTrue method. This method requires the user to answer "yes" to the
        question in order to pass the test. See the AssertNo method if the expected
        answer to the question is "no".
        The current test will be skipped, if the user closes the window instead
        of answering the question.
        @param question: the text of the question
        @param testcase: the TestCase instance whose assertTrue method shall be used
        """
        answer = self.Ask(question)
        if answer is None:
            unittest.skip("The questionnaire has been closed.")
        else:
            testcase.assertTrue(answer)

    def AssertNo(self, question, testcase):
        """
        Asks the user a question and passes the answer to the given testcase's
        assertFalse method. This method requires the user to answer "no" to the
        question in order to pass the test. See the AssertYes method if the expected
        answer to the question is "yes".
        The current test will be skipped, if the user closes the window instead
        of answering the question.
        @param question: the text of the question
        @param testcase: the TestCase instance whose assertFalse method shall be used
        """
        answer = self.Ask(question)
        if answer is None:
            unittest.skip("The questionnaire has been closed.")
        else:
            testcase.assertFalse(answer)

    def __OnYes(self, event):
        """
        Event handler for clicks on the yes button
        """
        self.__answer = True
        self.__DisableQuestion()
        self.__lock.set()

    def __OnNo(self, event):
        """
        Event handler for clicks on the no button
        """
        self.__answer = False
        self.__DisableQuestion()
        self.__lock.set()

    def __EnableQuestion(self):
        """
        Enables the GUI elements for the question.
        That is the question text and the two answer buttons.
        """
        self.__questiontext.Enable()
        self.__yesbutton.Enable()
        self.__nobutton.Enable()

    def __DisableQuestion(self):
        """
        Disables the GUI elements for the question.
        That is the question text and the two answer buttons.
        """
        self.__questiontext.Disable()
        self.__yesbutton.Disable()
        self.__nobutton.Disable()

    def __OnClose(self):
        """
        Is executed when the window is closed.
        This releases the lock for unanswered questions and prevents future locking.
        """
        self.__active = False
        self.__answer = None
        self.__lock.set()

